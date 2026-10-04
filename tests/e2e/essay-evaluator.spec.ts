import { expect, test } from "@playwright/test";

const draft = Array.from({ length: 60 }, (_, index) => `word${index + 1}`).join(" ");
const categories = Object.fromEntries(
  Object.entries({ content: 20, structure: 15, voice: 20, specificity: 15, reflection: 20, writing_quality: 10 })
    .map(([name, max_score]) => [name, { score: Math.floor(max_score / 2), max_score, feedback: "Revise with concrete evidence." }]),
);
const signal = { score: 50, label: "Moderate" };

test("anonymous user receives a hybrid essay review", async ({ page }) => {
  let submitted = "";
  await page.route("**/api/v1/essay-review", async (route) => {
    submitted = JSON.parse(route.request().postData() ?? "{}").essay;
    await route.fulfill({ json: { data: {
      status: "complete", analysis_id: "fixture-review", score: 50, label: "Developing",
      review: { overall_impression: "A clear start with room for detail.", categories, strengths: ["Clear intent"], improvements: ["Add evidence"], priority_action: "Describe one concrete moment." },
      metrics: { word_count: 60, sentence_count: 1, paragraph_count: 1, average_words_per_sentence: 60, sentence_variety: signal, vocabulary_diversity: signal, readability: signal, repetition: { label: "Low", repeated_phrases: [], repeated_openings: [] } },
      meta: { cached: false, ai_calls: 1 },
    } } });
  });
  await page.goto("/tools/essay-evaluator");
  await expect(page.getByRole("heading", { name: "College Essay Evaluator." })).toBeVisible();
  await page.getByLabel("Essay text").fill(draft);
  await expect(page.getByText("60 words")).toBeVisible();
  await page.getByRole("button", { name: "Analyze essay" }).click();
  await expect(page.getByText("Scoring rubric")).toBeVisible();
  await expect(page.getByText("Describe one concrete moment.")).toBeVisible();
  expect(submitted).toBe(draft);
  await page.getByLabel("Essay text").fill(`${draft} revised`);
  await expect(page.getByText("Your draft changed. Analyze it again to update the review.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Run Deep Review" })).toBeDisabled();
});

test("essay evaluator remains usable at 360px", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto("/tools/essay-evaluator");
  await expect(page.getByLabel("Essay text")).toBeVisible();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  expect(overflow).toBe(false);
});

test("provider rate limit pauses repeat analysis without losing writing signals", async ({ page }) => {
  let calls = 0;
  await page.route("**/api/v1/essay-review", async (route) => {
    calls += 1;
    await route.fulfill({ json: { data: {
      status: "partial", message: "Routeway request limit reached. Check the provider's quota and reset time; repeated requests will not help.",
      retry_after_seconds: 3,
      metrics: { word_count: 60, sentence_count: 1, paragraph_count: 1, average_words_per_sentence: 60, sentence_variety: signal, vocabulary_diversity: signal, readability: signal, repetition: { label: "Low", repeated_phrases: [], repeated_openings: [] } },
      meta: { cached: false, ai_calls: 1 },
    } } });
  });
  await page.goto("/tools/essay-evaluator");
  await page.getByLabel("Essay text").fill(draft);
  await page.getByRole("button", { name: "Analyze essay" }).click();
  await expect(page.getByText("Retry available in 3 seconds.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Try AI analysis again" })).toBeDisabled();
  await expect(page.getByRole("button", { name: "Analyze essay" })).toBeDisabled();
  expect(calls).toBe(1);
  await expect(page.getByRole("button", { name: "Try AI analysis again" })).toBeEnabled({ timeout: 5000 });
});
