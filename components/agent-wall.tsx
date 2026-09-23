import {
  siClaude,
  siCursor,
  siGithubcopilot,
  siGooglegemini,
  siOpenai,
  siWindsurf,
} from 'simple-icons'
import { Reveal } from '@/components/reveal'
import { SectionHeading } from '@/components/section-heading'

type SimpleIcon = { path: string; title: string }

type Agent =
  | { name: string; icon: SimpleIcon }
  // wordmark fallback — no official SVG in simple-icons yet; drop a real SVG in later.
  | { name: string; wordmark: true }

const AGENTS: Agent[] = [
  { name: 'Claude Code', icon: siClaude },
  { name: 'Gemini CLI', icon: siGooglegemini },
  { name: 'Codex CLI', icon: siOpenai },
  { name: 'GitHub Copilot', icon: siGithubcopilot },
  { name: 'Cursor', icon: siCursor },
  // FALLBACK (wordmark): OpenCode
  { name: 'OpenCode', wordmark: true },
  { name: 'Windsurf', icon: siWindsurf },
  // FALLBACK (wordmark): Cline
  { name: 'Cline', wordmark: true },
  // FALLBACK (wordmark): Goose
  { name: 'Goose', wordmark: true },
  // FALLBACK (wordmark): Amp
  { name: 'Amp', wordmark: true },
  // FALLBACK (wordmark): Antigravity
  { name: 'Antigravity', wordmark: true },
]

function BrandSvg({ icon }: { icon: SimpleIcon }) {
  return (
    <svg
      role="img"
      aria-label={`${icon.title} logo`}
      viewBox="0 0 24 24"
      width={28}
      height={28}
      fill="currentColor"
    >
      <path d={icon.path} />
    </svg>
  )
}

export function AgentWall() {
  return (
    <section className="scroll-mt-24">
      <div className="mx-auto max-w-[1080px] px-5 py-16 sm:px-8 sm:py-24">
        <Reveal>
          <SectionHeading
            eyebrow="Works with your agent"
            title="One skill, every agent"
          />
        </Reveal>

        <Reveal delay={60}>
          <ul className="glass mt-10 grid grid-cols-3 gap-px overflow-hidden rounded-2xl bg-white/[0.06] sm:grid-cols-3 lg:grid-cols-6">
            {AGENTS.map((agent) => (
              <li
                key={agent.name}
                className="group flex aspect-square flex-col items-center justify-center gap-3 bg-transparent px-2 text-center transition-colors hover:bg-white/[0.05]"
              >
                <span className="flex h-8 items-center justify-center text-[#f2f4f7]/70 transition-opacity duration-200 group-hover:text-[#f2f4f7]">
                  {'icon' in agent ? (
                    <BrandSvg icon={agent.icon} />
                  ) : (
                    <span
                      aria-hidden="true"
                      className="rounded-md border border-border-strong px-2.5 py-1 font-mono text-[11px] font-medium text-[#f2f4f7]/70 transition-opacity duration-200 group-hover:text-[#f2f4f7]"
                    >
                      {agent.name}
                    </span>
                  )}
                </span>
                <span className="font-mono text-[11px] text-muted transition-colors group-hover:text-foreground">
                  {agent.name}
                </span>
              </li>
            ))}
          </ul>
        </Reveal>

        <Reveal delay={80}>
          <p className="mt-8 text-sm text-muted">
            One canonical skill, symlinked to every agent&apos;s discovery path.
          </p>
          <p className="mt-2 text-xs text-faint">
            Logos are the property of their respective owners and do not imply
            endorsement.
          </p>
        </Reveal>
      </div>
    </section>
  )
}
