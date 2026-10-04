"use client";

import { apiFetch } from "@/lib/api/client";

import { useEffect, useState } from "react";
import { CollegeCard, type CollegeSummary } from "@/components/college/college-card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import styles from "./home.module.css";

export function CollegePreview() {
  const [colleges, setColleges] = useState<CollegeSummary[] | null>(null);
  const [failed, setFailed] = useState(false);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    async function load() {
      try {
        const response = await apiFetch("/api/v1/colleges?country=US&page=1&page_size=3", { signal: controller.signal });
        if (!response.ok) throw new Error("unavailable");
        const body = await response.json() as { data: CollegeSummary[] };
        if (!controller.signal.aborted) setColleges(body.data);
      } catch {
        if (!controller.signal.aborted) setFailed(true);
      }
    }
    void load();
    return () => controller.abort();
  }, [attempt]);
  if (failed) return <div className={styles.dataEmpty} role="status"><div><h3>College data is temporarily unavailable.</h3><p>Your profile has not been changed. Try again to load the college directory.</p></div><Button variant="secondary" onClick={() => { setFailed(false); setColleges(null); setAttempt(attempt + 1); }}>Try again</Button></div>;
  if (colleges === null) return <div className={styles.collegeGrid} role="status" aria-label="Loading college preview">{[0, 1, 2].map((index) => <div className="rounded-xl border border-border p-4" key={index}><Skeleton className="h-36 w-full" /><Skeleton className="mt-5 h-6 w-3/4" /><Skeleton className="mt-3 h-20 w-full" /></div>)}</div>;
  if (!colleges.length) return <div className={styles.dataEmpty}><div><h3>The directory is awaiting verified records.</h3><p>No college records are available yet. Evalio never fills missing data with invented schools.</p></div></div>;
  return <div className={styles.collegeGrid}>{colleges.map((college) => <CollegeCard college={college} key={college.id} />)}</div>;
}
