import { z } from "zod";

export const essayAnalysisFormSchema = z.object({
  essayType: z.enum(["COMMON_APP", "SUPPLEMENTAL", "SCHOLARSHIP", "OTHER"]),
  text: z.string().max(100_000, "Essay text must be 100,000 characters or fewer."),
  hasFile: z.boolean(),
  minWords: z.coerce.number().int().min(0).max(10_000),
  wordLimit: z.coerce.number().int().min(1).max(10_000),
}).superRefine((value, context) => {
  if (!value.hasFile && !value.text.trim()) {
    context.addIssue({ code: "custom", message: "Paste essay text or choose a file.", path: ["text"] });
  }
  if (value.minWords > value.wordLimit) {
    context.addIssue({ code: "custom", message: "Minimum words cannot exceed the word limit.", path: ["minWords"] });
  }
});

export const signInFormSchema = z.object({
  email: z.string().trim().email("Enter a valid email address.").max(320),
  password: z.string().max(128, "Password must be 128 characters or fewer."),
  mode: z.enum(["password", "signup", "magic"]),
}).superRefine((value, context) => {
  if (value.mode !== "magic" && value.password.length < 6) {
    context.addIssue({ code: "custom", message: "Password must contain at least 6 characters.", path: ["password"] });
  }
});

export function firstValidationError(result: z.ZodSafeParseError<unknown>): string {
  return result.error.issues[0]?.message ?? "Check the entered values.";
}
