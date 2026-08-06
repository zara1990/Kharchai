import { UniversalFinancialRecord } from '../types/ufr';
import { mockUFR } from '../mocks/mockUFR';

export async function uploadDocument(
  imageUris: string[],
): Promise<UniversalFinancialRecord> {
  // imageUris will be sent to the backend in a future milestone
  void imageUris;

  return mockUFR;
}
