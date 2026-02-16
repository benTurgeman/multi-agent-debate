/**
 * API client configuration
 */

// Base API URL - defaults to backend running on localhost:8000
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// WebSocket URL
export const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000';

/**
 * Format FastAPI validation error for display
 */
function formatValidationError(detail: unknown): string {
  // FastAPI validation errors are arrays of error objects
  if (Array.isArray(detail)) {
    return detail
      .map((err) => {
        const location = err.loc?.slice(1).join('.') || 'unknown field';
        return `${location}: ${err.msg}`;
      })
      .join('; ');
  }

  // Single string error
  if (typeof detail === 'string') {
    return detail;
  }

  // Object with message property
  if (detail && typeof detail === 'object' && 'message' in detail) {
    return String(detail.message);
  }

  return 'Validation error occurred';
}

/**
 * Base fetch wrapper with error handling
 */
export async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        detail: response.statusText,
      }));

      const errorMessage = formatValidationError(errorData.detail);
      throw new Error(errorMessage || `HTTP ${response.status}`);
    }

    return response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Unknown error occurred');
  }
}
