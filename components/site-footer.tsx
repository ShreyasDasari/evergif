import { GITHUB_URL } from '@/lib/constants'

export function SiteFooter() {
  return (
    <footer className="border-t border-border">
      <div className="mx-auto flex max-w-[1100px] flex-col gap-3 px-5 py-8 text-sm sm:flex-row sm:items-center sm:justify-between sm:px-8">
        <p className="text-faint">
          MIT licensed. Built on vhs by Charm and Playwright by Microsoft.
        </p>
        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noreferrer noopener"
          className="text-muted transition-colors hover:text-foreground"
        >
          GitHub
        </a>
      </div>
    </footer>
  )
}
