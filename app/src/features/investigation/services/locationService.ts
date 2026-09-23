import type { LocationSearchResult } from '@/features/investigation/types'

/**
 * Earth Whisper — Location service
 *
 * Abstracts geocoding (place name → coordinates) behind a stable
 * interface so the app is never hard-coded to one provider. Currently
 * backed by OpenStreetMap's Nominatim public API, which pairs naturally
 * with the Leaflet/OSM map and requires no API key — appropriate for a
 * prototype. Swapping providers later means changing only this file.
 *
 * Nominatim's usage policy asks for a descriptive User-Agent/Referer,
 * which browsers set automatically, and reasonable request volume — this
 * service is called only on explicit user search, not on every keystroke.
 */

const NOMINATIM_ENDPOINT = 'https://nominatim.openstreetmap.org/search'

interface NominatimResult {
  place_id: number
  display_name: string
  lat: string
  lon: string
  boundingbox: [string, string, string, string] // [south, north, west, east]
  type?: string
  addresstype?: string
}

export class LocationServiceError extends Error {
  cause: 'network' | 'invalid-response' | 'unknown'

  constructor(message: string, cause: 'network' | 'invalid-response' | 'unknown') {
    super(message)
    this.name = 'LocationServiceError'
    this.cause = cause
  }
}

function toSearchResult(raw: NominatimResult): LocationSearchResult {
  const [south, north, west, east] = raw.boundingbox.map(Number)
  const parts = raw.display_name.split(',').map((p) => p.trim())
  return {
    id: String(raw.place_id),
    label: parts[0] ?? raw.display_name,
    context: parts.slice(1).join(', ') || undefined,
    latitude: Number(raw.lat),
    longitude: Number(raw.lon),
    bbox: [south, west, north, east],
  }
}

/** Searches for a place by name, region, country, or free-text query. */
export async function searchLocations(query: string): Promise<LocationSearchResult[]> {
  const trimmed = query.trim()
  if (!trimmed) return []

  const url = new URL(NOMINATIM_ENDPOINT)
  url.searchParams.set('q', trimmed)
  url.searchParams.set('format', 'jsonv2')
  url.searchParams.set('limit', '6')
  url.searchParams.set('addressdetails', '0')

  let response: Response
  try {
    response = await fetch(url.toString(), {
      headers: { Accept: 'application/json' },
    })
  } catch {
    throw new LocationServiceError('Could not reach the location search service.', 'network')
  }

  if (!response.ok) {
    throw new LocationServiceError(`Location search failed (${response.status}).`, 'invalid-response')
  }

  let data: unknown
  try {
    data = await response.json()
  } catch {
    throw new LocationServiceError('Location search returned an unreadable response.', 'invalid-response')
  }

  if (!Array.isArray(data)) {
    throw new LocationServiceError('Location search returned an unexpected format.', 'invalid-response')
  }

  return (data as NominatimResult[]).map(toSearchResult)
}

/** Validates a free-typed latitude/longitude pair. Returns an error message, or null if valid. */
export function validateCoordinates(latRaw: string, lngRaw: string): string | null {
  if (!latRaw.trim() || !lngRaw.trim()) return 'Enter both latitude and longitude.'

  const lat = Number(latRaw)
  const lng = Number(lngRaw)

  if (Number.isNaN(lat) || Number.isNaN(lng)) return 'Coordinates must be numbers.'
  if (lat < -90 || lat > 90) return 'Latitude must be between -90 and 90.'
  if (lng < -180 || lng > 180) return 'Longitude must be between -180 and 180.'

  return null
}

/** Reverse-formats a manually entered coordinate pair into a LocationSearchResult-shaped object. */
export function coordinatesToResult(lat: number, lng: number): LocationSearchResult {
  return {
    id: `manual-${lat}-${lng}`,
    label: `${lat.toFixed(4)}, ${lng.toFixed(4)}`,
    context: 'Manually entered coordinates',
    latitude: lat,
    longitude: lng,
  }
}
