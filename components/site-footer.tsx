import { GITHUB_URL } from '@/lib/constants'
import { GitHubIcon } from '@/components/icons'
import { Wordmark } from '@/components/wordmark'

export function SiteFooter() {
  return (
    <footer className="border-t border-white/8">
      <div className="mx-auto flex max-w-[1080px] flex-col gap-4 px-5 py-10 text-sm sm:flex-row sm:items-center sm:justify-between sm:px-8">
        <div className="flex flex-col gap-2">
          <Wordmark className="text-sm" />
          <p className="text-faint">
            MIT licensed. Built on vhs by Charm and Playwright by Microsoft.
          </p>
        </div>
        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noreferrer noopener"
          className="glass-hover inline-flex items-center gap-2 self-start rounded-xl border border-white/10 bg-white/5 px-3.5 py-2 text-muted transition-colors hover:text-foreground sm:self-auto"
        >
          <GitHubIcon className="h-4 w-4" />
          GitHub
        </a>
      </div>
    </footer>
  )
}
