/**
 * Minimal dependency-free PDF writer.
 *
 * Produces a text-only A4 PDF using the standard Helvetica base fonts, plus a
 * simple bar graphic for the coherence comparison. Deliberately small: the
 * project has no PDF dependency and the case file only needs clean text pages.
 */

export interface PdfTextLine {
  kind?: 'text'
  text: string
  size?: number
  bold?: boolean
  /** Extra vertical space inserted before this line, in points. */
  gapBefore?: number
  /** Draw a thin rule above this line. */
  rule?: boolean
}

export interface PdfBarChart {
  kind: 'bars'
  beforeLabel: string
  afterLabel: string
  beforeValue: number
  afterValue: number
  caption?: string
}

export type PdfBlock = PdfTextLine | PdfBarChart

const PAGE_W = 595.28
const PAGE_H = 841.89
const MARGIN = 56
const MAX_W = PAGE_W - MARGIN * 2
const LINE_GAP = 4

/** WinAnsi-safe escaping for PDF literal strings. */
function esc(text: string): string {
  let out = text
  const replacements: Array<[string, string]> = [
    ['\u00b0', '\\260'], // degree
    ['\u00b7', '\\267'], // middle dot
    ['\u2013', '-'],
    ['\u2014', '-'],
    ['\u2192', '->'],
    ['\u2019', "'"],
    ['\u2018', "'"],
    ['\u201c', '"'],
    ['\u201d', '"'],
  ]
  for (const pair of replacements) out = out.split(pair[0]).join(pair[1])
  out = out.replace(/[^\x20-\x7e]/g, '?')
  return out.replace(/\\/g, '\\\\').replace(/\(/g, '\\(').replace(/\)/g, '\\)')
}

/** Rough Helvetica width estimate, adequate for line wrapping. */
function textWidth(text: string, size: number, bold: boolean): number {
  return text.length * size * (bold ? 0.55 : 0.5)
}

function wrap(text: string, size: number, bold: boolean, maxWidth: number): string[] {
  const words = text.split(/\s+/).filter(Boolean)
  const lines: string[] = []
  let current = ''
  for (const word of words) {
    const candidate = current ? current + ' ' + word : word
    if (textWidth(candidate, size, bold) <= maxWidth) {
      current = candidate
    } else {
      if (current) lines.push(current)
      current = word
    }
  }
  if (current) lines.push(current)
  return lines.length ? lines : ['']
}

export function buildPdf(docTitle: string, blocks: PdfBlock[]): Blob {
  const pages: string[] = []
  let ops: string[] = []
  let y = PAGE_H - MARGIN

  const newPage = () => {
    if (ops.length) pages.push(ops.join('\n'))
    ops = []
    y = PAGE_H - MARGIN
  }

  const ensure = (needed: number) => {
    if (y - needed < MARGIN) newPage()
  }

  for (const block of blocks) {
    if (block.kind === 'bars') {
      ensure(110)
      const barH = 16
      const trackW = MAX_W - 80
      const beforeW = Math.max(6, Math.min(1, Math.max(0, block.beforeValue)) * trackW)
      const afterW = Math.max(6, Math.min(1, Math.max(0, block.afterValue)) * trackW)

      y -= 20
      ops.push('0.10 0.10 0.12 rg')
      ops.push('BT /F1 9 Tf ' + MARGIN + ' ' + y.toFixed(2) + ' Td (' + esc(block.beforeLabel) + ') Tj ET')
      ops.push(MARGIN + 66 + ' ' + (y - 4).toFixed(2) + ' ' + beforeW.toFixed(2) + ' ' + barH + ' re f')

      y -= 28
      ops.push('BT /F1 9 Tf ' + MARGIN + ' ' + y.toFixed(2) + ' Td (' + esc(block.afterLabel) + ') Tj ET')
      ops.push(MARGIN + 66 + ' ' + (y - 4).toFixed(2) + ' ' + afterW.toFixed(2) + ' ' + barH + ' re f')

      y -= 24
      if (block.caption) {
        ops.push('BT /F1 9 Tf ' + MARGIN + ' ' + y.toFixed(2) + ' Td (' + esc(block.caption) + ') Tj ET')
        y -= 16
      }
      continue
    }

    const size = block.size ?? 11
    const bold = block.bold ?? false
    const font = bold ? '/F2' : '/F1'
    if (block.gapBefore) y -= block.gapBefore
    if (block.rule) {
      ensure(24)
      ops.push('0.82 0.86 0.90 rg')
      ops.push(MARGIN + ' ' + (y + 8).toFixed(2) + ' ' + MAX_W.toFixed(2) + ' 0.7 re f')
      ops.push('0 0 0 rg')
      y -= 6
    }
    for (const line of wrap(block.text, size, bold, MAX_W)) {
      ensure(size + LINE_GAP)
      y -= size + LINE_GAP
      ops.push('BT ' + font + ' ' + size + ' Tf ' + MARGIN + ' ' + y.toFixed(2) + ' Td (' + esc(line) + ') Tj ET')
    }
  }
  if (ops.length) pages.push(ops.join('\n'))
  if (!pages.length) {
    pages.push('BT /F1 12 Tf 56 780 Td (' + esc(docTitle) + ') Tj ET')
  }

  const objects: string[] = []
  const pageCount = pages.length
  const firstPageObj = 5
  const kids = pages.map((_, i) => firstPageObj + i * 2 + ' 0 R').join(' ')
  objects[1] = '<< /Type /Catalog /Pages 2 0 R >>'
  objects[2] = '<< /Type /Pages /Kids [' + kids + '] /Count ' + pageCount + ' >>'
  objects[3] = '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>'
  objects[4] = '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>'

  pages.forEach((content, i) => {
    const pageObj = firstPageObj + i * 2
    const contentObj = pageObj + 1
    objects[pageObj] =
      '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ' +
      PAGE_W +
      ' ' +
      PAGE_H +
      '] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents ' +
      contentObj +
      ' 0 R >>'
    objects[contentObj] = '<< /Length ' + content.length + ' >>\nstream\n' + content + '\nendstream'
  })

  let pdf = '%PDF-1.4\n'
  const offsets: number[] = []
  for (let i = 1; i < objects.length; i += 1) {
    const body = objects[i]
    if (!body) continue
    offsets[i] = pdf.length
    pdf += i + ' 0 obj\n' + body + '\nendobj\n'
  }

  const xrefStart = pdf.length
  const maxObj = objects.length - 1
  pdf += 'xref\n0 ' + (maxObj + 1) + '\n0000000000 65535 f \n'
  for (let i = 1; i <= maxObj; i += 1) {
    pdf += String(offsets[i] ?? 0).padStart(10, '0') + ' 00000 n \n'
  }
  pdf += 'trailer\n<< /Size ' + (maxObj + 1) + ' /Root 1 0 R >>\nstartxref\n' + xrefStart + '\n%%EOF\n'

  const bytes = new Uint8Array(pdf.length)
  for (let i = 0; i < pdf.length; i += 1) bytes[i] = pdf.charCodeAt(i) & 0xff
  return new Blob([bytes], { type: 'application/pdf' })
}
