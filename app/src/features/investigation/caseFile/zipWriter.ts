/**
 * Minimal dependency-free ZIP writer (STORE method, no compression).
 *
 * Enough to package the case-file documents into one .zip without adding a
 * compression dependency to the project.
 */
export interface ZipEntry {
  name: string
  data: Uint8Array
}

const CRC_TABLE = (() => {
  const table = new Uint32Array(256)
  for (let n = 0; n < 256; n += 1) {
    let c = n
    for (let k = 0; k < 8; k += 1) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1
    table[n] = c >>> 0
  }
  return table
})()

function crc32(data: Uint8Array): number {
  let c = 0xffffffff
  for (let i = 0; i < data.length; i += 1) c = CRC_TABLE[(c ^ data[i]) & 0xff] ^ (c >>> 8)
  return (c ^ 0xffffffff) >>> 0
}

class ByteWriter {
  private chunks: Uint8Array[] = []
  length = 0

  bytes(data: Uint8Array) {
    this.chunks.push(data)
    this.length += data.length
  }

  u16(value: number) {
    this.bytes(new Uint8Array([value & 0xff, (value >>> 8) & 0xff]))
  }

  u32(value: number) {
    this.bytes(
      new Uint8Array([
        value & 0xff,
        (value >>> 8) & 0xff,
        (value >>> 16) & 0xff,
        (value >>> 24) & 0xff,
      ]),
    )
  }

  toBlob(type: string): Blob {
    const merged = new Uint8Array(this.length)
    let offset = 0
    for (const chunk of this.chunks) {
      merged.set(chunk, offset)
      offset += chunk.length
    }
    return new Blob([merged], { type })
  }
}

export function textToBytes(text: string): Uint8Array {
  const encoded = unescape(encodeURIComponent(text))
  const out = new Uint8Array(encoded.length)
  for (let i = 0; i < encoded.length; i += 1) out[i] = encoded.charCodeAt(i)
  return out
}

export function buildZip(entries: ZipEntry[]): Blob {
  const out = new ByteWriter()
  const central: Array<{ name: Uint8Array; crc: number; size: number; offset: number }> = []

  for (const entry of entries) {
    const name = textToBytes(entry.name)
    const crc = crc32(entry.data)
    const offset = out.length

    out.u32(0x04034b50) // local file header
    out.u16(20) // version needed
    out.u16(0) // general purpose flags
    out.u16(0) // method: store
    out.u16(0) // last mod time
    out.u16(0) // last mod date
    out.u32(crc)
    out.u32(entry.data.length) // compressed size
    out.u32(entry.data.length) // uncompressed size
    out.u16(name.length)
    out.u16(0) // extra field length
    out.bytes(name)
    out.bytes(entry.data)

    central.push({ name, crc, size: entry.data.length, offset })
  }

  const centralStart = out.length
  for (const item of central) {
    out.u32(0x02014b50) // central directory header
    out.u16(20) // version made by
    out.u16(20) // version needed
    out.u16(0) // flags
    out.u16(0) // method
    out.u16(0) // time
    out.u16(0) // date
    out.u32(item.crc)
    out.u32(item.size)
    out.u32(item.size)
    out.u16(item.name.length)
    out.u16(0) // extra
    out.u16(0) // comment
    out.u16(0) // disk number start
    out.u16(0) // internal attributes
    out.u32(0) // external attributes
    out.u32(item.offset)
    out.bytes(item.name)
  }
  const centralSize = out.length - centralStart

  out.u32(0x06054b50) // end of central directory
  out.u16(0) // disk number
  out.u16(0) // disk with central directory
  out.u16(central.length)
  out.u16(central.length)
  out.u32(centralSize)
  out.u32(centralStart)
  out.u16(0) // comment length

  return out.toBlob('application/zip')
}
