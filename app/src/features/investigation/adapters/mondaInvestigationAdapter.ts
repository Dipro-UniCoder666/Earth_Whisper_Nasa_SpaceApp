import { MONDA_INVESTIGATION } from '@/features/investigation/data/investigationSite'
import { requestInvestigation } from '@/features/candidates/services/candidateService'
import type { InvestigationAdapter, InvestigationData } from '@/features/investigation/models/investigationModel'

export type MondaInvestigationData = Extract<InvestigationData, { kind: 'monda-site' }>

/**
 * Exposes the existing Monda investigation through the shared adapter
 * boundary. No measurements are copied, recalculated, or transformed.
 */
export const mondaInvestigationAdapter: InvestigationAdapter<MondaInvestigationData> = {
  async load() {
    try {
      const response = await requestInvestigation(MONDA_INVESTIGATION.id, MONDA_INVESTIGATION.coords.lat, MONDA_INVESTIGATION.coords.lng)
      if (response.result.site) return { kind: 'monda-site', site: response.result.site, sourceStatus: response.source_status }
    } catch {
      // Preserve the existing local Monda fallback when the API is unavailable.
    }
    return {
      kind: 'monda-site',
      site: MONDA_INVESTIGATION,
      sourceStatus: 'VERIFIED_STATIC',
    }
  },
}
