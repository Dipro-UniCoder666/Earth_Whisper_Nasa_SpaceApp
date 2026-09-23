import type { InvestigationSite } from '@/features/investigation/data/investigationSite'
import { buildPdf, type PdfBlock } from '@/features/investigation/caseFile/minimalPdf'
import { buildZip, textToBytes, type ZipEntry } from '@/features/investigation/caseFile/zipWriter'

/**
 * Event Case File generator.
 *
 * Consumes an InvestigationSite - never a hard-coded place - so the package
 * always describes the investigation the user actually ran.
 */

export const CASE_FILE_NAMES = {
  pdf: '01_Event_Summary.pdf',
  json: '02_Investigation_Data.json',
  sources: '03_Data_Sources.txt',
  methodology: '04_Methodology.txt',
  readme: '05_Readme.txt',
} as const

/** e.g. EARTH_WHISPER_CASE_FILE_Monda_Uttarakhand.zip */
export function caseFileName(site: InvestigationSite): string {
  const slug = site.name
    .replace(/[^A-Za-z0-9 ]/g, ' ')
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .join('_')
  return 'EARTH_WHISPER_CASE_FILE_' + (slug || 'Investigation') + '.zip'
}

const pixels = (value: number) => value.toLocaleString('en-US')

export function buildInvestigationJson(site: InvestigationSite): string {
  const payload = {
    project: 'Earth Whisper',
    team: 'AquaByte',
    challenge: 'NASA Space Apps Challenge 2026',
    generated_at: new Date().toISOString(),
    location: {
      name: site.name,
      latitude: site.coords.lat,
      longitude: site.coords.lng,
      latitude_display: site.latitude,
      longitude_display: site.longitude,
    },
    nisar: {
      product: site.nisar.product,
      before_coherence: site.nisar.beforeCoherence,
      after_coherence: site.nisar.afterCoherence,
      mean_change: site.nisar.meanChange,
      median_change: site.nisar.medianChange,
      valid_pixels: site.nisar.validPixels,
      observation_summary: site.nisar.observationSummary,
    },
    terrain: {
      dem: site.terrain.dem,
      elevation_m: site.terrain.elevationMeters,
      local_slope_deg: site.terrain.localSlopeDegrees,
      terrain_context: site.terrain.context,
      summary: site.terrain.summary,
    },
    data_sources: site.sources.map((source) => ({
      dataset: source.dataset,
      provider: source.provider,
      purpose: source.purpose,
      url: source.url,
    })),
    limitation: site.limitation,
  }
  return JSON.stringify(payload, null, 2)
}

export function buildDataSourcesText(site: InvestigationSite): string {
  const lines: string[] = []
  lines.push('EARTH WHISPER - DATA SOURCES')
  lines.push('='.repeat(60))
  lines.push('')
  lines.push('Investigation: ' + site.name)
  lines.push('Coordinates:   ' + site.coordLabel)
  lines.push('')
  site.sources.forEach((source) => {
    lines.push('Dataset : ' + source.dataset)
    lines.push('Provider: ' + source.provider)
    lines.push('Purpose : ' + source.purpose)
    lines.push('Source  : ' + source.url)
    lines.push('')
  })
  lines.push('Note: source URLs are the official portals used or referenced by this')
  lines.push('prototype. The measurements in this case file are the values computed in')
  lines.push('the Earth Whisper prototype analysis; they are not re-derived here.')
  return lines.join('\n')
}

export function buildMethodologyText(site: InvestigationSite): string {
  const lines: string[] = []
  lines.push('EARTH WHISPER - METHODOLOGY')
  lines.push('='.repeat(60))
  lines.push('')
  lines.push('Investigation: ' + site.name + ' (' + site.coordLabel + ')')
  lines.push('')
  lines.push('Workflow')
  lines.push('--------')
  site.methodology.forEach((step, index) => {
    lines.push(index + 1 + '. ' + step)
  })
  lines.push('')
  lines.push('Measurements')
  lines.push('------------')
  lines.push('Before coherence: ' + site.nisar.beforeCoherence)
  lines.push('After coherence:  ' + site.nisar.afterCoherence)
  lines.push('Mean change:      ' + site.nisar.meanChange)
  lines.push('Median change:    ' + site.nisar.medianChange)
  lines.push('Valid pixels:     ' + pixels(site.nisar.validPixels))
  lines.push('Elevation:        ' + pixels(site.terrain.elevationMeters) + ' m (' + site.terrain.dem + ')')
  lines.push('Local slope:      ' + site.terrain.localSlopeDegrees + '\u00b0')
  lines.push('')
  lines.push('Limitation')
  lines.push('----------')
  lines.push(site.limitation)
  return lines.join('\n')
}

export function buildReadmeText(site: InvestigationSite): string {
  const lines: string[] = []
  lines.push('EARTH WHISPER - EVENT CASE FILE')
  lines.push('='.repeat(60))
  lines.push('')
  lines.push('Location:    ' + site.name)
  lines.push('Coordinates: ' + site.coordLabel)
  lines.push('')
  lines.push('What was investigated')
  lines.push('---------------------')
  lines.push(
    'Earth Whisper examined radar coherence change together with terrain context at the selected location.',
  )
  lines.push('')
  lines.push('Datasets used')
  lines.push('-------------')
  site.sources.forEach((source) => {
    lines.push('- ' + source.dataset + ' (' + source.provider + ')')
  })
  lines.push('')
  lines.push('Measured results')
  lines.push('----------------')
  lines.push('Coherence before -> after: ' + site.nisar.beforeCoherence + ' -> ' + site.nisar.afterCoherence)
  lines.push('Mean coherence change:    ' + site.nisar.meanChange)
  lines.push('Median coherence change:  ' + site.nisar.medianChange)
  lines.push('Valid pixels:             ' + pixels(site.nisar.validPixels))
  lines.push('Elevation:                ' + pixels(site.terrain.elevationMeters) + ' m')
  lines.push('Local slope:              ' + site.terrain.localSlopeDegrees + '\u00b0')
  lines.push('')
  lines.push('Interpreting the evidence')
  lines.push('-------------------------')
  lines.push(site.nisar.observationSummary)
  lines.push(site.terrain.summary)
  lines.push(site.limitation)
  lines.push('')
  lines.push('Files in this package')
  lines.push('---------------------')
  Object.values(CASE_FILE_NAMES).forEach((name) => lines.push('- ' + name))
  return lines.join('\n')
}

export function buildSummaryPdf(site: InvestigationSite): Blob {
  const blocks: PdfBlock[] = [
    { text: 'EARTH WHISPER', size: 12, bold: true },
    { text: 'EARTH EVENT CASE FILE', size: 22, bold: true },
    { text: 'Location: ' + site.name, size: 12, gapBefore: 12 },
    { text: 'Coordinates: ' + site.coordLabel, size: 12 },

    { text: 'Investigation summary', size: 13, bold: true, gapBefore: 24, rule: true },
    {
      text:
        'Earth Whisper examined radar coherence change together with terrain context at ' +
        site.name +
        '. This case file documents the measured evidence for the investigation; it does not assign a cause to the observed change.',
      size: 11,
      gapBefore: 8,
    },

    { text: 'NISAR radar observation (' + site.nisar.product + ')', size: 13, bold: true, gapBefore: 24, rule: true },
    { text: 'Before coherence: ' + site.nisar.beforeCoherence, size: 11, gapBefore: 8 },
    { text: 'After coherence: ' + site.nisar.afterCoherence, size: 11 },
    { text: 'Mean coherence change: ' + site.nisar.meanChange, size: 11 },
    { text: 'Median coherence change: ' + site.nisar.medianChange, size: 11 },
    { text: 'Valid pixels: ' + pixels(site.nisar.validPixels), size: 11 },
    { text: site.nisar.observationSummary, size: 11, gapBefore: 8 },

    { text: 'Signal comparison', size: 13, bold: true, gapBefore: 24, rule: true },
    {
      kind: 'bars',
      beforeLabel: 'BEFORE',
      afterLabel: 'AFTER',
      beforeValue: site.nisar.beforeCoherence,
      afterValue: site.nisar.afterCoherence,
      caption:
        site.nisar.beforeCoherence +
        ' -> ' +
        site.nisar.afterCoherence +
        '   mean change ' +
        site.nisar.meanChange +
        '   median change ' +
        site.nisar.medianChange,
    },

    { text: 'Terrain context', size: 13, bold: true, gapBefore: 20, rule: true },
    { text: 'Elevation: ' + pixels(site.terrain.elevationMeters) + ' m', size: 11, gapBefore: 8 },
    { text: 'Local slope: ' + site.terrain.localSlopeDegrees + '\u00b0', size: 11 },
    { text: 'Terrain context: ' + site.terrain.context, size: 11 },
    { text: 'Source: ' + site.terrain.dem, size: 11 },

    { text: 'Observation summary', size: 13, bold: true, gapBefore: 24, rule: true },
    { text: 'RADAR SIGNAL', size: 10, bold: true, gapBefore: 8 },
    { text: site.nisar.observationSummary, size: 11 },
    { text: 'TERRAIN CONTEXT', size: 10, bold: true, gapBefore: 10 },
    { text: site.terrain.summary, size: 11 },
    { text: 'EVIDENCE COVERAGE', size: 10, bold: true, gapBefore: 10 },
    {
      text: pixels(site.nisar.validPixels) + ' valid NISAR pixels were used for the regional coherence comparison.',
      size: 11,
    },

    { text: 'Data used', size: 13, bold: true, gapBefore: 24, rule: true },
  ]

  site.sources.forEach((source, index) => {
    blocks.push({
      text: source.dataset + ' - ' + source.provider,
      size: 11,
      bold: true,
      gapBefore: index === 0 ? 8 : 10,
    })
    blocks.push({ text: source.purpose, size: 10 })
  })

  blocks.push({ text: 'Investigation location', size: 13, bold: true, gapBefore: 24, rule: true })
  blocks.push({ text: site.name, size: 11, gapBefore: 8 })
  blocks.push({ text: site.latitude + ' N', size: 11 })
  blocks.push({ text: site.longitude + ' E', size: 11 })

  blocks.push({ text: 'Data sources', size: 13, bold: true, gapBefore: 24, rule: true })
  blocks.push({
    text: 'The full dataset / provider / URL listing is provided in ' + CASE_FILE_NAMES.sources + '.',
    size: 10,
    gapBefore: 8,
  })

  return buildPdf('Earth Whisper - Earth Event Case File', blocks)
}

function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  document.body.removeChild(anchor)
  window.setTimeout(() => URL.revokeObjectURL(url), 4000)
}

/** Builds the full case file (summary PDF + structured data + documentation) and downloads it as a ZIP. */
export async function downloadCaseFile(site: InvestigationSite): Promise<void> {
  const pdfBlob = buildSummaryPdf(site)
  const pdfBytes = new Uint8Array(await pdfBlob.arrayBuffer())

  const entries: ZipEntry[] = [
    { name: CASE_FILE_NAMES.pdf, data: pdfBytes },
    { name: CASE_FILE_NAMES.json, data: textToBytes(buildInvestigationJson(site)) },
    { name: CASE_FILE_NAMES.sources, data: textToBytes(buildDataSourcesText(site)) },
    { name: CASE_FILE_NAMES.methodology, data: textToBytes(buildMethodologyText(site)) },
    { name: CASE_FILE_NAMES.readme, data: textToBytes(buildReadmeText(site)) },
  ]

  triggerDownload(buildZip(entries), caseFileName(site))
}
