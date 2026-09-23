/** Native value attributes keep scores compatible with the strict nonce CSP. */
export function ScoreBar({ value, label }: { value: number; label: string }) {
  return <progress className="evalio-score-bar" aria-label={label} max={100} value={Math.max(0, Math.min(100, value))} />;
}
