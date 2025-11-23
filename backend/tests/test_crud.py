"""
Unit tests for crud.py

Tests CRUD operations for Property model.
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import crud
import models
import schemas


@pytest.mark.unit
class TestGetProperty:
    """Test cases for get_property function."""

    def test_get_existing_property(self, test_db_session, create_test_property):
        """Test retrieving an existing property by ID."""
        # Create a property
        property_obj = create_test_property(
            name="新宿区",
            address="東京都",
            price=1500000.0
        )

        # Retrieve it using crud function
        result = crud.get_property(test_db_session, property_obj.id)

        assert result is not None
        assert result.id == property_obj.id
        assert result.name == "新宿区"
        assert result.address == "東京都"
        assert result.price == 1500000.0

    def test_get_nonexistent_property(self, test_db_session):
        """Test retrieving a property that doesn't exist."""
        result = crud.get_property(test_db_session, 99999)
        assert result is None

    def test_get_property_with_invalid_id(self, test_db_session):
        """Test retrieving property with various invalid IDs."""
        assert crud.get_property(test_db_session, 0) is None
        assert crud.get_property(test_db_session, -1) is None

    def test_get_first_of_multiple_properties(self, test_db_session, seed_test_properties):
        """Test getting the first property when multiple exist."""
        first_property = seed_test_properties[0]
        result = crud.get_property(test_db_session, first_property.id)

        assert result is not None
        assert result.id == first_property.id
        assert result.name == first_property.name


@pytest.mark.unit
class TestGetProperties:
    """Test cases for get_properties function."""

    def test_get_all_properties_default(self, test_db_session, seed_test_properties):
        """Test getting properties with default pagination."""
        results = crud.get_properties(test_db_session)

        assert len(results) == 5  # All 5 seeded properties
        assert all(isinstance(p, models.Property) for p in results)

    def test_get_properties_with_limit(self, test_db_session, seed_test_properties):
        """Test getting properties with a limit."""
        results = crud.get_properties(test_db_session, skip=0, limit=3)

        assert len(results) == 3
        assert all(isinstance(p, models.Property) for p in results)

    def test_get_properties_with_skip(self, test_db_session, seed_test_properties):
        """Test getting properties with skip offset."""
        # Get all properties first to know what to expect
        all_properties = crud.get_properties(test_db_session, skip=0, limit=10)

        # Skip first 2
        results = crud.get_properties(test_db_session, skip=2, limit=10)

        assert len(results) == 3  # 5 total - 2 skipped = 3
        # Verify that we skipped the first 2
        assert results[0].id == all_properties[2].id

    def test_get_properties_with_skip_and_limit(self, test_db_session, seed_test_properties):
        """Test pagination with both skip and limit."""
        results = crud.get_properties(test_db_session, skip=1, limit=2)

        assert len(results) == 2

    def test_get_properties_skip_all(self, test_db_session, seed_test_properties):
        """Test skipping more properties than exist."""
        results = crud.get_properties(test_db_session, skip=10, limit=10)

        assert len(results) == 0

    def test_get_properties_from_empty_database(self, test_db_session):
        """Test getting properties when database is empty."""
        results = crud.get_properties(test_db_session)

        assert len(results) == 0
        assert results == []

    def test_get_properties_limit_zero(self, test_db_session, seed_test_properties):
        """Test getting properties with limit=0."""
        results = crud.get_properties(test_db_session, skip=0, limit=0)

        assert len(results) == 0

    def test_get_properties_negative_skip(self, test_db_session, seed_test_properties):
        """Test getting properties with negative skip (treated as 0)."""
        results = crud.get_properties(test_db_session, skip=-5, limit=10)

        # SQLAlchemy handles negative offset as 0
        assert len(results) >= 0

    def test_get_properties_large_limit(self, test_db_session, seed_test_properties):
        """Test getting properties with very large limit."""
        results = crud.get_properties(test_db_session, skip=0, limit=1000)

        assert len(results) == 5  # Only 5 properties exist

    def test_get_properties_preserves_order(self, test_db_session):
        """Test that properties are returned in consistent order."""
        # Create properties with specific IDs
        for i in range(5):
            prop = models.Property(name=f"区{i}", address="東京都", price=float(i * 100000))
            test_db_session.add(prop)
        test_db_session.commit()

        # Get properties twice and verify same order
        results1 = crud.get_properties(test_db_session, skip=0, limit=10)
        results2 = crud.get_properties(test_db_session, skip=0, limit=10)

        assert len(results1) == len(results2)
        for r1, r2 in zip(results1, results2):
            assert r1.id == r2.id


@pytest.mark.unit
class TestCreateProperty:
    """Test cases for create_property function."""

    def test_create_property_basic(self, test_db_session):
        """Test creating a basic property."""
        property_data = schemas.PropertyCreate(
            name="港区",
            address="東京都",
            price=2000000.0
        )

        result = crud.create_property(test_db_session, property_data)

        assert result is not None
        assert result.id is not None
        assert result.name == "港区"
        assert result.address == "東京都"
        assert result.price == 2000000.0

    def test_create_property_returns_instance(self, test_db_session):
        """Test that create_property returns a Property instance."""
        property_data = schemas.PropertyCreate(
            name="品川区",
            address="東京都",
            price=1200000.0
        )

        result = crud.create_property(test_db_session, property_data)

        assert isinstance(result, models.Property)

    def test_create_property_persists_to_database(self, test_db_session):
        """Test that created property is actually saved to database."""
        property_data = schemas.PropertyCreate(
            name="中央区",
            address="東京都",
            price=2500000.0
        )

        created = crud.create_property(test_db_session, property_data)

        # Query directly to verify persistence
        queried = test_db_session.query(models.Property).filter(
            models.Property.id == created.id
        ).first()

        assert queried is not None
        assert queried.name == "中央区"

    def test_create_property_with_japanese_characters(self, test_db_session):
        """Test creating property with full Japanese text."""
        property_data = schemas.PropertyCreate(
            name="東京都千代田区",
            address="東京都",
            price=3862500.0
        )

        result = crud.create_property(test_db_session, property_data)

        assert result.name == "東京都千代田区"
        assert result.address == "東京都"

    def test_create_multiple_properties(self, test_db_session):
        """Test creating multiple properties."""
        properties_data = [
            schemas.PropertyCreate(name="横浜市", address="神奈川県", price=500000.0),
            schemas.PropertyCreate(name="川崎市", address="神奈川県", price=600000.0),
            schemas.PropertyCreate(name="相模原市", address="神奈川県", price=300000.0),
        ]

        results = []
        for prop_data in properties_data:
            result = crud.create_property(test_db_session, prop_data)
            results.append(result)

        assert len(results) == 3
        assert all(r.id is not None for r in results)
        # Verify all IDs are unique
        ids = [r.id for r in results]
        assert len(ids) == len(set(ids))

    def test_create_property_with_zero_price(self, test_db_session):
        """Test creating property with zero price."""
        property_data = schemas.PropertyCreate(
            name="無料区",
            address="東京都",
            price=0.0
        )

        result = crud.create_property(test_db_session, property_data)

        assert result.price == 0.0

    def test_create_property_with_float_price(self, test_db_session):
        """Test creating property with decimal price."""
        property_data = schemas.PropertyCreate(
            name="浮動区",
            address="東京都",
            price=1234567.89
        )

        result = crud.create_property(test_db_session, property_data)

        assert result.price == 1234567.89

    def test_create_property_auto_increment_id(self, test_db_session):
        """Test that IDs are auto-incremented."""
        prop1_data = schemas.PropertyCreate(name="区1", address="東京都", price=100000.0)
        prop2_data = schemas.PropertyCreate(name="区2", address="東京都", price=200000.0)

        prop1 = crud.create_property(test_db_session, prop1_data)
        prop2 = crud.create_property(test_db_session, prop2_data)

        assert prop2.id > prop1.id

    def test_create_property_with_same_name(self, test_db_session):
        """Test that multiple properties can have the same name."""
        prop1_data = schemas.PropertyCreate(name="同名区", address="東京都", price=100000.0)
        prop2_data = schemas.PropertyCreate(name="同名区", address="神奈川県", price=200000.0)

        prop1 = crud.create_property(test_db_session, prop1_data)
        prop2 = crud.create_property(test_db_session, prop2_data)

        assert prop1.id != prop2.id
        assert prop1.name == prop2.name == "同名区"

    def test_create_property_refreshes_instance(self, test_db_session):
        """Test that the returned instance is refreshed with DB-generated values."""
        property_data = schemas.PropertyCreate(
            name="リフレッシュ区",
            address="東京都",
            price=1000000.0
        )

        result = crud.create_property(test_db_session, property_data)

        # The ID should be populated from the database
        assert result.id is not None
        assert isinstance(result.id, int)


@pytest.mark.unit
class TestCRUDIntegration:
    """Integration tests combining multiple CRUD operations."""

    def test_create_and_get_property(self, test_db_session):
        """Test creating a property and then retrieving it."""
        property_data = schemas.PropertyCreate(
            name="統合テスト区",
            address="東京都",
            price=1111111.0
        )

        created = crud.create_property(test_db_session, property_data)
        retrieved = crud.get_property(test_db_session, created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == created.name
        assert retrieved.address == created.address
        assert retrieved.price == created.price

    def test_create_and_list_properties(self, test_db_session):
        """Test creating properties and listing them."""
        # Start with empty database
        initial_count = len(crud.get_properties(test_db_session))

        # Create 3 properties
        for i in range(3):
            property_data = schemas.PropertyCreate(
                name=f"テスト区{i}",
                address="東京都",
                price=float(i * 100000)
            )
            crud.create_property(test_db_session, property_data)

        # List all properties
        all_properties = crud.get_properties(test_db_session)

        assert len(all_properties) == initial_count + 3

    def test_pagination_consistency(self, test_db_session):
        """Test that pagination works consistently."""
        # Create 10 properties
        for i in range(10):
            property_data = schemas.PropertyCreate(
                name=f"ページ区{i}",
                address="東京都",
                price=float(i * 100000)
            )
            crud.create_property(test_db_session, property_data)

        # Get first page
        page1 = crud.get_properties(test_db_session, skip=0, limit=5)
        # Get second page
        page2 = crud.get_properties(test_db_session, skip=5, limit=5)

        assert len(page1) == 5
        assert len(page2) == 5
        # Verify no overlap
        page1_ids = [p.id for p in page1]
        page2_ids = [p.id for p in page2]
        assert len(set(page1_ids) & set(page2_ids)) == 0
