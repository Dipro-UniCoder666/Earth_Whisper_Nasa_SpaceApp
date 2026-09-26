import { useCallback, useEffect, useRef, useState } from 'react'
import type {
  InvestigationAdapter,
  InvestigationData,
  InvestigationLifecycle,
  InvestigationLifecycleStatus,
} from '@/features/investigation/models/investigationModel'

interface UseInvestigationLifecycleOptions {
  minimumDurationMs?: number
}

interface InvestigationLifecycleController<TData extends InvestigationData> {
  lifecycle: InvestigationLifecycle<TData>
  progress: number
  start: () => void
  reset: () => void
}

const DEFAULT_MINIMUM_DURATION_MS = 4000

function wait(durationMs: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, durationMs))
}

/**
 * Shared lifecycle for site-specific investigation adapters.
 *
 * The adapter owns data access. This hook only coordinates loading, the
 * minimum presentation duration, progress, completion, and cancellation.
 */
export function useInvestigationLifecycle<TData extends InvestigationData>(
  adapter: InvestigationAdapter<TData>,
  options: UseInvestigationLifecycleOptions = {},
): InvestigationLifecycleController<TData> {
  const minimumDurationMs = options.minimumDurationMs ?? DEFAULT_MINIMUM_DURATION_MS
  const [lifecycle, setLifecycle] = useState<InvestigationLifecycle<TData>>({
    status: 'idle',
    data: null,
    error: null,
  })
  const [progress, setProgress] = useState(0)
  const requestIdRef = useRef(0)

  useEffect(() => {
    if (lifecycle.status !== 'scanning') return

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setProgress(1)
      return
    }

    const progressTimer = window.setInterval(() => {
      setProgress((value) => Math.min(1, value + 0.01375))
    }, 55)

    return () => window.clearInterval(progressTimer)
  }, [lifecycle.status])

  const start = useCallback(() => {
    const requestId = ++requestIdRef.current
    setProgress(0)
    setLifecycle({ status: 'scanning', data: null, error: null })

    const loadStartedAt = Date.now()
    adapter.load()
      .then((data) => {
        if (requestIdRef.current !== requestId) return
        setLifecycle({ status: 'scanning', data, error: null })

        const remainingDuration = Math.max(0, minimumDurationMs - (Date.now() - loadStartedAt))
        return wait(remainingDuration).then(() => {
          if (requestIdRef.current !== requestId) return
          setProgress(1)
          setLifecycle({ status: 'ready', data, error: null })
        })
      })
      .catch((error: unknown) => {
        if (requestIdRef.current !== requestId) return
        setLifecycle({
          status: 'error',
          data: null,
          error: error instanceof Error ? error.message : 'Investigation data could not be loaded.',
        })
      })
  }, [adapter, minimumDurationMs])

  const reset = useCallback(() => {
    requestIdRef.current += 1
    setProgress(0)
    setLifecycle({ status: 'idle', data: null, error: null })
  }, [])

  return { lifecycle, progress, start, reset }
}

export type { InvestigationLifecycleStatus }
