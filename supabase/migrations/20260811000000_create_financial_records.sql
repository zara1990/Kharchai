-- KharchAI Supabase foundation
-- Canonical persistence shape for UniversalFinancialRecord.
--
-- Apply this migration in the Supabase SQL editor or migration tooling.
-- The application does not run migrations automatically.

create table if not exists public.financial_records (
    id text primary key,
    document_type text not null,
    source text not null,
    transaction_date text,
    merchant_provider text,
    amount numeric(14, 2),
    currency text,
    category text,
    payment_method text,
    items jsonb not null default '[]'::jsonb,
    metadata jsonb not null default '{}'::jsonb,
    confidence numeric(5, 4),
    parser_version text not null,
    created_at timestamptz not null default timezone('utc', now()),
    updated_at timestamptz not null default timezone('utc', now()),

    constraint financial_records_document_type_not_blank
        check (length(trim(document_type)) > 0),
    constraint financial_records_source_not_blank
        check (length(trim(source)) > 0),
    constraint financial_records_parser_version_not_blank
        check (length(trim(parser_version)) > 0),
    constraint financial_records_confidence_range
        check (confidence is null or (confidence >= 0 and confidence <= 1)),
    constraint financial_records_items_object
        check (jsonb_typeof(items) = 'array'),
    constraint financial_records_metadata_object
        check (jsonb_typeof(metadata) = 'object')
);

create index if not exists financial_records_document_type_idx
    on public.financial_records (document_type);

create index if not exists financial_records_transaction_date_idx
    on public.financial_records (transaction_date);

comment on table public.financial_records is
    'Canonical persisted UniversalFinancialRecord for financial documents.';
comment on column public.financial_records.id is
    'UFR record_id; kept as text to preserve the existing UFR contract.';
comment on column public.financial_records.transaction_date is
    'UFR document_date; text preserves parser output until date normalization is formalized.';
comment on column public.financial_records.merchant_provider is
    'UFR merchant; provider names for utility bills use the same column.';
comment on column public.financial_records.items is
    'Normalized UFR item list stored as JSONB.';
comment on column public.financial_records.metadata is
    'Structured document-specific and processing metadata stored as JSONB.';