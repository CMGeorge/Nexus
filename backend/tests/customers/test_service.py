"""Unit tests for CustomerService business logic."""

import io
import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.customers.schemas import (
    CustomerCreate,
    CustomerNoteCreate,
    CustomerUpdate,
)
from app.customers.service import CustomerService
from tests.customers.conftest import TEST_TENANT_A_ID, TEST_TENANT_B_ID, TEST_USER_ID


class TestCustomerServiceCreate:
    """Tests for CustomerService.create()."""

    @pytest.mark.asyncio
    async def test_create_customer_with_valid_data_returns_201(self, db_session: AsyncSession, tenant_a):
        """Creating a customer with valid data succeeds and returns CustomerResponse."""
        service = CustomerService(db_session)
        data = CustomerCreate(
            first_name="Ion",
            last_name="Popescu",
            email="ion.popescu@example.com",
            phone="+40722123456",
            city="Bucuresti",
            country="RO",
        )
        result = await service.create(TEST_TENANT_A_ID, data)
        assert result.first_name == "Ion"
        assert result.last_name == "Popescu"
        assert result.email == "ion.popescu@example.com"
        assert result.phone == "+40722123456"
        assert result.city == "Bucuresti"
        assert result.country == "RO"
        assert result.is_active is True
        assert result.id is not None
        assert result.tenant_id == TEST_TENANT_A_ID

    @pytest.mark.asyncio
    async def test_create_customer_duplicate_email_returns_409(self, db_session: AsyncSession, tenant_a):
        """Creating a customer with an existing email within the tenant returns 409."""
        service = CustomerService(db_session)
        data = CustomerCreate(first_name="Ion", last_name="Popescu", email="dup@example.com")
        await service.create(TEST_TENANT_A_ID, data)

        duplicate = CustomerCreate(first_name="Maria", last_name="Ionescu", email="dup@example.com")
        with pytest.raises(HTTPException) as exc:
            await service.create(TEST_TENANT_A_ID, duplicate)
        assert exc.value.status_code == 409
        assert "already exists" in exc.value.detail

    @pytest.mark.asyncio
    async def test_create_customer_same_email_different_tenant_succeeds(self, db_session: AsyncSession, tenant_a, tenant_b):
        """Same email in different tenants is allowed (tenant isolation)."""
        service = CustomerService(db_session)
        data_a = CustomerCreate(first_name="Ion", last_name="Popescu", email="cross@example.com")
        await service.create(TEST_TENANT_A_ID, data_a)

        data_b = CustomerCreate(first_name="Maria", last_name="Ionescu", email="cross@example.com")
        result = await service.create(TEST_TENANT_B_ID, data_b)
        assert result.email == "cross@example.com"
        assert result.tenant_id == TEST_TENANT_B_ID

    @pytest.mark.asyncio
    async def test_create_customer_without_email_succeeds(self, db_session: AsyncSession, tenant_a):
        """Creating a customer without an email is allowed."""
        service = CustomerService(db_session)
        data = CustomerCreate(first_name="Vasile", last_name="Georgescu")
        result = await service.create(TEST_TENANT_A_ID, data)
        assert result.email is None
        assert result.first_name == "Vasile"

    @pytest.mark.asyncio
    async def test_create_customer_defaults_country_to_ro(self, db_session: AsyncSession, tenant_a):
        """Country defaults to RO when not provided."""
        service = CustomerService(db_session)
        data = CustomerCreate(first_name="Elena", last_name="Dumitrescu")
        result = await service.create(TEST_TENANT_A_ID, data)
        assert result.country == "RO"


class TestCustomerServiceGet:
    """Tests for CustomerService.get()."""

    @pytest.mark.asyncio
    async def test_get_existing_customer_returns_200(self, db_session: AsyncSession, tenant_a):
        """Getting an existing customer returns the full customer response."""
        service = CustomerService(db_session)
        created = await service.create(
            TEST_TENANT_A_ID,
            CustomerCreate(first_name="George", last_name="Enescu", email="george@example.com"),
        )
        result = await service.get([TEST_TENANT_A_ID], created.id)
        assert result.id == created.id
        assert result.first_name == "George"
        assert result.last_name == "Enescu"

    @pytest.mark.asyncio
    async def test_get_nonexistent_customer_returns_404(self, db_session: AsyncSession, tenant_a):
        """Getting a customer that does not exist returns 404."""
        service = CustomerService(db_session)
        fake_id = uuid.uuid4()
        with pytest.raises(HTTPException) as exc:
            await service.get([TEST_TENANT_A_ID], fake_id)
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_customer_tenant_isolation(self, db_session: AsyncSession, tenant_a, tenant_b):
        """Tenant A cannot access Tenant B customer."""
        service = CustomerService(db_session)
        created = await service.create(
            TEST_TENANT_B_ID,
            CustomerCreate(first_name="Mihai", last_name="Eminescu", email="mihai@example.com"),
        )
        with pytest.raises(HTTPException) as exc:
            await service.get([TEST_TENANT_A_ID], created.id)
        assert exc.value.status_code == 404


class TestCustomerServiceList:
    """Tests for CustomerService.list_customers()."""

    @pytest.mark.asyncio
    async def test_list_returns_cursor_paginated_results(self, db_session: AsyncSession, tenant_a):
        """List returns cursor-paginated results with correct structure."""
        service = CustomerService(db_session)
        for i in range(5):
            await service.create(
                TEST_TENANT_A_ID,
                CustomerCreate(first_name=f"User{i}", last_name=f"Test{i}", email=f"user{i}@example.com"),
            )
        result = await service.list_customers(
            [TEST_TENANT_A_ID], cursor=None, limit=3, search=None,
            sort_by="created_at", order="desc", is_active=None,
        )
        assert len(result.data) == 3
        assert result.cursor.has_more is True
        assert result.cursor.next is not None

    @pytest.mark.asyncio
    async def test_list_with_search_filters_by_name(self, db_session: AsyncSession, tenant_a):
        """Search filters customers by first_name and last_name."""
        service = CustomerService(db_session)
        await service.create(TEST_TENANT_A_ID, CustomerCreate(first_name="Alice", last_name="Smith", email="alice@example.com"))
        await service.create(TEST_TENANT_A_ID, CustomerCreate(first_name="Bob", last_name="Jones", email="bob@example.com"))
        await service.create(TEST_TENANT_A_ID, CustomerCreate(first_name="Charlie", last_name="Smithson", email="charlie@example.com"))

        result = await service.list_customers(
            [TEST_TENANT_A_ID], cursor=None, limit=10, search="Smith",
            sort_by="created_at", order="desc", is_active=None,
        )
        assert len(result.data) >= 1

    @pytest.mark.asyncio
    async def test_list_tenant_isolation(self, db_session: AsyncSession, tenant_a, tenant_b):
        """Tenant A list does not include Tenant B customers."""
        service = CustomerService(db_session)
        await service.create(TEST_TENANT_A_ID, CustomerCreate(first_name="TenantA", last_name="User", email="a_user@example.com"))
        await service.create(TEST_TENANT_B_ID, CustomerCreate(first_name="TenantB", last_name="User", email="b_user@example.com"))

        result_a = await service.list_customers(
            [TEST_TENANT_A_ID], cursor=None, limit=10, search="TenantB",
            sort_by="created_at", order="desc", is_active=None,
        )
        assert len(result_a.data) == 0

    @pytest.mark.asyncio
    async def test_list_active_filter(self, db_session: AsyncSession, tenant_a):
        """is_active filter returns only active or inactive customers."""
        service = CustomerService(db_session)
        c1 = await service.create(TEST_TENANT_A_ID, CustomerCreate(first_name="Active", last_name="User", email="active@example.com"))
        c2 = await service.create(TEST_TENANT_A_ID, CustomerCreate(first_name="Inactive", last_name="User", email="inactive@example.com"))
        await service.deactivate([TEST_TENANT_A_ID], c2.id)

        active = await service.list_customers(
            [TEST_TENANT_A_ID], cursor=None, limit=10, search=None,
            sort_by="created_at", order="desc", is_active=True,
        )
        assert all(c.is_active for c in active.data)

        inactive = await service.list_customers(
            [TEST_TENANT_A_ID], cursor=None, limit=10, search=None,
            sort_by="created_at", order="desc", is_active=False,
        )
        assert all(not c.is_active for c in inactive.data)


class TestCustomerServiceUpdate:
    """Tests for CustomerService.update()."""

    @pytest.mark.asyncio
    async def test_update_partial_fields_succeeds(self, db_session: AsyncSession, tenant_a):
        """PATCH update changes only provided fields."""
        service = CustomerService(db_session)
        created = await service.create(
            TEST_TENANT_A_ID,
            CustomerCreate(first_name="Old", last_name="Name", email="old@example.com", phone="+40700111111"),
        )
        update_data = CustomerUpdate(first_name="New", phone="+40700222222")
        result = await service.update([TEST_TENANT_A_ID], created.id, update_data)
        assert result.first_name == "New"
        assert result.last_name == "Name"
        assert result.phone == "+40700222222"
        assert result.email == "old@example.com"

    @pytest.mark.asyncio
    async def test_update_nonexistent_returns_404(self, db_session: AsyncSession, tenant_a):
        """Updating a nonexistent customer returns 404."""
        service = CustomerService(db_session)
        fake_id = uuid.uuid4()
        with pytest.raises(HTTPException) as exc:
            await service.update([TEST_TENANT_A_ID], fake_id, CustomerUpdate(first_name="X"))
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_email_to_existing_returns_409(self, db_session: AsyncSession, tenant_a):
        """Updating email to one already used by another customer returns 409."""
        service = CustomerService(db_session)
        c1 = await service.create(TEST_TENANT_A_ID, CustomerCreate(first_name="First", last_name="User", email="first@example.com"))
        c2 = await service.create(TEST_TENANT_A_ID, CustomerCreate(first_name="Second", last_name="User", email="second@example.com"))

        with pytest.raises(HTTPException) as exc:
            await service.update([TEST_TENANT_A_ID], c2.id, CustomerUpdate(email="first@example.com"))
        assert exc.value.status_code == 409

    @pytest.mark.asyncio
    async def test_update_same_email_no_conflict(self, db_session: AsyncSession, tenant_a):
        """Updating with the same email (no change) does not trigger conflict."""
        service = CustomerService(db_session)
        created = await service.create(TEST_TENANT_A_ID, CustomerCreate(first_name="Same", last_name="Email", email="same@example.com"))
        result = await service.update([TEST_TENANT_A_ID], created.id, CustomerUpdate(email="same@example.com"))
        assert result.email == "same@example.com"


class TestCustomerServiceDeactivate:
    """Tests for CustomerService.deactivate()."""

    @pytest.mark.asyncio
    async def test_deactivate_sets_is_active_false(self, db_session: AsyncSession, tenant_a):
        """Deactivating a customer sets is_active to False."""
        service = CustomerService(db_session)
        created = await service.create(TEST_TENANT_A_ID, CustomerCreate(first_name="Deactivate", last_name="Me", email="deact@example.com"))

        result = await service.deactivate([TEST_TENANT_A_ID], created.id)
        assert "deactivated" in result.message.lower()

        customer = await service.get([TEST_TENANT_A_ID], created.id)
        assert customer.is_active is False

    @pytest.mark.asyncio
    async def test_deactivate_nonexistent_returns_404(self, db_session: AsyncSession, tenant_a):
        """Deactivating a nonexistent customer returns 404."""
        service = CustomerService(db_session)
        with pytest.raises(HTTPException) as exc:
            await service.deactivate([TEST_TENANT_A_ID], uuid.uuid4())
        assert exc.value.status_code == 404


class TestCustomerServiceNotes:
    """Tests for CustomerService.add_note() and list_notes()."""

    @pytest.mark.asyncio
    async def test_add_note_succeeds(self, db_session: AsyncSession, tenant_a):
        """Adding a note to a customer succeeds."""
        service = CustomerService(db_session)
        customer = await service.create(TEST_TENANT_A_ID, CustomerCreate(first_name="Note", last_name="Test", email="note@example.com"))

        note_data = CustomerNoteCreate(content="Important customer.")
        result = await service.add_note([TEST_TENANT_A_ID], customer.id, TEST_USER_ID, note_data)
        assert result.content == "Important customer."
        assert result.customer_id == customer.id

    @pytest.mark.asyncio
    async def test_add_note_nonexistent_customer_returns_404(self, db_session: AsyncSession, tenant_a):
        """Adding a note to a nonexistent customer returns 404."""
        service = CustomerService(db_session)
        with pytest.raises(HTTPException) as exc:
            await service.add_note([TEST_TENANT_A_ID], uuid.uuid4(), TEST_USER_ID, CustomerNoteCreate(content="test"))
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_list_notes_returns_paginated(self, db_session: AsyncSession, tenant_a):
        """Listing notes returns cursor-paginated results."""
        service = CustomerService(db_session)
        customer = await service.create(TEST_TENANT_A_ID, CustomerCreate(first_name="NotesList", last_name="Test", email="noteslist@example.com"))

        for i in range(3):
            await service.add_note([TEST_TENANT_A_ID], customer.id, TEST_USER_ID, CustomerNoteCreate(content=f"Note {i}"))

        result = await service.list_notes([TEST_TENANT_A_ID], customer.id, cursor=None, limit=10)
        assert len(result.data) == 3


class TestCustomerServiceCsvImport:
    """Tests for CustomerService.import_csv()."""

    @pytest.mark.asyncio
    async def test_import_valid_csv_creates_customers(self, db_session: AsyncSession, tenant_a):
        """Importing a valid CSV creates customers."""
        from fastapi import UploadFile
        csv_content = "first_name,last_name,email,phone\nAna,Pop,ana.csv@example.com,+40700111222\nDan,Ion,dan.csv@example.com,+40700333444\n"
        file = UploadFile(filename="customers.csv", file=io.BytesIO(csv_content.encode("utf-8")))

        service = CustomerService(db_session)
        result = await service.import_csv(TEST_TENANT_A_ID, file)
        assert result.total == 2
        assert result.created == 2
        assert result.skipped == 0
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_import_csv_missing_required_columns_returns_400(self, db_session: AsyncSession, tenant_a):
        """Importing a CSV without first_name/last_name columns returns 400."""
        from fastapi import UploadFile
        csv_content = "email,phone\ntest@example.com,+40700111222\n"
        file = UploadFile(filename="bad.csv", file=io.BytesIO(csv_content.encode("utf-8")))

        service = CustomerService(db_session)
        with pytest.raises(HTTPException) as exc:
            await service.import_csv(TEST_TENANT_A_ID, file)
        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_import_csv_non_csv_file_returns_400(self, db_session: AsyncSession, tenant_a):
        """Importing a non-CSV file returns 400."""
        from fastapi import UploadFile
        file = UploadFile(filename="data.txt", file=io.BytesIO(b"some text data"))

        service = CustomerService(db_session)
        with pytest.raises(HTTPException) as exc:
            await service.import_csv(TEST_TENANT_A_ID, file)
        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_import_csv_missing_name_rows_skipped(self, db_session: AsyncSession, tenant_a):
        """Rows missing first_name or last_name are skipped with errors."""
        from fastapi import UploadFile
        csv_content = "first_name,last_name,email\n,Pop,missing_first@example.com\nDan,,missing_last@example.com\nGood,Row,good@example.com\n"
        file = UploadFile(filename="partial.csv", file=io.BytesIO(csv_content.encode("utf-8")))

        service = CustomerService(db_session)
        result = await service.import_csv(TEST_TENANT_A_ID, file)
        assert result.total == 3
        assert result.created == 1
        assert result.skipped == 2
        assert len(result.errors) == 2


class TestCustomerServiceHistory:
    """Tests for CustomerService.get_history()."""

    @pytest.mark.asyncio
    async def test_get_history_returns_placeholder_structure(self, db_session: AsyncSession, tenant_a):
        """History returns placeholder data for MVP."""
        service = CustomerService(db_session)
        customer = await service.create(TEST_TENANT_A_ID, CustomerCreate(first_name="History", last_name="Test", email="history@example.com"))

        result = await service.get_history([TEST_TENANT_A_ID], customer.id)
        assert result.appointments["total"] == 0
        assert result.jobs["total"] == 0
        assert result.invoices["total"] == 0
        assert result.files["total"] == 0
        assert result.notes_count == 0

    @pytest.mark.asyncio
    async def test_get_history_nonexistent_returns_404(self, db_session: AsyncSession, tenant_a):
        """History for nonexistent customer returns 404."""
        service = CustomerService(db_session)
        with pytest.raises(HTTPException) as exc:
            await service.get_history([TEST_TENANT_A_ID], uuid.uuid4())
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_history_includes_notes_count(self, db_session: AsyncSession, tenant_a):
        """History includes the count of notes attached."""
        service = CustomerService(db_session)
        customer = await service.create(TEST_TENANT_A_ID, CustomerCreate(first_name="NotesCount", last_name="Test", email="count@example.com"))
        await service.add_note([TEST_TENANT_A_ID], customer.id, TEST_USER_ID, CustomerNoteCreate(content="Note 1"))
        await service.add_note([TEST_TENANT_A_ID], customer.id, TEST_USER_ID, CustomerNoteCreate(content="Note 2"))

        result = await service.get_history([TEST_TENANT_A_ID], customer.id)
        assert result.notes_count == 2
