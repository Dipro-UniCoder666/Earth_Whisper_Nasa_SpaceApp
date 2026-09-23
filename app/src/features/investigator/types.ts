/**
 * Types for the AI Investigator feature. This layer explains evidence
 * that has already been measured — it does not generate or invent
 * scientific findings. Implemented starting in a later prompt.
 */

export interface InvestigatorQuestion {
  question: string
  /** The evidence-grounded answer, once the engine exists. */
  answer?: string
}

export type InvestigatorTone = 'child-friendly' | 'scientific'
