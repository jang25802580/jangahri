export type HealthStatus = 'healthy' | 'degraded';

export interface HealthChecks {
  storage: string;
  cosmos: string;
  gemini: string;
}

export interface HealthResponse {
  status: HealthStatus;
  checks: HealthChecks;
}
