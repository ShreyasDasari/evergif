import { CopyBlock } from '@/components/copy-block'
import { TerminalFrame } from '@/components/frames'
import { Reveal } from '@/components/reveal'
import { GITHUB_URL, INSTALL_COMMAND } from '@/lib/constants'

function ArrowIcon() {
  return (
    <svg
      className="h-3.5 w-3.5"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M5 12h14M13 6l6 6-6 6" />
    </svg>
  )
}

export function Hero() {
  return (
    <section id="top" className="relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 hero-texture" aria-hidden="true" />
      <div className="pointer-events-none absolute inset-0 hero-scanline" aria-hidden="true" />

      <div className="relative mx-auto max-w-[1100px] px-5 pb-14 pt-20 sm:px-8 sm:pt-28">
        <Reveal>
          <p className="mb-8 font-mono text-sm font-semibold tracking-tight text-foreground">
            evergif
          </p>
        </Reveal>

        <Reveal delay={40}>
          <h1 className="max-w-3xl text-balance text-4xl font-semibold leading-[1.08] tracking-tight sm:text-5xl md:text-6xl">
            Your README demo that never goes stale.
          </h1>
        </Reveal>

        <Reveal delay={80}>
          <p className="mt-6 max-w-2xl text-pretty text-base leading-relaxed text-muted sm:text-lg">
            One line to install in any coding agent. It records a terminal or
            web demo, embeds it in your README, and CI re-renders it only when
            what it shows actually changed.
          </p>
        </Reveal>

        <Reveal delay={120}>
          <div className="mt-9 max-w-2xl">
            <CopyBlock code={INSTALL_COMMAND} prompt />
            <div className="mt-4">
              <a
                href={GITHUB_URL}
                target="_blank"
                rel="noreferrer noopener"
                className="inline-flex items-center gap-1.5 text-sm text-accent transition-colors hover:text-foreground"
              >
                View on GitHub
                <ArrowIcon />
              </a>
            </div>
          </div>
        </Reveal>
      </div>

      <div className="relative mx-auto max-w-[1100px] px-5 pb-20 sm:px-8">
        <Reveal delay={80}>
          <TerminalFrame
            title="demo/evergif.gif"
            caption="Recorded by evergif, on evergif."
          />
        </Reveal>
      </div>
    </section>
  )
}
