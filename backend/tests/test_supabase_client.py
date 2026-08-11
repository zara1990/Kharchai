import os
import unittest
from unittest.mock import patch

import httpx

from services.supabase_client import (
    SupabaseClient,
    SupabaseConfigurationError,
)


class SupabaseClientTests(unittest.TestCase):
    def test_missing_url_fails_with_clear_configuration_error(self):
        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "", "SUPABASE_SERVICE_ROLE_KEY": "server-key"},
            clear=False,
        ):
            with self.assertRaisesRegex(
                SupabaseConfigurationError, "SUPABASE_URL is not configured"
            ):
                SupabaseClient.from_environment()

    def test_missing_service_role_key_fails_with_clear_configuration_error(self):
        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "https://example.supabase.co", "SUPABASE_SERVICE_ROLE_KEY": ""},
            clear=False,
        ):
            with self.assertRaisesRegex(
                SupabaseConfigurationError,
                "SUPABASE_SERVICE_ROLE_KEY is not configured",
            ):
                SupabaseClient.from_environment()

    def test_initializes_and_verifies_without_exposing_key(self):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.headers["apikey"] == "server-key"
            assert request.headers["authorization"] == "Bearer server-key"
            return httpx.Response(200, json=[])

        http_client = httpx.Client(
            base_url="https://example.supabase.co",
            transport=httpx.MockTransport(handler),
        )
        client = SupabaseClient(
            url="https://example.supabase.co",
            service_role_key="server-key",
            http_client=http_client,
        )

        result = client.verify_connection()

        self.assertTrue(result.reachable)
        self.assertTrue(result.schema_ready)
        self.assertNotIn("server-key", result.message)
        client.close()

    def test_missing_initial_table_is_reachable_but_not_schema_ready(self):
        http_client = httpx.Client(
            base_url="https://example.supabase.co",
            transport=httpx.MockTransport(
                lambda request: httpx.Response(404, json={"message": "not found"})
            ),
        )
        client = SupabaseClient(
            url="https://example.supabase.co",
            service_role_key="server-key",
            http_client=http_client,
        )

        result = client.verify_connection()

        self.assertTrue(result.reachable)
        self.assertFalse(result.schema_ready)
        self.assertIn("financial_records", result.message)
        client.close()


if __name__ == "__main__":
    unittest.main()