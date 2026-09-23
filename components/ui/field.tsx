import type { InputHTMLAttributes, SelectHTMLAttributes, TextareaHTMLAttributes } from "react";

import { cx } from "@/lib/utils/cx";

interface FieldFrameProps {
  children: React.ReactNode;
  description?: string;
  error?: string;
  id: string;
  label: string;
}

function FieldFrame({ children, description, error, id, label }: FieldFrameProps) {
  return (
    <div className="grid gap-2">
      <label className="text-sm font-bold" htmlFor={id}>{label}</label>
      {children}
      {description && !error ? <p className="text-sm leading-5 text-muted" id={`${id}-description`}>{description}</p> : null}
      {error ? <p className="text-sm font-medium text-[var(--danger)]" id={`${id}-error`}>{error}</p> : null}
    </div>
  );
}

const control = "min-h-11 w-full rounded-lg border border-border bg-white px-4 py-2.5 text-foreground shadow-sm transition-[border-color,box-shadow] duration-200 placeholder:text-muted/70 hover:border-primary/45 focus:border-primary focus:shadow-[0_0_0_3px_rgb(103_87_245/10%)] disabled:cursor-not-allowed disabled:bg-[var(--surface-muted)] disabled:opacity-70";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  description?: string;
  error?: string;
  id: string;
  label: string;
}

export function Input({ className, description, error, id, label, ...props }: InputProps) {
  const describedBy = error ? `${id}-error` : description ? `${id}-description` : undefined;
  return (
    <FieldFrame description={description} error={error} id={id} label={label}>
      <input aria-describedby={describedBy} aria-invalid={Boolean(error)} className={cx(control, error && "border-[var(--danger)]", className)} id={id} {...props} />
    </FieldFrame>
  );
}

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  description?: string;
  error?: string;
  id: string;
  label: string;
}

export function Textarea({ className, description, error, id, label, ...props }: TextareaProps) {
  const describedBy = error ? `${id}-error` : description ? `${id}-description` : undefined;
  return (
    <FieldFrame description={description} error={error} id={id} label={label}>
      <textarea aria-describedby={describedBy} aria-invalid={Boolean(error)} className={cx(control, "min-h-32 resize-y", error && "border-[var(--danger)]", className)} id={id} {...props} />
    </FieldFrame>
  );
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  description?: string;
  error?: string;
  id: string;
  label: string;
}

export function Select({ children, className, description, error, id, label, ...props }: SelectProps) {
  const describedBy = error ? `${id}-error` : description ? `${id}-description` : undefined;
  return (
    <FieldFrame description={description} error={error} id={id} label={label}>
      <select aria-describedby={describedBy} aria-invalid={Boolean(error)} className={cx(control, error && "border-[var(--danger)]", className)} id={id} {...props}>{children}</select>
    </FieldFrame>
  );
}

interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "type"> {
  description?: string;
  id: string;
  label: string;
}

export function Checkbox({ description, id, label, ...props }: CheckboxProps) {
  return (
    <div className="flex items-start gap-3">
      <input className="mt-1 size-5 rounded border-border accent-primary" id={id} type="checkbox" {...props} />
      <div>
        <label className="font-semibold" htmlFor={id}>{label}</label>
        {description ? <p className="mt-1 text-sm leading-5 text-muted">{description}</p> : null}
      </div>
    </div>
  );
}
