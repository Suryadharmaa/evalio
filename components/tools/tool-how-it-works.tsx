interface ToolStep {
  description: string;
  title: string;
}

export function ToolHowItWorks({ steps }: { steps: ToolStep[] }) {
  return (
    <section aria-labelledby="how-it-works-title">
      <p className="eyebrow">Evalio / Process</p>
      <h2 className="section-title mt-4 text-[clamp(2rem,4vw,3rem)]" id="how-it-works-title">How it works</h2>
      <ol className="mt-8 grid gap-6 md:grid-cols-3">
        {steps.map((step, index) => (
          <li className="border-t border-border pt-5" key={step.title}>
            <p className="text-sm font-extrabold text-primary">{String(index + 1).padStart(2, "0")}</p>
            <h3 className="mt-4 text-xl font-semibold">{step.title}</h3>
            <p className="mt-2 leading-7 text-muted">{step.description}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
