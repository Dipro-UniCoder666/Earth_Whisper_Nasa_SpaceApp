import { useState } from 'react'
import { Satellite } from 'lucide-react'
import { DHARA_CONTEXT_IMAGE } from './services/gherproofApi'
import './contextSatelliteImage.css'

export function ContextSatelliteImage({ className, alt }: { className?: string; alt: string }) {
  const [unavailable, setUnavailable] = useState(false)

  if (unavailable) {
    return (
      <div className={`gp-context-image-fallback ${className ?? ''}`} role="img" aria-label={`${alt} Image unavailable.`}>
        <Satellite size={24} aria-hidden="true" />
        <span>Sentinel-2 context preview unavailable</span>
        <small>Acquired January 13, 2026</small>
      </div>
    )
  }

  return <img className={className} src={DHARA_CONTEXT_IMAGE} alt={alt} onError={() => setUnavailable(true)} />
}
