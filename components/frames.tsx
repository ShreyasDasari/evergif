import type { ReactNode } from 'react'

function WindowDots() {
  return (
    <div className="flex items-center gap-1.5" aria-hidden="true">
      <span className="h-3 w-3 rounded-full bg-[#ff5f57]/80" />
      <span className="h-3 w-3 rounded-full bg-[#febc2e]/80" />
      <span className="h-3 w-3 rounded-full bg-[#28c840]/80" />
    </div>
  )
}

/** A muted gradient 16:9 placeholder — real GIF gets swapped in later. */
function GifPlaceholder({ label }: { label: string }) {
  return (
    <div className="relative aspect-video w-full overflow-hidden bg-surface-2">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,#1b2130_0%,#0d1015_55%,#0a0c10_100%)]" />
      <div
        className="absolute inset-0 opacity-[0.04]"
        style={{
          backgroundImage:
            'repeating-linear-gradient(0deg, #fff 0 1px, transparent 1px 3px)',
        }}
      />
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="rounded-md border border-border-strong bg-background/70 px-3 py-1.5 font-mono text-xs text-muted backdrop-blur-sm">
          {label}
        </span>
      </div>
    </div>
  )
}

export function TerminalFrame({
  title,
  caption,
  children,
}: {
  title: string
  caption?: string
  children?: ReactNode
}) {
  return (
    <figure className="overflow-hidden rounded-xl border border-border-strong bg-surface shadow-[0_1px_0_0_rgba(255,255,255,0.03)_inset]">
      <div className="flex items-center gap-3 border-b border-border bg-surface-2 px-4 py-2.5">
        <WindowDots />
        <span className="mx-auto truncate font-mono text-xs text-muted">
          {title}
        </span>
        <span className="w-[54px]" aria-hidden="true" />
      </div>
      {children ?? <GifPlaceholder label={title} />}
      {caption && (
        <figcaption className="border-t border-border px-4 py-2.5 text-center text-xs text-faint">
          {caption}
        </figcaption>
      )}
    </figure>
  )
}

export function BrowserFrame({
  url,
  caption,
  children,
}: {
  url: string
  caption?: string
  children?: ReactNode
}) {
  return (
    <figure className="overflow-hidden rounded-xl border border-border-strong bg-surface">
      <div className="flex items-center gap-3 border-b border-border bg-surface-2 px-4 py-2.5">
        <WindowDots />
        <div className="mx-auto flex w-full max-w-sm items-center gap-2 rounded-md border border-border bg-background px-3 py-1">
          <span
            className="h-2.5 w-2.5 rounded-full border border-border-strong"
            aria-hidden="true"
          />
          <span className="truncate font-mono text-xs text-muted">{url}</span>
        </div>
        <span className="w-[54px]" aria-hidden="true" />
      </div>
      {children ?? <GifPlaceholder label={url} />}
      {caption && (
        <figcaption className="border-t border-border px-4 py-2.5 text-center text-xs text-faint">
          {caption}
        </figcaption>
      )}
    </figure>
  )
}
