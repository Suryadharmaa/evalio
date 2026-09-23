import Link from "next/link";

interface ToolHeaderProps {
  description: string;
  eyebrow?: string;
  title: string;
}

export function ToolHeader({ description, eyebrow = "Tools", title }: ToolHeaderProps) {
  return (
    <header className="max-w-3xl">
      <Link className="quiet-link inline-flex min-h-11 items-center text-sm" href="/tools">
        <span aria-hidden="true">←</span>&nbsp; Tools
      </Link>
      <p className="eyebrow mt-7">Evalio / {eyebrow}</p>
      <h1 className="display-title mt-4 max-w-4xl text-[clamp(2.75rem,6vw,4.75rem)]">{title}.</h1>
      <p className="mt-6 max-w-2xl text-lg leading-8 text-muted sm:text-xl">{description}</p>
    </header>
  );
}
