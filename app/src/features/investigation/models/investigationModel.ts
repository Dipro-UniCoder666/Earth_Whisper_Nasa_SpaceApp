import type { CandidateDetail, CandidateListResponse, InvestigationSourceStatus } from '@/features/candidates/types'
import type { InvestigationSite } from '@/features/investigation/data/investigationSite'

/**
 * Site-specific verified data carried by the shared investigation lifecycle.
 *
 * The union is deliberately discriminated: Monda is not represented as a
 * Sandhya candidate, and each site keeps its native evidence contract.
 */
export type InvestigationData =
  | {
      kind: 'sandhya-candidate'
      candidate: CandidateDetail
      payload: CandidateListResponse
    }
  | {
      kind: 'monda-site'
      site: InvestigationSite
      sourceStatus: InvestigationSourceStatus
    }

export type InvestigationLifecycleStatus = 'idle' | 'scanning' | 'ready' | 'error'

export interface InvestigationLifecycle<TData extends InvestigationData = InvestigationData> {
  status: InvestigationLifecycleStatus
  data: TData | null
  error: string | null
}

/** A small data-loading boundary for site-specific investigation sources. */
export interface InvestigationAdapter<TData extends InvestigationData> {
  load: () => Promise<TData>
}
