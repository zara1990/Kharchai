import { UniversalFinancialRecord } from '../types/ufr';
import { mockUFR } from '../mocks/mockUFR';
import { API_BASE_URL } from '../config/api';

export async function uploadDocument(
  imageUris: string[],
): Promise<UniversalFinancialRecord> {
  // imageUris will be sent to the backend in a future milestone
  void imageUris;

  return mockUFR;
}

// ── Save payload types ────────────────────────────────────────────────────────

export interface ReviewHintPayload {
  field: string;
  message: string;
}

export interface UFRItemPayload {
  description: string;
  amount: number | null;
  quantity: number | null;
  unit_price: number | null;
  category: string | null;
  metadata: Record<string, unknown>;
}

export interface UFRMetadataPayload {
  source: string;
  confidence: number | null;
  confidence_level: string | null;
  review_required: boolean | null;
  review_hints: ReviewHintPayload[];
  quality_score: number | null;
  parser_version: string;
}

export interface SaveRecordPayload {
  record_id: string;
  document_type: string;
  merchant: string | null;
  document_date: string | null;
  currency: string | null;
  total_amount: number | null;
  payment_method: null;
  category: null;
  items: UFRItemPayload[];
  metadata: UFRMetadataPayload;
}

export interface SaveRecordResponse {
  saved: boolean;
  record_id: string;
  document_type: string;
}

export class SaveError extends Error {
  constructor(
    public readonly status: number,
    public readonly body: unknown,
  ) {
    super(`Save failed with HTTP ${status}`);
  }
}

/**
 * POST the reviewed UFR payload to the backend save endpoint.
 *
 * Throws SaveError on non-2xx responses.
 * Throws a plain Error on network/timeout failures.
 * Never contacts Supabase or OpenAI directly.
 */
export async function saveFinancialRecord(
  payload: SaveRecordPayload,
): Promise<SaveRecordResponse> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}/api/v1/financial-records`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  } catch (networkError) {
    throw new Error('Could not reach the server. Check your connection and try again.');
  }

  let body: unknown;
  try {
    body = await response.json();
  } catch {
    body = null;
  }

  if (!response.ok) {
    throw new SaveError(response.status, body);
  }

  return body as SaveRecordResponse;
}
