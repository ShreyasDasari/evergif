import type { ReactNode } from 'react'

function WindowDots() {
  return (
    <div className="flex items-center gap-1.5" aria-hidden="true">
      <span className="h-3 w-3 rounded-full bg-[#ff5f57]/90" />
      <span className="h-3 w-3 rounded-full bg-[#febc2e]/90" />
      <span className="h-3 w-3 rounded-full bg-[#28c840]/90" />
    </div>
  )
}

/** Renders a recorded GIF, or a muted placeholder when no source is given. */
function Media({
  src,
  alt,
  label,
  priority = false,
}: {
  src?: string
  alt?: string
  label: string
  priority?: boolean
}) {
  if (src) {
    return (
      <div className="relative w-full overflow-hidden bg-[#0a0b12]">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={src || '/placeholder.svg'}
          alt={alt ?? label}
          className="block h-auto w-full"
          loading={priority ? 'eager' : 'lazy'}
          decoding="async"
        />
      </div>
    )
  }
  return (
    <div className="relative aspect-video w-full overflow-hidden bg-[#0a0b12]">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,#22203a_0%,#0d1015_55%,#0a0c10_100%)]" />
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="rounded-md border border-white/10 bg-black/40 px-3 py-1.5 font-mono text-xs text-muted backdrop-blur-sm">
          {label}
        </span>
      </div>
    </div>
  )
}

export function TerminalFrame({
  title,
  caption,
  src,
  alt,
  priority = false,
  children,
}: {
  title: string
  caption?: string
  src?: string
  alt?: string
  priority?: boolean
  children?: ReactNode
}) {
  return (
    <figure className="glass overflow-hidden rounded-2xl">
      <div className="flex items-center gap-3 border-b border-white/10 bg-white/[0.04] px-4 py-2.5">
        <WindowDots />
        <span className="mx-auto truncate font-mono text-xs text-muted">
          {title}
        </span>
        <span className="w-[54px]" aria-hidden="true" />
      </div>
      {children ?? <Media src={src} alt={alt} label={title} priority={priority} />}
      {caption && (
        <figcaption className="border-t border-white/10 px-4 py-2.5 text-center text-xs text-faint">
          {caption}
        </figcaption>
      )}
    </figure>
  )
}

export function BrowserFrame({
  url,
  caption,
  src,
  alt,
  priority = false,
  children,
}: {
  url: string
  caption?: string
  src?: string
  alt?: string
  priority?: boolean
  children?: ReactNode
}) {
  return (
    <figure className="glass overflow-hidden rounded-2xl">
      <div className="flex items-center gap-3 border-b border-white/10 bg-white/[0.04] px-4 py-2.5">
        <WindowDots />
        <div className="mx-auto flex w-full max-w-sm items-center gap-2 rounded-md border border-white/10 bg-black/30 px-3 py-1">
          <span
            className="h-2.5 w-2.5 rounded-full border border-white/20"
            aria-hidden="true"
          />
          <span className="truncate font-mono text-xs text-muted">{url}</span>
        </div>
        <span className="w-[54px]" aria-hidden="true" />
      </div>
      {children ?? <Media src={src} alt={alt} label={url} priority={priority} />}
      {caption && (
        <figcaption className="border-t border-white/10 px-4 py-2.5 text-center text-xs text-faint">
          {caption}
        </figcaption>
      )}
    </figure>
  )
}
