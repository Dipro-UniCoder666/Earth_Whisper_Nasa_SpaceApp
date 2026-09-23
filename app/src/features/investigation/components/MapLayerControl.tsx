import { Layers } from 'lucide-react'

export interface MapLayerState {
  candidateAnomalies: boolean
}

interface MapLayerControlProps {
  layers: MapLayerState
  onChange: (layers: MapLayerState) => void
}

const LAYER_OPTIONS: Array<{ key: keyof MapLayerState; label: string; disabled?: boolean }> = [
  { key: 'candidateAnomalies', label: 'Candidate anomalies' },
]

/**
 * Compact layer toggle panel. Only "candidate anomalies" is wired up today;
 * NISAR footprint and raster overlays are reserved as disabled entries so
 * the control doesn't need restructuring when those layers arrive.
 */
export function MapLayerControl({ layers, onChange }: MapLayerControlProps) {
  return (
    <div className="rounded-xl border border-[var(--color-sky)] bg-white/95 p-3 shadow-[0_10px_30px_-18px_rgba(7,59,102,0.4)] backdrop-blur-sm">
      <p className="mb-2 flex items-center gap-1.5 text-[0.65rem] font-semibold uppercase tracking-wide text-[var(--color-muted)]">
        <Layers size={12} aria-hidden="true" />
        Layers
      </p>
      <ul className="flex flex-col gap-1.5">
        {LAYER_OPTIONS.map((option) => (
          <li key={option.key}>
            <label className="flex items-center gap-2 text-sm text-[var(--color-text)]">
              <input
                type="checkbox"
                checked={layers[option.key]}
                onChange={(e) => onChange({ ...layers, [option.key]: e.target.checked })}
                className="h-3.5 w-3.5 rounded accent-[var(--color-primary)]"
              />
              {option.label}
            </label>
          </li>
        ))}
        <li>
          <span className="flex items-center gap-2 text-sm text-[var(--color-muted)]/70" title="Reserved for a future prompt">
            <input type="checkbox" disabled className="h-3.5 w-3.5 rounded" />
            NISAR footprint
          </span>
        </li>
        <li>
          <span className="flex items-center gap-2 text-sm text-[var(--color-muted)]/70" title="Reserved for a future prompt">
            <input type="checkbox" disabled className="h-3.5 w-3.5 rounded" />
            Raster overlays
          </span>
        </li>
      </ul>
    </div>
  )
}
