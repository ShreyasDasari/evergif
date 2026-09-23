import { CopyBlock } from '@/components/copy-block'
import { Reveal } from '@/components/reveal'
import { GITHUB_URL, INSTALL_COMMAND, LICENSE_URL } from '@/lib/constants'

export function FinalCta() {
  return (
    <section className="border-t border-border">
      <div className="mx-auto max-w-[1100px] px-5 py-20 sm:px-8 sm:py-24">
        <Reveal className="mx-auto max-w-2xl text-center">
          <h2 className="text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
            Record it once. Let CI keep it true.
          </h2>
          <div className="mt-8 text-left">
            <CopyBlock code={INSTALL_COMMAND} prompt />
          </div>
          <div className="mt-6 flex items-center justify-center gap-6 text-sm">
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noreferrer noopener"
              className="text-accent transition-colors hover:text-foreground"
            >
              GitHub
            </a>
            <a
              href={LICENSE_URL}
              target="_blank"
              rel="noreferrer noopener"
              className="text-muted transition-colors hover:text-foreground"
            >
              MIT License
            </a>
          </div>
        </Reveal>
      </div>
    </section>
  )
}
