import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { AppShell } from '@/components/app/AppShell'
import { getCandidate } from '@/features/investigation/services/nisarService'
import type { CandidateAnomaly } from '@/features/investigation/types'
import { buildEarthEventFingerprint } from '@/features/evidence/services/fingerprintService'
import type { EarthEventFingerprint } from '@/features/evidence/types'
import { ChangeSummary } from '@/features/evidence/components/ChangeSummary'
import { EvidenceBoard } from '@/features/evidence/components/EvidenceBoard'
import { UncertaintyPanel } from '@/features/evidence/components/UncertaintyPanel'
import { ROUTES } from '@/lib/constants'

/**
 * The evidence-collection stage of the investigation: given a selected
 * candidate anomaly, assemble its Earth Event Fingerprint (six
 * independent clues) and present it. This page deliberately stops short
 * of any cause determination — that comparison is a later prompt.
 */
export function CaseInvestigationPage() {
  const { candidateId } = useParams<{ candidateId: string }>()
  const [candidate, setCandidate] = useState<CandidateAnomaly | undefined>()
  const [fingerprint, setFingerprint] = useState<EarthEventFingerprint | undefined>()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    if (!candidateId) {
      setLoading(false)
      return
    }
    setLoading(true)

    getCandidate(candidateId).then(async (found) => {
      if (cancelled) return
      setCandidate(found)
      if (found) {
        const fp = await buildEarthEventFingerprint(found)
        if (!cancelled) setFingerprint(fp)
      }
      if (!cancelled) setLoading(false)
    })

    return () => {
      cancelled = true
    }
  }, [candidateId])

  const radarClue = fingerprint?.clues.find((c) => c.id === 'radar')

  return (
    <AppShell>
      <div className="mx-auto max-w-5xl px-6 py-10 lg:py-14">
        <Link
          to={ROUTES.investigate}
          className="mb-8 inline-flex items-center gap-1.5 text-sm font-medium text-[var(--color-primary)] hover:underline"
        >
          <ArrowLeft size={14} aria-hidden="true" /> Back to investigation start
        </Link>

        {loading && <p className="text-center text-[var(--color-muted)]">Assembling evidence…</p>}

        {!loading && !candidate && (
          <p className="text-center text-[var(--color-muted)]">
            We couldn&rsquo;t find that candidate anomaly. It may not exist in the demonstration catalog.
          </p>
        )}

        {!loading && candidate && fingerprint && radarClue?.id === 'radar' && (
          <div className="flex flex-col gap-6">
            <ChangeSummary candidate={candidate} radar={radarClue} />
            <EvidenceBoard fingerprint={fingerprint} />
            <UncertaintyPanel uncertainty={fingerprint.uncertainty} />

            <div className="rounded-2xl border border-dashed border-[var(--color-sky)] bg-white/60 p-5 text-center">
              <p className="text-sm text-[var(--color-muted)]">
                Candidate-cause comparison — weighing these clues against competing hypotheses — is the next stage of
                the investigation and has not been implemented yet.
              </p>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  )
}
