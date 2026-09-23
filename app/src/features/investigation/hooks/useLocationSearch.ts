import { useCallback, useEffect, useRef, useState } from 'react'
import type { LocationSearchState } from '@/features/investigation/types'
import { searchLocations, LocationServiceError } from '@/features/investigation/services/locationService'

const DEBOUNCE_MS = 400
const MIN_QUERY_LENGTH = 2

/**
 * Manages debounced location search state (loading / success / no-results /
 * error) for a free-text query. Cancels stale requests so a fast typist
 * never sees an older response overwrite a newer one.
 */
export function useLocationSearch() {
  const [query, setQuery] = useState('')
  const [state, setState] = useState<LocationSearchState>({ status: 'idle' })
  const requestIdRef = useRef(0)

  useEffect(() => {
    const trimmed = query.trim()

    if (trimmed.length < MIN_QUERY_LENGTH) {
      setState({ status: 'idle' })
      return
    }

    const thisRequestId = ++requestIdRef.current
    setState({ status: 'loading' })

    const timeout = setTimeout(async () => {
      try {
        const results = await searchLocations(trimmed)
        if (requestIdRef.current !== thisRequestId) return // stale response, ignore

        setState(results.length > 0 ? { status: 'success', results } : { status: 'no-results' })
      } catch (err) {
        if (requestIdRef.current !== thisRequestId) return

        const message =
          err instanceof LocationServiceError
            ? err.message
            : 'Something went wrong while searching. Please try again.'
        setState({ status: 'error', message })
      }
    }, DEBOUNCE_MS)

    return () => clearTimeout(timeout)
  }, [query])

  const reset = useCallback(() => {
    setQuery('')
    setState({ status: 'idle' })
  }, [])

  return { query, setQuery, state, reset }
}
