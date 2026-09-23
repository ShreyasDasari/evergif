import { SiteHeader } from '@/components/site-header'
import { Hero } from '@/components/hero'
import { ProblemFix } from '@/components/problem-fix'
import { HowItWorks } from '@/components/how-it-works'
import { SeeItWork } from '@/components/see-it-work'
import { RepoTree } from '@/components/repo-tree'
import { AgentWall } from '@/components/agent-wall'
import { FeatureGrid } from '@/components/feature-grid'
import { FinalCta } from '@/components/final-cta'
import { SiteFooter } from '@/components/site-footer'

export default function Page() {
  return (
    <>
      <SiteHeader />
      <main>
        <Hero />
        <ProblemFix />
        <HowItWorks />
        <SeeItWork />
        <RepoTree />
        <AgentWall />
        <FeatureGrid />
        <FinalCta />
      </main>
      <SiteFooter />
    </>
  )
}
