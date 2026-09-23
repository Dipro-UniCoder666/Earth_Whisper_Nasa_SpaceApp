export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(' ')
}

/** Formats a decimal-degree coordinate with a compass suffix, e.g. 31.1105 -> "31.1105° N" */
export function formatCoordinate(value: number, axis: 'lat' | 'lng'): string {
  const suffix = axis === 'lat' ? (value >= 0 ? 'N' : 'S') : value >= 0 ? 'E' : 'W'
  return `${Math.abs(value).toFixed(4)}° ${suffix}`
}
