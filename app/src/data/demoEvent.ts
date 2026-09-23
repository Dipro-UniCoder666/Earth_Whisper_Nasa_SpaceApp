import type { DemoEvent } from './eventTypes'

/**
 * Prototype NISAR anomaly ("Candidate #1").
 *
 * This is NOT a confirmed landslide or disaster. It is a coherence-loss
 * anomaly identified in early QGIS analysis of NISAR coherence products.
 * Only measured values are populated here — no rainfall, terrain, optical,
 * fire, or cause data has been fabricated. Fields without real data are
 * simply left undefined and the UI must represent that honestly as
 * "not yet collected," not as zero or "none."
 */
export const demoEvent: DemoEvent = {
  id: 'candidate-001',
  title: 'Prototype NISAR anomaly — Candidate #1',
  status: 'prototype-anomaly',
  location: {
    latitude: 31.1105,
    longitude: 77.9373,
    label: 'Candidate region, Monda, Uttarakhand, India',
  },
  area: {
    valueSqKm: 41.57,
    description: 'Approximate candidate polygon area from QGIS coherence-loss clustering.',
  },
  evidence: {
    nisar: {
      coherenceBefore: 0.6648,
      coherenceAfter: 0.2188,
      meanCoherenceChange: -0.446,
      productType: 'NISAR coherence (prototype QGIS analysis)',
    },
    // terrain, weather, optical, fire, water evidence: not yet collected.
  },
  hypotheses: [
    { type: 'landslide', label: 'Landslide / slope disturbance', status: 'not-yet-assessed' },
    { type: 'flood', label: 'Flood / water-related change', status: 'not-yet-assessed' },
    { type: 'vegetation-disturbance', label: 'Vegetation disturbance', status: 'not-yet-assessed' },
    { type: 'wildfire', label: 'Wildfire / burned area', status: 'not-yet-assessed' },
    { type: 'human-disturbance', label: 'Human land-surface disturbance', status: 'not-yet-assessed' },
    { type: 'subsidence', label: 'Ground subsidence', status: 'not-yet-assessed' },
    { type: 'seismic-deformation', label: 'Earthquake-related deformation', status: 'not-yet-assessed' },
    { type: 'undetermined', label: 'Undetermined', status: 'not-yet-assessed' },
  ],
  uncertainty: {
    known: [
      'A substantial coherence loss (~-0.446 mean change) was measured across the candidate polygon.',
      'The candidate area is approximately 41.57 km².',
    ],
    uncertain: [
      'What caused the coherence loss has not yet been investigated.',
      'No independent environmental evidence has been collected for this location yet.',
    ],
    cannotConclude: [
      'This anomaly cannot yet be attributed to any specific event type.',
      'No claim of landslide, disaster, or hazard can be made from coherence loss alone.',
    ],
  },
  sources: [{ label: 'AquaByte NISAR/QGIS prototype workspace' }],
}
