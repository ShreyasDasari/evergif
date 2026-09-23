'use client'

import { useEffect, useRef, useState } from 'react'

export function Reveal({
  children,
  className,
  as: Tag = 'div',
  delay = 0,
}: {
  children: React.ReactNode
  className?: string
  as?: React.ElementType
  delay?: number
}) {
  const ref = useRef<HTMLElement | null>(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setVisible(true)
            observer.disconnect()
          }
        })
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' },
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  return (
    <Tag
      ref={ref}
      style={delay ? { transitionDelay: `${delay}ms` } : undefined}
      className={`reveal ${visible ? 'is-visible' : ''} ${className ?? ''}`}
    >
      {children}
    </Tag>
  )
}
