export interface UFRItem {
  name: string;
  amount: string;
}

export interface UniversalFinancialRecord {
  documentType: string;
  merchant: string;
  date: string;
  total: string;
  items: UFRItem[];
  confidence: string;
  reviewHints: string[];
  serviceCharge?: string;
  taxAmount?: string;
  deliveryCharge?: string;
  discountAmount?: string;
  subtotalAmount?: string;
}
