# ADR-0005: Add an EasyPaisa/JazzCash Wallet Screenshot Parser

- **Status:** Accepted
- **Date:** 2026-08-04

## Context

KharchAI already supports receipt and Pakistani utility-bill extraction through
the shared financial-document pipeline. The next MVP document type is a mobile
wallet transaction screenshot, focused on EasyPaisa and JazzCash.

Wallet screenshots have a different shape from receipts: a transaction can be
represented by one amount and may include a wallet name, transaction type,
counterparty, timestamp, and reference identifier rather than line items.
Missing values must remain explicitly unknown instead of being inferred.

The existing receipt and utility parsers and the public
`ReceiptUploadResponse` contract must remain backward compatible.

## Decision

Add a dedicated `WalletParser` using the existing OpenAI Vision client pattern
and a file-backed prompt. Its strongly typed output contains:

- `wallet_name`
- `transaction_type`
- `amount`
- `currency`
- `counterparty`
- `transaction_date`
- `transaction_time`
- `transaction_reference`

Every extracted field is nullable. The parser returns an error response with
null extraction fields when the OpenAI key is unavailable or the model returns
invalid JSON.

Register the parser under `wallet_screenshot` in `ParserRegistry`. The
classifier routes portrait, saturated, UI-like screenshots to this document
type using the current deterministic MVP heuristic.

## UFR mapping

Wallet output is mapped into the existing `UniversalFinancialRecord`:

```text
document_type  → wallet_screenshot
merchant       → wallet_name
document_date  → transaction_date
currency       → currency
total_amount   → amount
category       → wallet
items[0]       → transaction amount and type
item.metadata  → counterparty, time, reference, and wallet fields
```

No new financial-record format is introduced. Wallet-specific fields that do
not have dedicated UFR columns are retained in item metadata.

The public upload response remains the existing receipt-shaped schema. A wallet
transaction is projected into that response as a merchant/date/amount summary,
with an optional single item when an amount is available.

## Consequences

### Positive

- EasyPaisa and JazzCash screenshots use the shared pipeline and UFR.
- Missing fields are represented as `null` and do not fail parsing.
- Existing receipt and utility behavior remains unchanged.
- Future wallet providers can share the same schema and parser boundary.

### Limitations

- Classifier routing is heuristic and does not perform OCR in this MVP.
- The parser does not infer transaction direction or missing dates.
- Live screenshot extraction requires the configured OpenAI integration.