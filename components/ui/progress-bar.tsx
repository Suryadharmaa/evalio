interface ProgressBarProps {
  label: string;
  value: number;
}

export function ProgressBar({ label, value }: ProgressBarProps) {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div>
      <div className="mb-2 flex justify-between gap-4 text-sm">
        <span className="font-medium">{label}</span>
        <span className="text-muted">{clamped}%</span>
      </div>
      <progress
        aria-label={label}
        className="h-2 w-full overflow-hidden rounded-full bg-[var(--surface-muted)] [&::-moz-progress-bar]:bg-primary [&::-webkit-progress-bar]:bg-[var(--surface-muted)] [&::-webkit-progress-value]:bg-primary"
        max={100}
        value={clamped}
      />
    </div>
  );
}
