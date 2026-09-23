import { Reveal } from '@/components/reveal'
import { SectionHeading } from '@/components/section-heading'

const STEPS = [
  {
    n: '1',
    title: 'Ask your agent',
    body: '“Add a demo gif to my README.” It inspects the project and picks what\u2019s worth showing.',
  },
  {
    n: '2',
    title: 'It records and embeds',
    body: 'A committed vhs tape or Playwright script, an optimized GIF, and an embed block in your README.',
  },
  {
    n: '3',
    title: 'CI keeps it honest',
    body: 'Output-hash freshness re-renders only the demos that actually changed.',
  },
]

export function HowItWorks() {
  return (
    <section id="how" className="border-t border-border">
      <div className="mx-auto max-w-[1100px] px-5 py-16 sm:px-8 sm:py-20">
        <Reveal>
          <SectionHeading eyebrow="How it works" title="Three steps, no ceremony" />
        </Reveal>

        <div className="mt-10 grid gap-px overflow-hidden rounded-xl border border-border bg-border md:grid-cols-3">
          {STEPS.map((step, i) => (
            <Reveal
              as="div"
              key={step.n}
              delay={i * 70}
              className="flex flex-col bg-background p-7"
            >
              <span className="font-mono text-lg font-semibold text-accent">
                {step.n}
              </span>
              <h3 className="mt-4 text-lg font-semibold tracking-tight">
                {step.title}
              </h3>
              <p className="mt-2.5 leading-relaxed text-muted">{step.body}</p>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
