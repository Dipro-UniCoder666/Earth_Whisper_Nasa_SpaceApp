import { RadioTower } from 'lucide-react'

interface InvestigationScanProps {
  locationName: string
  progress: number
}

const SCAN_TOTALS = [
  ['AOI PIXELS', 79874],
  ['CANDIDATE REGIONS', 211],
  ['INVESTIGATED', 32],
  ['NISAR OBSERVATIONS', 4],
  ['RADAR SOURCES', 2],
] as const

export function InvestigationScan({ locationName, progress }: InvestigationScanProps) {
  return (
    <div className="ew-sandhya-analysis">
      <div className="ew-sandhya-analysis-top">
        <div>
          <p className="ew-panel-label">EARTH WHISPER</p>
          <h2 className="ew-results-title">{locationName.toUpperCase()}</h2>
          <p className="ew-sandhya-analysis-status">SCANNING</p>
        </div>
        <div className="ew-sandhya-signal" aria-hidden="true">
          <RadioTower size={25} />
          <i />
          <i />
          <i />
          <b />
        </div>
      </div>
      <div className="ew-sandhya-scan-field" aria-label={`Scanning verified observations for ${locationName}`}>
        <div className="ew-sandhya-scan-line" aria-hidden="true" />
        {SCAN_TOTALS.map(([label, total]) => (
          <div className="ew-sandhya-scan-metric" key={label}>
            <strong>{Math.round(total * progress).toLocaleString('en-US')}</strong>
            <span>{label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
