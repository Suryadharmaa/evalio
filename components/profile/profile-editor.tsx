"use client";

import { useEffect, useState } from "react";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox, Input, Select } from "@/components/ui/field";
import { apiError, authenticatedFetch } from "@/lib/api/client";

interface Profile {
  id: string;
  profile_name: string;
  applicant_type: string;
  country_code: string | null;
  graduation_year: number | null;
  curriculum_type: string | null;
  grading_scale_name: string | null;
  grading_scale_min: string | null;
  grading_scale_max: string | null;
  intended_major: string | null;
  school_name: string | null;
  class_size: number | null;
  class_rank: number | null;
  max_family_contribution: string | null;
  budget_currency: string | null;
  requires_need_based_aid: boolean | null;
}

function numericInputValue(value: string | null): string {
  if (!value) return "";
  const parsed = Number(value);
  return Number.isFinite(parsed) ? String(parsed) : value;
}

function formatCurrency(value: string, currency: string): string | null {
  const amount = Number(value);
  const code = currency.trim().toUpperCase();
  if (!Number.isFinite(amount) || !/^[A-Z]{3}$/.test(code)) return null;
  try {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: code,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  } catch {
    return null;
  }
}

export function ProfileEditor() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [familyContribution, setFamilyContribution] = useState("");
  const [budgetCurrency, setBudgetCurrency] = useState("USD");

  useEffect(() => {
    authenticatedFetch("/api/v1/profiles")
      .then(async (response) => {
        if (!response.ok) throw new Error(await apiError(response));
        const selected = ((await response.json()) as { data: Profile[] }).data[0] ?? null;
        setProfile(selected);
        setFamilyContribution(numericInputValue(selected?.max_family_contribution ?? null));
        setBudgetCurrency(selected?.budget_currency ?? "USD");
      })
      .catch((reason: unknown) => setMessage(reason instanceof Error ? reason.message : "Unable to load profile."))
      .finally(() => setLoaded(true));
  }, []);

  async function save(formData: FormData) {
    setBusy(true); setMessage(null);
    const optionalNumber = (name: string) => { const value = String(formData.get(name) ?? "").trim(); return value ? Number(value) : null; };
    const optionalText = (name: string) => String(formData.get(name) ?? "").trim() || null;
    const body = {
      profile_name: String(formData.get("profile_name") ?? "").trim(),
      applicant_type: formData.get("applicant_type"),
      country_code: optionalText("country_code")?.toUpperCase() ?? null,
      graduation_year: optionalNumber("graduation_year"),
      curriculum_type: optionalText("curriculum_type"),
      grading_scale_name: optionalText("grading_scale_name"),
      grading_scale_min: optionalNumber("grading_scale_min"),
      grading_scale_max: optionalNumber("grading_scale_max"),
      intended_major: optionalText("intended_major"),
      school_name: optionalText("school_name"),
      class_size: optionalNumber("class_size"),
      class_rank: optionalNumber("class_rank"),
      max_family_contribution: optionalNumber("max_family_contribution"),
      budget_currency: optionalText("budget_currency")?.toUpperCase() ?? null,
      requires_need_based_aid: formData.get("requires_need_based_aid") === "on",
    };
    try {
      const response = await authenticatedFetch(profile ? `/api/v1/profiles/${profile.id}` : "/api/v1/profiles", { method: profile ? "PATCH" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      if (!response.ok) throw new Error(await apiError(response));
      setProfile(((await response.json()) as { data: Profile }).data);
      setMessage(profile ? "Profile updated." : "Profile created.");
    } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Unable to save profile."); }
    finally { setBusy(false); }
  }

  if (!loaded) return <p className="mt-8 text-muted">Loading profile…</p>;
  const formattedContribution = formatCurrency(familyContribution, budgetCurrency);
  return <Card className="mt-8 p-6 sm:p-8"><form action={save} className="grid gap-6" key={profile?.id ?? "new"}><h2 className="text-xl font-bold">{profile ? "Update profile" : "Create profile"}</h2><div className="grid gap-6 sm:grid-cols-2">
    <Input id="profile-name" label="Profile name" name="profile_name" placeholder="2027 US Applications" defaultValue={profile?.profile_name ?? ""} required />
    <Select id="applicant-type" label="Applicant type" name="applicant_type" defaultValue={profile?.applicant_type ?? "UNKNOWN"}><option value="UNKNOWN">Select applicant type</option><option value="DOMESTIC">Domestic</option><option value="INTERNATIONAL">International</option></Select>
    <Input id="country-code" label="Country code" name="country_code" placeholder="ID" minLength={2} maxLength={2} defaultValue={profile?.country_code ?? ""} />
    <Input id="graduation-year" label="Graduation year" name="graduation_year" type="number" min={2020} max={2100} defaultValue={profile?.graduation_year ?? ""} />
    <Input id="curriculum" label="Curriculum" name="curriculum_type" placeholder="Kurikulum Merdeka, IB, A-Level…" defaultValue={profile?.curriculum_type ?? ""} />
    <Input id="major" label="Intended major" name="intended_major" placeholder="Finance" defaultValue={profile?.intended_major ?? ""} />
    <Input id="school" label="School name" name="school_name" defaultValue={profile?.school_name ?? ""} />
    <Input id="class-size" label="Class size (optional)" name="class_size" type="number" min={1} defaultValue={profile?.class_size ?? ""} />
    <Input id="class-rank" label="Class rank (optional)" name="class_rank" type="number" min={1} defaultValue={profile?.class_rank ?? ""} />
    <Input id="scale-name" label="Grading scale" name="grading_scale_name" placeholder="0–100" defaultValue={profile?.grading_scale_name ?? ""} />
    <Input id="scale-min" label="Scale minimum" name="grading_scale_min" type="number" step="0.01" defaultValue={numericInputValue(profile?.grading_scale_min ?? null)} />
    <Input id="scale-max" label="Scale maximum" name="grading_scale_max" type="number" step="0.01" defaultValue={numericInputValue(profile?.grading_scale_max ?? null)} />
    <Input id="family-contribution" label="Maximum annual family contribution" name="max_family_contribution" type="number" min={0} step="0.01" value={familyContribution} onChange={(event) => setFamilyContribution(event.target.value)} description={formattedContribution ? `Formatted amount: ${formattedContribution}` : "Enter an amount and a three-letter currency code."} />
    <Input id="budget-currency" label="Budget currency" name="budget_currency" minLength={3} maxLength={3} placeholder="USD" value={budgetCurrency} onChange={(event) => setBudgetCurrency(event.target.value.toUpperCase())} />
  </div><Checkbox id="needs-aid" label="I expect to require need-based financial aid" name="requires_need_based_aid" defaultChecked={profile?.requires_need_based_aid ?? false} />{message ? <Alert title="Profile status">{message}</Alert> : null}<div className="flex justify-end"><Button type="submit" disabled={busy}>{busy ? "Saving…" : profile ? "Update profile" : "Create profile"}</Button></div></form></Card>;
}
