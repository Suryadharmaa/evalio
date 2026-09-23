import Link from "next/link";
import type { AnchorHTMLAttributes, ButtonHTMLAttributes } from "react";

import { cx } from "@/lib/utils/cx";

type Variant = "primary" | "secondary" | "danger" | "ghost" | "inverse" | "inverseGhost";

const variants: Record<Variant, string> = {
  primary: "border-primary bg-primary text-white shadow-[0_8px_20px_rgb(103_87_245/18%)] hover:border-[var(--primary-hover)] hover:bg-[var(--primary-hover)] active:translate-y-px",
  secondary: "border-border bg-white text-foreground hover:border-primary/30 hover:bg-[var(--primary-soft)]",
  danger: "border-[var(--danger)] bg-[var(--danger)] text-white hover:brightness-90",
  ghost: "border-transparent bg-transparent text-foreground hover:bg-[var(--surface-muted)]",
  inverse: "border-white bg-white text-[var(--primary-ink)] shadow-none hover:border-white hover:bg-[var(--surface-soft)]",
  inverseGhost: "border-white/30 bg-transparent text-white shadow-none hover:border-white/60 hover:bg-white/10",
};

const base = "evalio-button inline-flex min-h-11 items-center justify-center gap-3 rounded-[10px] border px-5 py-3 text-sm font-bold transition-[background-color,border-color,color,box-shadow,transform] duration-200 hover:-translate-y-px disabled:cursor-not-allowed disabled:hover:translate-y-0";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

export function Button({ className, type = "button", variant = "primary", ...props }: ButtonProps) {
  return <button className={cx(base, variants[variant], className)} type={type} {...props} data-variant={variant} />;
}

interface ButtonLinkProps extends AnchorHTMLAttributes<HTMLAnchorElement> {
  href: string;
  variant?: Variant;
}

export function ButtonLink({ className, href, variant = "primary", ...props }: ButtonLinkProps) {
  return <Link className={cx(base, variants[variant], className)} href={href} {...props} data-variant={variant} />;
}
