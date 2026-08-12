from __future__ import annotations

import unittest
from typing import Any

from fastapi.testclient import TestClient

from main import app
from schemas.ufr import (
    UniversalFinancialRecord,
    UniversalFinancialRecordItem,
    UniversalFinancialRecordMetadata,
)
from routes.financial_records import get_financial_record_persistence_service
from services.financial_record_persistence import FinancialRecordPersistenceService
from services.supabase_client import (
    SupabaseClient,
    SupabaseConflictError,
    SupabaseConnectionError,
)


class FakeSupabaseClient:
    """In-memory insert spy; no test writes to Supabase."""

    def __init__(self, error: Exception | None = None) -> None:
        self.payloads: list[dict[str, Any]] = []
        self.error = error

    def insert_financial_record(self, payload: dict[str, Any]) -> None:
        if self.error is not None:
            raise self.error
        self.payloads.append(payload)


def make_record(
    *,
    record_id: str = "record-1",
    document_type: str = "receipt",
    source: str = "receipt_analysis",
    merchant: str = "Karachi Grocers",
    total_amount: float = 450.50,
    category: str = "groceries",
    items: list[UniversalFinancialRecordItem] | None = None,
) -> UniversalFinancialRecord:
    if items is None:
        items = [
            UniversalFinancialRecordItem(
                description="Rice",
                amount=300.00,
                quantity=1,
                unit_price=300.00,
                category="groceries",
            ),
            UniversalFinancialRecordItem(
                description="Tea",
                amount=150.50,
                quantity=1,
                unit_price=150.50,
                category="groceries",
            ),
        ]

    return UniversalFinancialRecord(
        record_id=record_id,
        document_type=document_type,
        merchant=merchant,
        document_date="2026-08-12",
        currency="PKR",
        total_amount=total_amount,
        payment_method=None,
        category=category,
        items=items,
        metadata=UniversalFinancialRecordMetadata(
            source=source,
            confidence=0.9,
            confidence_level="high",
            review_required=False,
            parser_version="test-parser-v1",
        ),
    )


class FinancialRecordEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = FakeSupabaseClient()
        self.persistence = FinancialRecordPersistenceService(
            client=self.client,  # type: ignore[arg-type]
        )
        app.dependency_overrides[
            get_financial_record_persistence_service
        ] = lambda: self.persistence
        self.http = TestClient(app)

    def tearDown(self) -> None:
        self.http.close()
        app.dependency_overrides.clear()

    def post_record(self, record: UniversalFinancialRecord):
        return self.http.post(
            "/api/v1/financial-records",
            json=record.model_dump(mode="json"),
        )

    def test_valid_receipt_ufr_saves_successfully(self):
        response = self.post_record(make_record())

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "saved": True,
                "record_id": "record-1",
                "document_type": "receipt",
            },
        )
        self.assertEqual(self.client.payloads[0]["id"], "record-1")
        self.assertEqual(self.client.payloads[0]["source"], "receipt_analysis")
        self.assertEqual(self.client.payloads[0]["amount"], 450.5)
        self.assertEqual(len(self.client.payloads[0]["items"]), 2)

    def test_valid_utility_bill_ufr_saves_successfully(self):
        record = make_record(
            record_id="utility-1",
            document_type="utility_bill",
            source="utility_bill_analysis",
            merchant="K-Electric",
            total_amount=2750.0,
            category="utilities",
            items=[
                UniversalFinancialRecordItem(
                    description="Electricity bill",
                    amount=2750.0,
                    category="utilities",
                    metadata={"consumer_number": "consumer-1"},
                )
            ],
        )

        response = self.post_record(record)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["document_type"], "utility_bill")
        self.assertEqual(self.client.payloads[0]["merchant_provider"], "K-Electric")
        self.assertEqual(self.client.payloads[0]["category"], "utilities")

    def test_valid_wallet_screenshot_ufr_saves_successfully(self):
        record = make_record(
            record_id="wallet-1",
            document_type="wallet_screenshot",
            source="wallet_analysis",
            merchant="Easypaisa",
            total_amount=1200.0,
            items=[
                UniversalFinancialRecordItem(
                    description="Money sent",
                    amount=1200.0,
                    category="wallet",
                    metadata={
                        "wallet_name": "Easypaisa",
                        "transaction_type": "debit",
                    },
                )
            ],
        )

        response = self.post_record(record)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["document_type"], "wallet_screenshot")
        self.assertEqual(self.client.payloads[0]["source"], "wallet_analysis")
        self.assertEqual(self.client.payloads[0]["items"][0]["category"], "wallet")

    def test_invalid_malformed_ufr_is_rejected(self):
        response = self.http.post(
            "/api/v1/financial-records",
            json={
                "record_id": "invalid-1",
                "document_type": "receipt",
                "items": [],
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(self.client.payloads, [])

    def test_inconsistent_reviewed_total_is_rejected(self):
        record = make_record(total_amount=9999.0)

        response = self.post_record(record)

        self.assertEqual(response.status_code, 422)
        self.assertIn("does not reconcile", response.json()["detail"]["errors"][0])
        self.assertEqual(self.client.payloads, [])

    def test_duplicate_record_id_is_handled_safely(self):
        self.client.error = SupabaseConflictError(
            "Supabase rejected the insert because the record already exists."
        )

        response = self.post_record(make_record(record_id="duplicate-1"))

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.json()["detail"],
            {
                "error": "Financial record already exists",
                "record_id": "duplicate-1",
            },
        )

    def test_supabase_failure_produces_controlled_api_error(self):
        self.client.error = SupabaseConnectionError("simulated database failure")

        response = self.post_record(make_record(record_id="database-failure-1"))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json()["detail"],
            {"error": "Financial record persistence is unavailable."},
        )


class SupabaseInsertTests(unittest.TestCase):
    def test_supabase_client_maps_http_409_to_conflict(self):
        import httpx

        http_client = httpx.Client(
            base_url="https://example.supabase.co",
            transport=httpx.MockTransport(
                lambda request: httpx.Response(409, json={"code": "23505"})
            ),
        )
        client = SupabaseClient(
            url="https://example.supabase.co",
            service_role_key="server-key",
            http_client=http_client,
        )

        with self.assertRaises(SupabaseConflictError):
            client.insert_financial_record({"id": "duplicate-1"})

        client.close()


if __name__ == "__main__":
    unittest.main()