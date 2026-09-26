/**
 * Earth Whisper - investigation site model.
 *
 * Single source of truth for an investigated location: the result section,
 * the Science Mode panel and the Event Case File generator all consume this
 * object. Nothing downstream hard-codes a place name or a measurement, so a
 * future investigation only needs a new entry here.
 *
 * All values are the team's real prototype measurements.
 */
export interface InvestigationSource {
  dataset: string
  provider: string
  purpose: string
  url: string
}

export interface InvestigationSite {
  id: string
  /** Short label used on the available-investigation card. */
  shortName: string
  /** Full place name. */
  name: string
  coords: { lat: number; lng: number }
  /** Six-decimal display strings, as measured. */
  latitude: string
  longitude: string
  /** Pre-formatted coordinate label, e.g. `31.110500° N · 77.937300° E`. */
  coordLabel: string
  nisar: {
    product: string
    beforeCoherence: number
    afterCoherence: number
    meanChange: number
    medianChange: number
    validPixels: number
    observationSummary: string
  }
  terrain: {
    dem: string
    elevationMeters: number
    localSlopeDegrees: number
    context: string
    summary: string
  }
  sources: InvestigationSource[]
  methodology: string[]
  limitation: string
}

export interface InvestigationLocation {
  id: string
  shortName: string
  subtitle: string
  name: string
  coords: { lat: number; lng: number }
  latitude: string
  longitude: string
  coordLabel: string
  aoiBounds?: [[number, number], [number, number]]
  badges?: string[]
}

export const SANDHYA_INVESTIGATION: InvestigationLocation = {
  id: 'sandhya-river',
  shortName: 'Sandhya River',
  subtitle: 'Babuganj, Barishal, Bangladesh',
  name: 'Sandhya River near Babuganj, Barishal, Bangladesh',
  coords: { lat: 22.49, lng: 90.185 },
  latitude: '22.4900',
  longitude: '90.1850',
  coordLabel: '22.4900° N · 90.1850° E',
  aoiBounds: [[22.47, 90.15], [22.51, 90.22]],
  badges: ['211 radar candidates', '32 investigated'],
}

export const MONDA_INVESTIGATION: InvestigationSite = {
  id: 'monda-uttarakhand',
  shortName: 'Monda, Uttarakhand',
  name: 'Monda, Uttarakhand, India',
  coords: { lat: 31.1105, lng: 77.9373 },
  latitude: '31.110500',
  longitude: '77.937300',
  coordLabel: '31.110500° N · 77.937300° E',
  nisar: {
    product: 'NISAR GUNW coherence',
    beforeCoherence: 0.6648,
    afterCoherence: 0.2188,
    meanChange: -0.446,
    medianChange: -0.4667,
    validPixels: 6504,
    observationSummary:
      'Substantial coherence loss was observed across the investigated region.',
  },
  terrain: {
    dem: 'NASADEM',
    elevationMeters: 2794,
    localSlopeDegrees: 40.8,
    context: 'Mountainous',
    summary:
      'The investigated point sits at 2,794 m elevation with a local slope of 40.8°.',
  },
  sources: [
    {
      dataset: 'NISAR GUNW coherence',
      provider: 'NASA / JPL - NASA-ISRO SAR mission',
      purpose: 'Regional radar coherence-change detection',
      url: 'https://science.nasa.gov/',
    },
    {
      dataset: 'NASA-ISRO SAR (NISAR) mission reference',
      provider: 'NASA Jet Propulsion Laboratory',
      purpose: 'Mission and instrument reference',
      url: 'https://www.jpl.nasa.gov/',
    },
    {
      dataset: 'NASADEM',
      provider: 'NASA',
      purpose: 'Elevation and terrain/slope context',
      url: 'https://www.earthdata.nasa.gov/',
    },
    {
      dataset: 'NASADEM distribution',
      provider: 'OpenTopography',
      purpose: 'Digital elevation model distribution',
      url: 'https://portal.opentopography.org/',
    },
    {
      dataset: 'OpenStreetMap tiles',
      provider: 'OpenStreetMap contributors',
      purpose: 'Investigation map basemap',
      url: 'https://www.openstreetmap.org/copyright',
    },
  ],
  methodology: [
    'NISAR GUNW coherence products for the investigated observation pair',
    'Regional coherence comparison across the candidate investigation region',
    'Zonal statistics over the candidate polygon (mean, median, valid pixel count)',
    'NASADEM elevation and local slope derived at the investigation point',
    'Combination of radar and terrain measurements into the Earth Event Evidence view',
  ],
  limitation:
    'Coherence change indicates a change in radar-scattering consistency between observations; it does not by itself establish the physical cause of the change.',
}
