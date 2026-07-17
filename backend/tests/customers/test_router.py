"""Integration tests for customers REST API router."""

import io
import uuid

import pytest
from httpx import AsyncClient

from app.main import app
from app.core.deps import get_current_user, get_current_tenant_id
from tests.customers.conftest import (
    TEST_TENANT_A_ID,
    TEST_TENANT_B_ID,
    TEST_USER_ID,
    _make_user_payload,
)


# ================================================================
# Auth / 401 Tests
# ================================================================


class TestUnauthenticated:
    """Tests for endpoints without authentication."""

    @pytest.mark.asyncio
    async def test_create_customer_without_token_returns_401(self, async_client: AsyncClient):
        response = await async_client.post("/api/v1/customers/", json={
            "first_name": "Test", "last_name": "User",
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_customers_without_token_returns_401(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/customers/")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_customer_without_token_returns_401(self, async_client: AsyncClient):
        response = await async_client.get(f"/api/v1/customers/{uuid.uuid4()}")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_customer_without_token_returns_401(self, async_client: AsyncClient):
        response = await async_client.patch(f"/api/v1/customers/{uuid.uuid4()}", json={"first_name": "X"})
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_customer_without_token_returns_401(self, async_client: AsyncClient):
        response = await async_client.delete(f"/api/v1/customers/{uuid.uuid4()}")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_history_without_token_returns_401(self, async_client: AsyncClient):
        response = await async_client.get(f"/api/v1/customers/{uuid.uuid4()}/history")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_add_note_without_token_returns_401(self, async_client: AsyncClient):
        response = await async_client.post(f"/api/v1/customers/{uuid.uuid4()}/notes", json={"content": "test"})
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_notes_without_token_returns_401(self, async_client: AsyncClient):
        response = await async_client.get(f"/api/v1/customers/{uuid.uuid4()}/notes")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_import_csv_without_token_returns_401(self, async_client: AsyncClient):
        response = await async_client.post("/api/v1/customers/import")
        assert response.status_code == 401


# ================================================================
# Create Customer Tests (POST /)
# ================================================================


class TestCreateCustomer:
    """Tests for POST /api/v1/customers/."""

    @pytest.mark.asyncio
    async def test_create_customer_success_returns_201(self, async_client: AsyncClient, override_auth_tenant_a):
        payload = {
            "first_name": "Ion",
            "last_name": "Popescu",
            "email": "ion.router@example.com",
            "phone": "+40722123456",
            "city": "Bucuresti",
            "country": "RO",
        }
        response = await async_client.post("/api/v1/customers/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Ion"
        assert data["last_name"] == "Popescu"
        assert data["email"] == "ion.router@example.com"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_customer_duplicate_email_returns_409(self, async_client: AsyncClient, override_auth_tenant_a):
        payload = {"first_name": "Dup", "last_name": "Email", "email": "dup.router@example.com"}
        r1 = await async_client.post("/api/v1/customers/", json=payload)
        assert r1.status_code == 201
        r2 = await async_client.post("/api/v1/customers/", json=payload)
        assert r2.status_code == 409

    @pytest.mark.asyncio
    async def test_create_customer_validation_error_returns_422(self, async_client: AsyncClient, override_auth_tenant_a):
        payload = {"first_name": "", "last_name": "User"}
        response = await async_client.post("/api/v1/customers/", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_customer_first_name_too_long_returns_422(self, async_client: AsyncClient, override_auth_tenant_a):
        payload = {"first_name": "A" * 101, "last_name": "User"}
        response = await async_client.post("/api/v1/customers/", json=payload)
        assert response.status_code == 422


# ================================================================
# List Customers Tests (GET /)
# ================================================================


class TestListCustomers:
    """Tests for GET /api/v1/customers/."""

    @pytest.mark.asyncio
    async def test_list_returns_paginated_response(self, async_client: AsyncClient, override_auth_tenant_a):
        response = await async_client.get("/api/v1/customers/")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "cursor" in data
        assert isinstance(data["data"], list)
        assert "has_more" in data["cursor"]
        assert "next" in data["cursor"]

    @pytest.mark.asyncio
    async def test_list_with_search_param(self, async_client: AsyncClient, override_auth_tenant_a):
        await async_client.post("/api/v1/customers/", json={
            "first_name": "Searchable", "last_name": "Unique", "email": "searchable@example.com",
        })
        response = await async_client.get("/api/v1/customers/?search=Searchable")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) >= 1
        assert data["data"][0]["first_name"] == "Searchable"

    @pytest.mark.asyncio
    async def test_list_with_sort_param(self, async_client: AsyncClient, override_auth_tenant_a):
        response = await async_client.get("/api/v1/customers/?sort_by=first_name&order=asc")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_invalid_order_returns_422(self, async_client: AsyncClient, override_auth_tenant_a):
        response = await async_client.get("/api/v1/customers/?order=invalid")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_limit_too_high_returns_422(self, async_client: AsyncClient, override_auth_tenant_a):
        response = await async_client.get("/api/v1/customers/?limit=101")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_is_active_filter(self, async_client: AsyncClient, override_auth_tenant_a):
        response = await async_client.get("/api/v1/customers/?is_active=true")
        assert response.status_code == 200
        data = response.json()
        for c in data["data"]:
            assert c["is_active"] is True


# ================================================================
# Get Customer Tests (GET /{id})
# ================================================================


class TestGetCustomer:
    """Tests for GET /api/v1/customers/{id}."""

    @pytest.mark.asyncio
    async def test_get_existing_customer_returns_200(self, async_client: AsyncClient, override_auth_tenant_a):
        create_resp = await async_client.post("/api/v1/customers/", json={
            "first_name": "Get", "last_name": "Me", "email": "get.me@example.com",
        })
        customer_id = create_resp.json()["id"]

        response = await async_client.get(f"/api/v1/customers/{customer_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == customer_id
        assert data["first_name"] == "Get"
        assert data["email"] == "get.me@example.com"

    @pytest.mark.asyncio
    async def test_get_nonexistent_customer_returns_404(self, async_client: AsyncClient, override_auth_tenant_a):
        fake_id = str(uuid.uuid4())
        response = await async_client.get(f"/api/v1/customers/{fake_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_invalid_uuid_returns_422(self, async_client: AsyncClient, override_auth_tenant_a):
        response = await async_client.get("/api/v1/customers/not-a-uuid")
        assert response.status_code == 422


# ================================================================
# Update Customer Tests (PATCH /{id})
# ================================================================


class TestUpdateCustomer:
    """Tests for PATCH /api/v1/customers/{id}."""

    @pytest.mark.asyncio
    async def test_update_partial_succeeds(self, async_client: AsyncClient, override_auth_tenant_a):
        create_resp = await async_client.post("/api/v1/customers/", json={
            "first_name": "Old", "last_name": "Name",
            "email": "old.patch@example.com", "phone": "+40700111111",
        })
        customer_id = create_resp.json()["id"]

        response = await async_client.patch(f"/api/v1/customers/{customer_id}", json={
            "first_name": "New", "phone": "+40700222222",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "New"
        assert data["last_name"] == "Name"
        assert data["phone"] == "+40700222222"

    @pytest.mark.asyncio
    async def test_update_nonexistent_returns_404(self, async_client: AsyncClient, override_auth_tenant_a):
        fake_id = str(uuid.uuid4())
        response = await async_client.patch(f"/api/v1/customers/{fake_id}", json={"first_name": "X"})
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_email_conflict_returns_409(self, async_client: AsyncClient, override_auth_tenant_a):
        r1 = await async_client.post("/api/v1/customers/", json={
            "first_name": "First", "last_name": "User", "email": "conflict1@example.com",
        })
        await async_client.post("/api/v1/customers/", json={
            "first_name": "Second", "last_name": "User", "email": "conflict2@example.com",
        })
        cid = r1.json()["id"]

        response = await async_client.patch(f"/api/v1/customers/{cid}", json={"email": "conflict2@example.com"})
        assert response.status_code == 409


# ================================================================
# Delete (Deactivate) Customer Tests (DELETE /{id})
# ================================================================


class TestDeleteCustomer:
    """Tests for DELETE /api/v1/customers/{id}."""

    @pytest.mark.asyncio
    async def test_delete_soft_deactivates_customer(self, async_client: AsyncClient, override_auth_tenant_a):
        create_resp = await async_client.post("/api/v1/customers/", json={
            "first_name": "Delete", "last_name": "Me", "email": "delete.me@example.com",
        })
        customer_id = create_resp.json()["id"]

        response = await async_client.delete(f"/api/v1/customers/{customer_id}")
        assert response.status_code == 200
        data = response.json()
        assert "deactivated" in data["message"].lower()

        get_resp = await async_client.get(f"/api/v1/customers/{customer_id}")
        assert get_resp.json()["is_active"] is False

    @pytest.mark.asyncio
    async def test_delete_nonexistent_returns_404(self, async_client: AsyncClient, override_auth_tenant_a):
        fake_id = str(uuid.uuid4())
        response = await async_client.delete(f"/api/v1/customers/{fake_id}")
        assert response.status_code == 404


# ================================================================
# Notes Tests (POST /{id}/notes, GET /{id}/notes)
# ================================================================


class TestCustomerNotes:
    """Tests for POST /{id}/notes and GET /{id}/notes."""

    @pytest.mark.asyncio
    async def test_add_note_succeeds_returns_201(self, async_client: AsyncClient, override_auth_tenant_a):
        create_resp = await async_client.post("/api/v1/customers/", json={
            "first_name": "Note", "last_name": "Test", "email": "note.test@example.com",
        })
        customer_id = create_resp.json()["id"]

        response = await async_client.post(f"/api/v1/customers/{customer_id}/notes", json={
            "content": "Important customer note.",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Important customer note."
        assert data["customer_id"] == customer_id
        assert "created_by" in data

    @pytest.mark.asyncio
    async def test_add_note_nonexistent_customer_returns_404(self, async_client: AsyncClient, override_auth_tenant_a):
        fake_id = str(uuid.uuid4())
        response = await async_client.post(f"/api/v1/customers/{fake_id}/notes", json={"content": "test"})
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_add_note_empty_content_returns_422(self, async_client: AsyncClient, override_auth_tenant_a):
        create_resp = await async_client.post("/api/v1/customers/", json={
            "first_name": "Empty", "last_name": "Note", "email": "empty.note@example.com",
        })
        customer_id = create_resp.json()["id"]

        response = await async_client.post(f"/api/v1/customers/{customer_id}/notes", json={"content": ""})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_notes_returns_paginated(self, async_client: AsyncClient, override_auth_tenant_a):
        create_resp = await async_client.post("/api/v1/customers/", json={
            "first_name": "Notes", "last_name": "List", "email": "notes.list@example.com",
        })
        customer_id = create_resp.json()["id"]

        await async_client.post(f"/api/v1/customers/{customer_id}/notes", json={"content": "Note 1"})
        await async_client.post(f"/api/v1/customers/{customer_id}/notes", json={"content": "Note 2"})

        response = await async_client.get(f"/api/v1/customers/{customer_id}/notes")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert "cursor" in data


# ================================================================
# CSV Import Tests (POST /import)
# ================================================================


class TestCsvImport:
    """Tests for POST /api/v1/customers/import."""

    @pytest.mark.asyncio
    async def test_import_valid_csv_succeeds(self, async_client: AsyncClient, override_auth_tenant_a):
        csv_content = b"first_name,last_name,email,phone\nAna,Pop,ana.import@example.com,+40700111222\nDan,Ion,dan.import@example.com,+40700333444\n"
        response = await async_client.post(
            "/api/v1/customers/import",
            files={"file": ("customers.csv", io.BytesIO(csv_content), "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["created"] == 2
        assert data["skipped"] == 0

    @pytest.mark.asyncio
    async def test_import_non_csv_returns_400(self, async_client: AsyncClient, override_auth_tenant_a):
        response = await async_client.post(
            "/api/v1/customers/import",
            files={"file": ("data.txt", io.BytesIO(b"not csv"), "text/plain")},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_import_missing_required_columns_returns_400(self, async_client: AsyncClient, override_auth_tenant_a):
        csv_content = b"email,phone\ntest@example.com,+40700111222\n"
        response = await async_client.post(
            "/api/v1/customers/import",
            files={"file": ("bad.csv", io.BytesIO(csv_content), "text/csv")},
        )
        assert response.status_code == 400


# ================================================================
# History Tests (GET /{id}/history)
# ================================================================


class TestCustomerHistory:
    """Tests for GET /api/v1/customers/{id}/history."""

    @pytest.mark.asyncio
    async def test_get_history_returns_placeholder(self, async_client: AsyncClient, override_auth_tenant_a):
        create_resp = await async_client.post("/api/v1/customers/", json={
            "first_name": "History", "last_name": "Test", "email": "history.api@example.com",
        })
        customer_id = create_resp.json()["id"]

        response = await async_client.get(f"/api/v1/customers/{customer_id}/history")
        assert response.status_code == 200
        data = response.json()
        assert "appointments" in data
        assert "jobs" in data
        assert "invoices" in data
        assert "files" in data
        assert "notes_count" in data
        assert data["appointments"]["total"] == 0

    @pytest.mark.asyncio
    async def test_get_history_nonexistent_returns_404(self, async_client: AsyncClient, override_auth_tenant_a):
        fake_id = str(uuid.uuid4())
        response = await async_client.get(f"/api/v1/customers/{fake_id}/history")
        assert response.status_code == 404


# ================================================================
# Tenant Isolation Tests
# ================================================================


class TestTenantIsolation:
    """Tests verifying that tenant A cannot access tenant B data."""

    @pytest.mark.asyncio
    async def test_tenant_isolation_cross_tenant_not_found(self, async_client: AsyncClient):
        """Customer created in Tenant A is not visible to Tenant B."""
        from app.core.deps import get_current_tenant_id

        # Create with tenant A
        app.dependency_overrides[get_current_user] = lambda: _make_user_payload(TEST_USER_ID, TEST_TENANT_A_ID)
        app.dependency_overrides[get_current_tenant_id] = lambda: TEST_TENANT_A_ID

        create_resp = await async_client.post("/api/v1/customers/", json={
            "first_name": "Cross", "last_name": "Tenant", "email": "cross.tenant.iso@example.com",
        })
        assert create_resp.status_code == 201
        customer_id = create_resp.json()["id"]

        # Switch to tenant B
        app.dependency_overrides[get_current_user] = lambda: _make_user_payload(TEST_USER_ID, TEST_TENANT_B_ID)
        app.dependency_overrides[get_current_tenant_id] = lambda: TEST_TENANT_B_ID

        # Tenant B should NOT find Tenant A customer
        get_resp = await async_client.get(f"/api/v1/customers/{customer_id}")
        assert get_resp.status_code == 404

        app.dependency_overrides.clear()
