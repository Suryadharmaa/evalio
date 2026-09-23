/** Presentation only: preserve missing values and research qualifiers from the API. */
export const UNVERIFIED = "Not yet verified";

const LABELS: Record<string, string> = {
  REQUIRED: "Required",
  OPTIONAL: "Test optional",
  FLEXIBLE: "Test flexible",
  BLIND: "Test blind",
  NOT_ACCEPTED: "Not accepted",
  PROGRAM_DEPENDENT: "Program dependent",
  OPTIONAL_FOR_INTL_OUTSIDE_US: "Optional for international graduates outside the US",
  OPTIONAL_WITH_PROGRAM_EXCEPTIONS: "Optional with program exceptions",
  NEED_BLIND: "Need blind",
  NEED_AWARE: "Need aware",
  NEED_AWARE_OR_SELECTIVE: "Need aware or selective",
  NO_NEED_BASED_AID: "No need-based aid",
  NO_NEED_BASED_AID_OR_VERY_LIMITED: "No or very limited need-based aid",
  LIMITED_NEED_BASED: "Limited need-based aid",
  MERIT_FOCUSED_LIMITED: "Merit-focused / limited",
  PRIVATE_NONPROFIT: "Private nonprofit",
  PRIVATE_FOR_PROFIT: "Private for-profit",
  PUBLIC: "Public",
  COMMON_APP: "Common App",
  COALITION: "Coalition",
  INSTITUTIONAL: "Institutional application",
  UC_APPLICATION: "UC application",
  CAL_STATE_APPLY: "Cal State Apply",
  APPLYTEXAS: "ApplyTexas",
  SUNY: "SUNY",
};

export function collegeLabel(value: string | null | undefined): string {
  if (!value?.trim() || value === "UNKNOWN") return UNVERIFIED;
  return LABELS[value] ?? value.replaceAll("_", " ").toLowerCase().replace(/^./, (letter) => letter.toUpperCase());
}

export function collegeNumber(value: string | number | null | undefined): string {
  if (value == null || value === "" || !Number.isFinite(Number(value))) return UNVERIFIED;
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(Number(value));
}

export function collegeMoney(value: string | number | null | undefined, currency = "USD"): string {
  if (value == null || value === "" || !Number.isFinite(Number(value))) return UNVERIFIED;
  try {
    return new Intl.NumberFormat("en-US", { style: "currency", currency, maximumFractionDigits: 0 }).format(Number(value));
  } catch {
    return `${collegeNumber(value)} ${currency}`;
  }
}

export function collegeBoolean(value: boolean | null | undefined): string {
  return value == null ? UNVERIFIED : value ? "Yes" : "No";
}

export function collegeDate(value: string | null | undefined): string {
  if (!value || Number.isNaN(Date.parse(value))) return UNVERIFIED;
  return new Intl.DateTimeFormat("en-US", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" }).format(new Date(value));
}
