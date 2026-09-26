import { MONDA_INVESTIGATION } from '@/features/investigation/data/investigationSite'
import type { InvestigationAdapter, InvestigationData } from '@/features/investigation/models/investigationModel'

export type MondaInvestigationData = Extract<InvestigationData, { kind: 'monda-site' }>

/**
 * Exposes the existing Monda investigation through the shared adapter
 * boundary. No measurements are copied, recalculated, or transformed.
 */
export const mondaInvestigationAdapter: InvestigationAdapter<MondaInvestigationData> = {
  async load() {
    return {
      kind: 'monda-site',
      site: MONDA_INVESTIGATION,
    }
  },
}
