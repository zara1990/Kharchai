import { UniversalFinancialRecord } from '../types/ufr';

/** Temporary mock data — will be replaced by API response in a future milestone. */
export const mockUFR: UniversalFinancialRecord = {
  documentType: 'Receipt',
  merchant: 'Imtiaz Super Market',
  date: '06 Aug 2026',
  total: 'PKR 2,450',
  items: [
    { name: 'Milk', amount: 'PKR 350' },
    { name: 'Bread', amount: 'PKR 180' },
    { name: 'Eggs', amount: 'PKR 420' },
  ],
  confidence: 'GOOD',
  reviewHints: [
    'Merchant detected successfully',
    'Please verify the total amount',
  ],
};
