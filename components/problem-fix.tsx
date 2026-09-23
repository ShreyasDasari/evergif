import { Reveal } from '@/components/reveal'

export function ProblemFix() {
  return (
    <section className="scroll-mt-24">
      <div className="mx-auto grid max-w-[1080px] gap-4 px-5 py-8 sm:grid-cols-2 sm:px-8">
        <Reveal as="article" className="glass glass-hover rounded-2xl p-8 sm:p-10">
          <p className="font-mono text-xs uppercase tracking-[0.18em] text-faint">
            The problem
          </p>
          <h3 className="mt-3 text-xl font-semibold tracking-tight">
            Demos rot
          </h3>
          <ul className="mt-5 space-y-2.5 text-muted">
            <li className="flex gap-3">
              <span
                className="mt-2 h-px w-4 shrink-0 bg-white/25"
                aria-hidden="true"
              />
              You rename a flag.
            </li>
            <li className="flex gap-3">
              <span
                className="mt-2 h-px w-4 shrink-0 bg-white/25"
                aria-hidden="true"
              />
              You change the output.
            </li>
            <li className="flex gap-3">
              <span
                className="mt-2 h-px w-4 shrink-0 bg-white/25"
                aria-hidden="true"
              />
              You ship a new screen.
            </li>
          </ul>
          <p className="mt-6 text-foreground">The GIF never notices.</p>
        </Reveal>

        <Reveal
          as="article"
          className="glass glass-hover rounded-2xl p-8 sm:p-10"
          delay={80}
        >
          <p className="font-mono text-xs uppercase tracking-[0.18em] text-accent">
            The fix
          </p>
          <h3 className="mt-3 text-xl font-semibold tracking-tight">
            <span className="font-mono">
              <span className="text-accent">/</span>evergif
            </span>{' '}
            notices
          </h3>
          <p className="mt-5 leading-relaxed text-muted">
            CI re-runs the exact commands the demo shows and hashes the output.
          </p>
          <p className="mt-4 leading-relaxed text-muted">
            <span className="text-foreground">Match</span> means nothing
            renders. <span className="text-foreground">Change</span> means a
            fresh GIF lands on your branch.
          </p>
        </Reveal>
      </div>
    </section>
  )
}
