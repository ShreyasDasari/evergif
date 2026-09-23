import { GITHUB_URL } from '@/lib/constants'

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-border/70 bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-[1100px] items-center justify-between px-5 sm:px-8">
        <a
          href="#top"
          className="font-mono text-sm font-semibold tracking-tight text-foreground"
        >
          evergif
        </a>
        <nav className="flex items-center gap-5 text-sm">
          <a
            href="#how"
            className="hidden text-muted transition-colors hover:text-foreground sm:inline"
          >
            How it works
          </a>
          <a
            href="#see-it-work"
            className="hidden text-muted transition-colors hover:text-foreground sm:inline"
          >
            See it work
          </a>
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noreferrer noopener"
            className="text-muted transition-colors hover:text-foreground"
          >
            GitHub
          </a>
        </nav>
      </div>
    </header>
  )
}
