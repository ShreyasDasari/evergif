import { CopyBlock } from '@/components/copy-block'
import { Reveal } from '@/components/reveal'
import { GitHubIcon } from '@/components/icons'
import { GITHUB_URL, INSTALL_COMMAND, LICENSE_URL } from '@/lib/constants'

export function FinalCta() {
  return (
    <section className="scroll-mt-24">
      <div className="mx-auto max-w-[1080px] px-5 py-16 sm:px-8 sm:py-24">
        <Reveal>
          <div className="glass-strong relative overflow-hidden rounded-3xl px-6 py-14 sm:px-14 sm:py-16">
            <div
              className="pointer-events-none absolute -top-24 left-1/2 h-64 w-[36rem] -translate-x-1/2 rounded-full opacity-40 blur-3xl"
              style={{
                background:
                  'radial-gradient(circle, var(--color-accent) 0%, transparent 70%)',
              }}
              aria-hidden="true"
            />
            <div className="relative mx-auto max-w-2xl text-center">
              <h2 className="text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
                Record it once. Let CI keep it true.
              </h2>
              <p className="mt-4 text-pretty leading-relaxed text-muted">
                Add{' '}
                <span className="font-mono text-foreground">
                  <span className="text-accent">/</span>evergif
                </span>{' '}
                to your project and never ship a stale demo again.
              </p>
              <div className="mt-8 text-left">
                <CopyBlock code={INSTALL_COMMAND} prompt />
              </div>
              <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
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
                  href={LICENSE_URL}
                  target="_blank"
                  rel="noreferrer noopener"
                  className="glass-hover inline-flex items-center rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-medium text-foreground"
                >
                  MIT License
                </a>
              </div>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  )
}
