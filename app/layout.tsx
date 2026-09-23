import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono-jb',
  display: 'swap',
})

const TAGLINE = 'Your README demo that never goes stale.'
const DESCRIPTION =
  'evergif is an open-source Agent Skill. One line to install in any coding agent. It records a terminal or web demo, embeds it in your README, and CI re-renders it only when what it shows actually changed.'

export const metadata: Metadata = {
  metadataBase: new URL('https://evergif.dev'),
  title: `evergif — ${TAGLINE}`,
  description: DESCRIPTION,
  applicationName: 'evergif',
  keywords: [
    'evergif',
    'README GIF',
    'agent skill',
    'vhs',
    'Playwright',
    'terminal demo',
    'CI',
    'developer tools',
  ],
  authors: [{ name: 'Shreyas Dasari' }],
  openGraph: {
    type: 'website',
    title: `evergif — ${TAGLINE}`,
    description: DESCRIPTION,
    siteName: 'evergif',
    url: 'https://evergif.dev',
    images: [
      {
        url: '/og.png',
        width: 1200,
        height: 630,
        alt: 'evergif — your README demo that never goes stale.',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: `evergif — ${TAGLINE}`,
    description: DESCRIPTION,
    images: ['/og.png'],
  },
}

export const viewport = {
  themeColor: '#0b0d0f',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${jetbrainsMono.variable} bg-background`}
    >
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  )
}
