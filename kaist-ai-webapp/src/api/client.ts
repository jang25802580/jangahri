import { apiBaseUrl, apiKey } from '../config/env';

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export async function apiFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const url = `${apiBaseUrl}${path}`;

  const headers = new Headers(init?.headers);
  if (apiKey) {
    headers.set('x-functions-key', apiKey);
  }

  const response = await fetch(url, { ...init, headers });

  if (!response.ok) {
    throw new ApiError(response.status, `API error: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}
