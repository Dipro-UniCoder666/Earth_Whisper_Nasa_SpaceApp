import { ImageOff } from 'lucide-react'
import type { OpticalClue } from '@/features/evidence/types'

export function OpticalClueDetail({ clue }: { clue: OpticalClue }) {
  if (clue.availability !== 'unavailable') return null

  return (
    <div className="flex items-center gap-3 rounded-xl bg-[var(--color-bg)] p-4 text-[var(--color-muted)]">
      <ImageOff size={20} aria-hidden="true" className="shrink-0" />
      <p className="text-xs leading-relaxed">
        No before/after imagery is available yet. This space will show a visual comparison once optical imagery
        integration is implemented.
      </p>
    </div>
  )
}
