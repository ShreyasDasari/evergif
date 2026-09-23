/** The evergif skill wordmark. The leading slash marks it as an agent skill command. */
export function Wordmark({ className }: { className?: string }) {
  return (
    <span
      className={`font-mono font-semibold tracking-tight text-foreground ${className ?? ''}`}
    >
      <span className="text-accent">/</span>evergif
    </span>
  )
}
