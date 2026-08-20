import type { ResearchResult } from "@/lib/research-result";

export type ResearchResultRequest = {
  resultType: string;
  season?: string;
  competition?: string;
  asOf?: string;
  entity?: {
    kind: "fixture" | "team" | "player";
    season?: string;
    id?: string;
  };
  filters?: Record<string, string | number | boolean | string[]>;
};

/**
 * Frontend boundary only.
 *
 * Production implementations must call the authoritative Python research/query
 * API. They must not recreate query, identity, provenance or historical-state
 * logic in the browser.
 */
export type ResearchApi = {
  getResearchResult<T>(request: ResearchResultRequest): Promise<ResearchResult<T>>;
};
