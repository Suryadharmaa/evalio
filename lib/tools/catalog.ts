export type ToolGroupId = "essays" | "application" | "letters";

export interface ToolCatalogItem {
  description: string;
  group: ToolGroupId;
  href: `/tools/${string}`;
  milestone: `T${number}` | "Engine milestone";
  name: string;
  shortName: string;
  slug: string;
}

export const toolGroups = [
  { id: "essays", label: "Essays" },
  { id: "application", label: "Application" },
  { id: "letters", label: "Letters" },
] as const;

export const toolCatalog: ToolCatalogItem[] = [
  {
    description: "Review measurable structure, clarity, specificity, and reflection signals.",
    group: "essays",
    href: "/tools/essay-evaluator",
    milestone: "T1",
    name: "Essay Evaluator",
    shortName: "EE",
    slug: "essay-evaluator",
  },
  {
    description: "Surface measurable writing patterns without claiming who wrote the text.",
    group: "essays",
    href: "/tools/writing-pattern-checker",
    milestone: "T2",
    name: "Writing Pattern Checker",
    shortName: "WP",
    slug: "writing-pattern-checker",
  },
  {
    description: "Turn experiences, values, and moments into structured story directions.",
    group: "essays",
    href: "/tools/essay-idea-builder",
    milestone: "T3",
    name: "Essay Idea Builder",
    shortName: "IB",
    slug: "essay-idea-builder",
  },
  {
    description: "Evaluate a complete profile for a target college without fake admission odds.",
    group: "application",
    href: "/tools/application-evaluator",
    milestone: "T7",
    name: "Application Evaluator",
    shortName: "AE",
    slug: "application-evaluator",
  },
  {
    description: "Calculate GPA transparently while preserving international grading context.",
    group: "application",
    href: "/tools/gpa",
    milestone: "T4",
    name: "GPA Toolkit",
    shortName: "GP",
    slug: "gpa",
  },
  {
    description: "Review course rigor against the opportunities available at your school.",
    group: "application",
    href: "/tools/coursework-evaluator",
    milestone: "T5",
    name: "Coursework Evaluator",
    shortName: "CE",
    slug: "coursework-evaluator",
  },
  {
    description: "Evaluate impact, initiative, leadership, commitment, and distinction.",
    group: "application",
    href: "/tools/activity-evaluator",
    milestone: "Engine milestone",
    name: "Activity Evaluator",
    shortName: "AT",
    slug: "activity-evaluator",
  },
  {
    description: "Find and track source-backed scholarships, including international eligibility.",
    group: "application",
    href: "/tools/scholarships",
    milestone: "T10",
    name: "Scholarship Tracker",
    shortName: "ST",
    slug: "scholarships",
  },
  {
    description: "Build a specific recommendation-letter framework from structured evidence.",
    group: "letters",
    href: "/tools/lor-builder",
    milestone: "T8",
    name: "LOR Builder",
    shortName: "LB",
    slug: "lor-builder",
  },
  {
    description: "Check specificity, examples, generic praise, and comparative language.",
    group: "letters",
    href: "/tools/lor-evaluator",
    milestone: "T9",
    name: "LOR Evaluator",
    shortName: "LE",
    slug: "lor-evaluator",
  },
];

export function findTool(slug: string) {
  return toolCatalog.find((tool) => tool.slug === slug);
}

export function toolsInGroup(group: ToolGroupId) {
  return toolCatalog.filter((tool) => tool.group === group);
}
