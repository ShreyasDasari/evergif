'use client'

import { useId, useRef, useState } from 'react'
import { CopyBlock } from '@/components/copy-block'
import { BrowserFrame, TerminalFrame } from '@/components/frames'
import { SectionHeading } from '@/components/section-heading'
import { Reveal } from '@/components/reveal'

const TABS = [
  { id: 'terminal', label: 'Terminal demo' },
  { id: 'web', label: 'Web app demo' },
  { id: 'fresh', label: 'Staying fresh' },
] as const

type TabId = (typeof TABS)[number]['id']

const README_EMBED = `<!-- evergif:start -->
![Terminal demo of the todo CLI: --help lists the commands, list --open shows three open tasks](demo/evergif.gif)
<!-- evergif:end -->`

const WEB_COMMAND = `evergif --web --url http://localhost:3000 --serve "npm run dev" \\
  --steps "goto /; wait #invoice; pause 800; click text=Create invoice"`

function ChatExchange() {
  return (
    <div className="flex flex-col gap-4">
      <div className="glass rounded-xl p-4">
        <p className="mb-1.5 font-mono text-xs uppercase tracking-[0.14em] text-faint">
          You
        </p>
        <p className="text-sm leading-relaxed text-foreground">
          add a demo gif to my README
        </p>
      </div>
      <div className="glass rounded-xl p-4">
        <p className="mb-1.5 font-mono text-xs uppercase tracking-[0.14em] text-accent">
          <span className="text-accent">/</span>evergif
        </p>
        <p className="text-sm leading-relaxed text-muted">
          Inspected the repo — a Python CLI with 3 commands. Recording{' '}
          <code className="rounded bg-white/10 px-1 py-0.5 font-mono text-[12px] text-foreground">
            --help
          </code>
          ,{' '}
          <code className="rounded bg-white/10 px-1 py-0.5 font-mono text-[12px] text-foreground">
            list --open
          </code>
          , and{' '}
          <code className="rounded bg-white/10 px-1 py-0.5 font-mono text-[12px] text-foreground">
            stats
          </code>
          . Writing{' '}
          <code className="rounded bg-white/10 px-1 py-0.5 font-mono text-[12px] text-foreground">
            demo/evergif.tape
          </code>
          …
        </p>
      </div>
    </div>
  )
}

function TerminalTab() {
  return (
    <div className="flex flex-col gap-6">
      <div className="grid gap-6 lg:grid-cols-2">
        <ChatExchange />
        <TerminalFrame
          title="demo/evergif.gif"
          caption="examples/shcli — recorded and kept current by CI."
          src="/demo-cli.gif"
          alt="Terminal recording of a CLI session captured by evergif."
        />
      </div>
      <div>
        <p className="mb-2.5 font-mono text-xs uppercase tracking-[0.14em] text-faint">
          What it wrote into your README
        </p>
        <CopyBlock
          code={README_EMBED}
          label="Copy README embed"
          display={
            <span className="whitespace-pre">
              {'<!-- evergif:start -->\n'}
              <span className="text-muted">
                {
                  '![Terminal demo of the todo CLI: --help lists the commands, list --open shows three open tasks](demo/evergif.gif)\n'
                }
              </span>
              {'<!-- evergif:end -->'}
            </span>
          }
        />
      </div>
    </div>
  )
}

function WebTab() {
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div className="flex flex-col gap-4">
        <CopyBlock code={WEB_COMMAND} label="Copy command" display={WEB_COMMAND} />
        <p className="text-sm leading-relaxed text-muted">
          <span className="font-mono text-foreground">
            <span className="text-accent">/</span>evergif
          </span>{' '}
          starts your dev server, waits for the port, records the flow with
          Playwright, stops the server, and converts the video to an optimized
          GIF.
        </p>
      </div>
      <BrowserFrame
        url="localhost:3000"
        caption="demo/webapp.gif — the Invoice Maker app, recorded end to end."
        src="/demo-web.gif"
        alt="Browser recording of the Invoice Maker web app captured by evergif."
      />
    </div>
  )
}

function FreshTab() {
  return (
    <div className="flex flex-col gap-6">
      <div className="grid items-stretch gap-3 md:grid-cols-[1fr_auto_1.4fr_auto_1fr]">
        <FlowNode>Push to main</FlowNode>
        <FlowArrow />
        <FlowNode>Re-run the demo&apos;s commands, hash the output</FlowNode>
        <FlowArrow />
        <FlowNode mono>matches demo/evergif.lock?</FlowNode>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="glass rounded-2xl p-6">
          <p className="font-mono text-xs uppercase tracking-[0.14em] text-faint">
            Match
          </p>
          <p className="mt-2.5 leading-relaxed text-muted">
            Nothing renders. Your GIF is still true.
          </p>
        </div>
        <div className="glass rounded-2xl border border-accent/40 p-6 shadow-[0_0_60px_-30px_var(--color-accent)]">
          <p className="font-mono text-xs uppercase tracking-[0.14em] text-accent">
            Changed
          </p>
          <p className="mt-2.5 leading-relaxed text-foreground">
            Re-render, commit the new GIF to your branch.
          </p>
        </div>
      </div>

      <p className="text-sm leading-relaxed text-muted">
        Output hashing, not pixel diffing — terminal recordings jitter by a
        frame, so pixel diffs would churn every week. Command output changes
        only when your CLI does.
      </p>
    </div>
  )
}

function FlowNode({
  children,
  mono = false,
}: {
  children: React.ReactNode
  mono?: boolean
}) {
  return (
    <div
      className={`glass flex items-center justify-center rounded-xl px-4 py-4 text-center text-sm leading-snug text-foreground ${
        mono ? 'font-mono text-[13px]' : ''
      }`}
    >
      {children}
    </div>
  )
}

function FlowArrow() {
  return (
    <div
      className="flex items-center justify-center text-accent/70"
      aria-hidden="true"
    >
      <span className="md:hidden">↓</span>
      <span className="hidden md:inline">→</span>
    </div>
  )
}

export function SeeItWork() {
  const [active, setActive] = useState<TabId>('terminal')
  const baseId = useId()
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([])

  function onKeyDown(e: React.KeyboardEvent, index: number) {
    let next = index
    if (e.key === 'ArrowRight') next = (index + 1) % TABS.length
    else if (e.key === 'ArrowLeft') next = (index - 1 + TABS.length) % TABS.length
    else if (e.key === 'Home') next = 0
    else if (e.key === 'End') next = TABS.length - 1
    else return
    e.preventDefault()
    setActive(TABS[next].id)
    tabRefs.current[next]?.focus()
  }

  return (
    <section id="see-it-work" className="scroll-mt-24">
      <div className="mx-auto max-w-[1080px] px-5 py-16 sm:px-8 sm:py-24">
        <Reveal>
          <SectionHeading eyebrow="See it work" title="Show, don't claim">
            The same skill, three ways: a terminal recording, a web app
            recording, and the CI check that keeps both honest.
          </SectionHeading>
        </Reveal>

        <Reveal delay={60}>
          <div className="mt-9">
            <div
              role="tablist"
              aria-label="See evergif in action"
              className="glass flex w-full gap-1 rounded-2xl p-1.5 sm:w-auto sm:inline-flex"
            >
              {TABS.map((tab, i) => {
                const selected = active === tab.id
                return (
                  <button
                    key={tab.id}
                    ref={(el) => {
                      tabRefs.current[i] = el
                    }}
                    role="tab"
                    id={`${baseId}-tab-${tab.id}`}
                    aria-selected={selected}
                    aria-controls={`${baseId}-panel-${tab.id}`}
                    tabIndex={selected ? 0 : -1}
                    onClick={() => setActive(tab.id)}
                    onKeyDown={(e) => onKeyDown(e, i)}
                    className={`flex-1 whitespace-nowrap rounded-xl px-4 py-2 text-sm font-medium transition-colors sm:flex-none ${
                      selected
                        ? 'bg-white/10 text-foreground shadow-[inset_0_1px_0_0_rgba(255,255,255,0.12)]'
                        : 'text-muted hover:text-foreground'
                    }`}
                  >
                    {tab.label}
                  </button>
                )
              })}
            </div>

            <div className="glass mt-6 rounded-2xl p-5 sm:p-7">
              {TABS.map((tab) => (
                <div
                  key={tab.id}
                  role="tabpanel"
                  id={`${baseId}-panel-${tab.id}`}
                  aria-labelledby={`${baseId}-tab-${tab.id}`}
                  hidden={active !== tab.id}
                >
                  {tab.id === 'terminal' && <TerminalTab />}
                  {tab.id === 'web' && <WebTab />}
                  {tab.id === 'fresh' && <FreshTab />}
                </div>
              ))}
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  )
}
