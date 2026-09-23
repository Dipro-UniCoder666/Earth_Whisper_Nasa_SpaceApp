import type { EarthEventFingerprint } from '@/features/evidence/types'
import { ClueCard } from '@/features/evidence/components/ClueCard'
import { RadarClueDetail } from '@/features/evidence/components/RadarClueDetail'
import { TerrainClueDetail } from '@/features/evidence/components/TerrainClueDetail'
import { WeatherClueDetail } from '@/features/evidence/components/WeatherClueDetail'
import { OpticalClueDetail } from '@/features/evidence/components/OpticalClueDetail'
import { FireClueDetail } from '@/features/evidence/components/FireClueDetail'
import { WaterClueDetail } from '@/features/evidence/components/WaterClueDetail'
import { summarizeFingerprintCompleteness } from '@/features/evidence/services/fingerprintService'

interface EvidenceBoardProps {
  fingerprint: EarthEventFingerprint
}

export function EvidenceBoard({ fingerprint }: EvidenceBoardProps) {
  const completeness = summarizeFingerprintCompleteness(fingerprint)

  return (
    <div>
      <div className="mb-5 flex flex-wrap items-center gap-3 rounded-xl border border-[var(--color-sky)] bg-white px-4 py-3 text-xs text-[var(--color-muted)]">
        <span className="font-semibold uppercase tracking-wide text-[var(--color-navy)]">Evidence status</span>
        <span>{completeness.measured} measured</span>
        <span aria-hidden="true">·</span>
        <span>{completeness.demonstration} demonstration</span>
        <span aria-hidden="true">·</span>
        <span>{completeness.unavailable} not yet available</span>
      </div>

      <div className="grid gap-5 sm:grid-cols-2">
        {fingerprint.clues.map((clue) => {
          switch (clue.id) {
            case 'radar':
              return (
                <ClueCard key={clue.id} clue={clue} clueNumber={clue.order}>
                  <RadarClueDetail clue={clue} />
                </ClueCard>
              )
            case 'terrain':
              return (
                <ClueCard key={clue.id} clue={clue} clueNumber={clue.order}>
                  <TerrainClueDetail clue={clue} />
                </ClueCard>
              )
            case 'weather':
              return (
                <ClueCard key={clue.id} clue={clue} clueNumber={clue.order}>
                  <WeatherClueDetail clue={clue} />
                </ClueCard>
              )
            case 'optical':
              return (
                <ClueCard key={clue.id} clue={clue} clueNumber={clue.order}>
                  <OpticalClueDetail clue={clue} />
                </ClueCard>
              )
            case 'fire':
              return (
                <ClueCard key={clue.id} clue={clue} clueNumber={clue.order}>
                  <FireClueDetail clue={clue} />
                </ClueCard>
              )
            case 'water':
              return (
                <ClueCard key={clue.id} clue={clue} clueNumber={clue.order}>
                  <WaterClueDetail clue={clue} />
                </ClueCard>
              )
            default:
              return null
          }
        })}
      </div>
    </div>
  )
}
