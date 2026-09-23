import Link from "next/link";

export function MethodologyLink({ href = "/methodology", label = "See how this is calculated" }: { href?: string; label?: string }) {
  return (
    <Link className="quiet-link inline-flex min-h-11 items-center gap-2" href={href}>
      {label} <span aria-hidden="true">→</span>
    </Link>
  );
}
