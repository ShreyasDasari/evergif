'use client'

import { useEffect, useState } from 'react'
import { GITHUB_URL } from '@/lib/constants'
import { GitHubIcon, StarIcon } from '@/components/icons'
import { Wordmark } from '@/components/wordmark'

const LINKS = [
  { href: '#how', label: 'How it works' },
  { href: '#see-it-work', label: 'See it work' },
  { href: '#features', label: 'Features' },
]

export function SiteHeader() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 16)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header className="fixed inset-x-0 top-0 z-50 flex justify-center px-3 sm:px-4">
      <div
        className={`mt-3 flex w-full max-w-[1080px] items-center justify-between gap-3 rounded-2xl px-3 transition-all duration-300 sm:px-4 ${
          scrolled
            ? 'glass-strong sm:max-w-[880px]'
            : 'border border-transparent'
        }`}
        style={{ height: scrolled ? '3.25rem' : '3.5rem' }}
      >
        <a
          href="#top"
          className="flex items-center gap-2 rounded-lg px-1 text-sm"
          aria-label="evergif — home"
        >
          <Wordmark className="text-[15px]" />
        </a>

        <nav className="hidden items-center gap-1 md:flex">
          {LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="rounded-lg px-3 py-1.5 text-sm text-muted transition-colors hover:bg-white/5 hover:text-foreground"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noreferrer noopener"
          className="glass-hover group inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-1.5 text-sm font-medium text-foreground"
        >
          <GitHubIcon className="h-4 w-4" />
          <span className="hidden sm:inline">Star</span>
          <StarIcon className="h-3.5 w-3.5 text-accent transition-transform group-hover:scale-110" />
        </a>
      </div>
    </header>
  )
}
