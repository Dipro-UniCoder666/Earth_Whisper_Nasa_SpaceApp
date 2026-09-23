import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { CandidateAnomaly, LocationSearchResult, NisarObservation } from '@/features/investigation/types'
import {
  findCandidatesNear,
  getObservationsForCandidate,
} from '@/features/investigation/services/nisarService'
import {
  coordinatesToResult,
  validateCoordinates,
} from '@/features/investigation/services/locationService'

export interface InvestigationState {
  selectedLocation: LocationSearchResult | null
  manualLat: string
  manualLng: string
  manualError: string | null
  candidates: CandidateAnomaly[]
  selectedCandidateId: string | undefined
  observations: NisarObservation[]
  selectedObservationId: string | undefined
  loadingPhase: 'idle' | 'searching-candidates' | 'loading-observations' | 'ready'
  errorMessage: string | null
  scienceMode: boolean
}

export interface InvestigationDerived {
  selectedCandidate: CandidateAnomaly | undefined
  mapCenter: { lat: number; lng: number } | null
  hasActiveInvestigation: boolean
  canContinue: boolean
  activeStep: 1 | 2 | 3 | 4 | 5
}

export interface InvestigationActions {
  selectLocation: (result: LocationSearchResult) => void
  setManualLat: (v: string) => void
  setManualLng: (v: string) => void
  submitManualCoordinates: () => void
  selectCandidate: (id: string) => void
  selectObservation: (id: string) => void
  loadSampleInvestigation: () => void
  setScienceMode: (v: boolean) => void
  reset: () => void
}

const INITIAL_STATE: Omit<InvestigationState, 'scienceMode'> = {
  selectedLocation: null,
  manualLat: '',
  manualLng: '',
  manualError: null,
  candidates: [],
  selectedCandidateId: undefined,
  observations: [],
  selectedObservationId: undefined,
  loadingPhase: 'idle',
  errorMessage: null,
}

export function useInvestigationState(
  initialScienceMode = false,
): InvestigationState & InvestigationActions & InvestigationDerived {
  const [state, setState] = useState<Omit<InvestigationState, 'scienceMode'>>({ ...INITIAL_STATE })
  const [scienceMode, setScienceModeState] = useState(initialScienceMode)
  const requestIdRef = useRef(0)

  // Sync scienceMode from external prop changes
  useEffect(() => {
    setScienceModeState(initialScienceMode)
  }, [initialScienceMode])

  const selectLocation = useCallback((result: LocationSearchResult) => {
    const thisId = ++requestIdRef.current
    setState((s) => ({
      ...s,
      selectedLocation: result,
      candidates: [],
      selectedCandidateId: undefined,
      observations: [],
      selectedObservationId: undefined,
      loadingPhase: 'searching-candidates',
      errorMessage: null,
    }))
    findCandidatesNear(result.latitude, result.longitude)
      .then((found) => {
        if (requestIdRef.current !== thisId) return
        setState((s) => ({ ...s, candidates: found, loadingPhase: 'ready' }))
      })
      .catch(() => {
        if (requestIdRef.current !== thisId) return
        setState((s) => ({
          ...s,
          loadingPhase: 'ready',
          errorMessage: 'Could not load observation data. Check your connection and try again.',
        }))
      })
  }, [])

  const selectCandidate = useCallback(
    (id: string) => {
      setState((s) => ({
        ...s,
        selectedCandidateId: id,
        observations: [],
        selectedObservationId: undefined,
        loadingPhase: 'loading-observations',
      }))
      const candidate = state.candidates.find((c) => c.id === id)
      if (!candidate) {
        setState((s) => ({ ...s, loadingPhase: 'ready' }))
        return
      }
      const thisId = ++requestIdRef.current
      getObservationsForCandidate(candidate).then((obs) => {
        if (requestIdRef.current !== thisId) return
        setState((s) => ({ ...s, observations: obs, loadingPhase: 'ready' }))
      })
    },
    [state.candidates],
  )

  const selectObservation = useCallback((id: string) => {
    setState((s) => ({ ...s, selectedObservationId: id }))
  }, [])

  const setManualLat = useCallback((v: string) => {
    setState((s) => ({ ...s, manualLat: v, manualError: null }))
  }, [])

  const setManualLng = useCallback((v: string) => {
    setState((s) => ({ ...s, manualLng: v, manualError: null }))
  }, [])

  const submitManualCoordinates = useCallback(() => {
    const error = validateCoordinates(state.manualLat, state.manualLng)
    if (error) {
      setState((s) => ({ ...s, manualError: error }))
      return
    }
    const result = coordinatesToResult(Number(state.manualLat), Number(state.manualLng))
    selectLocation(result)
  }, [state.manualLat, state.manualLng, selectLocation])

  const loadSampleInvestigation = useCallback(() => {
    const sampleLocation: LocationSearchResult = {
      id: 'sample-candidate-001',
      label: 'Monda, Uttarakhand, India',
      context: 'NISAR Candidate #1 analysis site',
      latitude: 31.1105,
      longitude: 77.9373,
    }
    const thisId = ++requestIdRef.current
    setState((s) => ({
      ...s,
      selectedLocation: sampleLocation,
      candidates: [],
      selectedCandidateId: undefined,
      observations: [],
      selectedObservationId: undefined,
      loadingPhase: 'searching-candidates',
      errorMessage: null,
    }))
    findCandidatesNear(sampleLocation.latitude, sampleLocation.longitude).then((found) => {
      if (requestIdRef.current !== thisId) return
      const sampleCandidate = found.find((c) => c.id === 'candidate-001') ?? found[0]
      setState((s) => ({
        ...s,
        candidates: found,
        loadingPhase: sampleCandidate ? 'loading-observations' : 'ready',
        selectedCandidateId: sampleCandidate?.id,
      }))
      if (sampleCandidate) {
        getObservationsForCandidate(sampleCandidate).then((obs) => {
          if (requestIdRef.current !== thisId) return
          setState((s) => ({ ...s, observations: obs, loadingPhase: 'ready' }))
        })
      }
    })
  }, [])

  const setScienceMode = useCallback((v: boolean) => {
    setScienceModeState(v)
  }, [])

  const reset = useCallback(() => {
    requestIdRef.current++
    setState({ ...INITIAL_STATE })
  }, [])

  const derived = useMemo<InvestigationDerived>(() => {
    const selectedCandidate = state.candidates.find((c) => c.id === state.selectedCandidateId)
    const mapCenter = state.selectedLocation
      ? { lat: state.selectedLocation.latitude, lng: state.selectedLocation.longitude }
      : null
    const hasActiveInvestigation = Boolean(state.selectedCandidateId)
    const canContinue = Boolean(state.selectedCandidateId)
    let activeStep: 1 | 2 | 3 | 4 | 5 = 1
    if (state.selectedLocation && !state.selectedCandidateId) activeStep = 2
    else if (state.selectedCandidateId) activeStep = 3
    return { selectedCandidate, mapCenter, hasActiveInvestigation, canContinue, activeStep }
  }, [state.selectedLocation, state.selectedCandidateId, state.candidates])

  return {
    ...state,
    scienceMode,
    ...derived,
    selectLocation,
    setManualLat,
    setManualLng,
    submitManualCoordinates,
    selectCandidate,
    selectObservation,
    loadSampleInvestigation,
    setScienceMode,
    reset,
  }
}
