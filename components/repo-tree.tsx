import { Reveal } from '@/components/reveal'
import { SectionHeading } from '@/components/section-heading'

const FILES = [
  { path: 'demo/evergif.tape', note: 'the recording script, committed so renders are reproducible' },
  { path: 'demo/evergif.gif', note: 'under 2 MB where possible, never over 5 MB' },
  { path: 'demo/evergif.lock', note: 'what the demo showed, for the CI freshness check' },
  { path: 'README.md', note: 'an embed between <!-- evergif:start --> / <!-- evergif:end -->' },
]

export function RepoTree() {
  return (
    <section className="border-t border-border">
      <div className="mx-auto max-w-[1100px] px-5 py-16 sm:px-8 sm:py-20">
        <Reveal>
          <SectionHeading
            eyebrow="What lands in your repo"
            title="Four files, all reviewable"
          />
        </Reveal>

        <Reveal delay={60}>
          <div className="mt-8 overflow-hidden rounded-xl border border-border-strong bg-surface">
            <div className="border-b border-border bg-surface-2 px-4 py-2.5 font-mono text-xs text-muted">
              your-project/
            </div>
            <ul className="divide-y divide-border font-mono text-[13px]">
              {FILES.map((file) => (
                <li
                  key={file.path}
                  className="flex flex-col gap-1 px-4 py-3.5 sm:flex-row sm:items-baseline sm:gap-6"
                >
                  <span className="shrink-0 text-foreground sm:w-52">
                    {file.path}
                  </span>
                  <span className="text-faint"># {file.note}</span>
                </li>
              ))}
            </ul>
          </div>
        </Reveal>
      </div>
    </section>
  )
}
