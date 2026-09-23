import { CopyBlock } from '@/components/copy-block'
import { TerminalFrame } from '@/components/frames'
import { Reveal } from '@/components/reveal'
import { GitHubIcon, ArrowIcon } from '@/components/icons'
import { GITHUB_URL, INSTALL_COMMAND } from '@/lib/constants'

export function Hero() {
  return (
    <section id="top" className="relative">
      <div className="relative mx-auto max-w-[1080px] px-5 pb-12 pt-36 sm:px-8 sm:pt-40">
        <Reveal>
          <span className="glass inline-flex items-center gap-2 rounded-full px-3.5 py-1.5 text-xs font-medium text-muted">
            <span className="relative flex h-1.5 w-1.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-60" />
              <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-accent" />
            </span>
            Open-source Agent Skill · installs in one line
          </span>
        </Reveal>

        <Reveal delay={40}>
          <h1 className="mt-7 max-w-3xl text-balance text-4xl font-semibold leading-[1.05] tracking-tight sm:text-5xl md:text-[4.1rem]">
            Your README demo that{' '}
            <span className="bg-gradient-to-r from-accent to-accent-2 bg-clip-text text-transparent">
              never goes stale
            </span>
            .
          </h1>
        </Reveal>

        <Reveal delay={80}>
          <p className="mt-6 max-w-2xl text-pretty text-base leading-relaxed text-muted sm:text-lg">
            Install{' '}
            <span className="font-mono text-foreground">
              <span className="text-accent">/</span>evergif
            </span>{' '}
            in any coding agent. It records a terminal or web demo, embeds it in
            your README, and CI re-renders it only when what it shows actually
            changed.
          </p>
        </Reveal>

        <Reveal delay={120}>
          <div className="mt-9 max-w-2xl">
            <CopyBlock code={INSTALL_COMMAND} prompt />
            <div className="mt-5 flex flex-wrap items-center gap-3">
              <a
                href={GITHUB_URL}
                target="_blank"
                rel="noreferrer noopener"
                className="accent-glow inline-flex items-center gap-2 rounded-xl bg-accent px-4 py-2.5 text-sm font-semibold text-accent-foreground transition-transform hover:-translate-y-0.5"
              >
                <GitHubIcon className="h-4 w-4" />
                Star on GitHub
              </a>
              <a
                href="#see-it-work"
                className="glass-hover inline-flex items-center gap-1.5 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-medium text-foreground"
              >
                See it work
                <ArrowIcon className="h-3.5 w-3.5" />
              </a>
            </div>
          </div>
        </Reveal>
      </div>

      <div className="relative mx-auto max-w-[1080px] px-5 pb-20 sm:px-8">
        <Reveal delay={80}>
          <TerminalFrame
            title="demo/evergif.gif"
            caption="Recorded by /evergif, on /evergif."
            src="/demo-cli.gif"
            alt="Terminal recording produced by evergif, showing a CLI session captured with a blinking prompt."
            priority
          />
        </Reveal>
      </div>
    </section>
  )
}
