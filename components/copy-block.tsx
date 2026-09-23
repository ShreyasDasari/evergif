'use client'

import { useState } from 'react'

function CheckIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M20 6 9 17l-5-5" />
    </svg>
  )
}

function CopyIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <rect x="9" y="9" width="13" height="13" rx="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
  )
}

type CopyBlockProps = {
  /** The raw text copied to the clipboard. */
  code: string
  /** Optional visual override; defaults to `code`. Use for multi-line display. */
  display?: React.ReactNode
  /** Show a shell "$" prompt before a single-line command. */
  prompt?: boolean
  label?: string
  className?: string
}

export function CopyBlock({
  code,
  display,
  prompt = false,
  label = 'Copy command',
  className,
}: CopyBlockProps) {
  const [copied, setCopied] = useState(false)

  async function copy() {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 2000)
    } catch {
      /* clipboard unavailable — no-op */
    }
  }

  return (
    <div
      className={`glass group relative flex items-start gap-3 rounded-xl px-4 py-3.5 ${className ?? ''}`}
    >
      <pre className="min-w-0 flex-1 overflow-x-auto font-mono text-[13px] leading-relaxed text-foreground">
        <code>
          {prompt && (
            <span className="mr-2 select-none text-accent" aria-hidden="true">
              $
            </span>
          )}
          {display ?? code}
        </code>
      </pre>
      <button
        type="button"
        onClick={copy}
        aria-label={copied ? 'Copied' : label}
        className="sticky right-0 top-0 mt-0.5 inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-md border border-white/10 bg-white/5 text-muted transition-colors hover:border-accent hover:text-accent"
      >
        {copied ? (
          <CheckIcon className="h-3.5 w-3.5 text-accent" />
        ) : (
          <CopyIcon className="h-3.5 w-3.5" />
        )}
        <span className="sr-only" role="status" aria-live="polite">
          {copied ? 'Copied to clipboard' : ''}
        </span>
      </button>
    </div>
  )
}
