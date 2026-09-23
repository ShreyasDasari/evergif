import { Reveal } from '@/components/reveal'
import { SectionHeading } from '@/components/section-heading'

const FEATURES = [
  {
    title: 'Terminal and web',
    body: 'vhs for CLIs and TUIs, Playwright for web apps.',
  },
  {
    title: 'Only re-renders what changed',
    body: 'Output hashing, not pixel diffing, so demos don\u2019t churn weekly.',
  },
  {
    title: 'Safe by construction',
    body: 'Refuses destructive, networked, or credential-exposing commands in code, not just in the prompt.',
  },
  {
    title: 'Legible by default',
    body: 'Recorded at 1100px display width, never downscaled, colors given up last.',
  },
  {
    title: 'No local toolchain needed',
    body: 'CI renders tapes for contributors who have nothing installed.',
  },
  {
    title: 'Several demos per README',
    body: 'Each with its own marker block and lock file.',
  },
]

export function FeatureGrid() {
  return (
    <section id="features" className="scroll-mt-24">
      <div className="mx-auto max-w-[1080px] px-5 py-16 sm:px-8 sm:py-24">
        <Reveal>
          <SectionHeading
            eyebrow="Features"
            title="Built like a CLI tool, not a SaaS"
          />
        </Reveal>

        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature, i) => (
            <Reveal
              as="article"
              key={feature.title}
              delay={(i % 3) * 60}
              className="glass glass-hover rounded-2xl p-7"
            >
              <h3 className="text-base font-semibold tracking-tight text-foreground">
                {feature.title}
              </h3>
              <p className="mt-2.5 text-sm leading-relaxed text-muted">
                {feature.body}
              </p>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
