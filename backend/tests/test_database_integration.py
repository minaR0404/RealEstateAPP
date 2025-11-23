"""
Integration tests for database operations.

Tests the full database integration including transactions, rollbacks, and data integrity.
"""
import pytest
from sqlalchemy.exc import IntegrityError
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import models
import crud
import schemas


@pytest.mark.integration
class TestDatabaseTransactions:
    """Test database transaction handling."""

    def test_transaction_commit_success(self, test_db_session):
        """Test that successful transactions commit properly."""
        property_obj = models.Property(
            name="トランザクション区",
            address="東京都",
            price=1000000.0
        )

        test_db_session.add(property_obj)
        test_db_session.commit()

        # Verify the data persists
        result = test_db_session.query(models.Property).filter(
            models.Property.name == "トランザクション区"
        ).first()

        assert result is not None
        assert result.name == "トランザクション区"

    def test_transaction_rollback_on_error(self, test_db_session):
        """Test that transactions rollback on error."""
        # Add a valid property
        prop1 = models.Property(name="有効区", address="東京都", price=1000000.0)
        test_db_session.add(prop1)
        test_db_session.commit()

        # Try to add a property with duplicate ID (should fail)
        try:
            prop2 = models.Property(id=prop1.id, name="重複区", address="東京都", price=2000000.0)
            test_db_session.add(prop2)
            test_db_session.commit()
        except IntegrityError:
            test_db_session.rollback()

        # Verify only the first property exists
        count = test_db_session.query(models.Property).count()
        assert count == 1

    def test_multiple_operations_in_transaction(self, test_db_session):
        """Test multiple operations in a single transaction."""
        properties = [
            models.Property(name=f"複数区{i}", address="東京都", price=float(i * 100000))
            for i in range(5)
        ]

        for prop in properties:
            test_db_session.add(prop)

        test_db_session.commit()

        # Verify all were committed
        count = test_db_session.query(models.Property).count()
        assert count == 5

    def test_flush_vs_commit(self, test_db_session):
        """Test the difference between flush and commit."""
        property_obj = models.Property(
            name="フラッシュ区",
            address="東京都",
            price=1000000.0
        )

        test_db_session.add(property_obj)
        test_db_session.flush()  # Sends to DB but doesn't commit

        # ID should be assigned after flush
        assert property_obj.id is not None

        test_db_session.commit()

        # Now it's permanently stored
        result = test_db_session.query(models.Property).filter(
            models.Property.id == property_obj.id
        ).first()

        assert result is not None


@pytest.mark.integration
class TestDatabaseConstraints:
    """Test database constraints and integrity."""

    def test_primary_key_uniqueness(self, test_db_session):
        """Test that primary key must be unique."""
        prop1 = models.Property(id=100, name="区1", address="東京都", price=1000000.0)
        test_db_session.add(prop1)
        test_db_session.commit()

        prop2 = models.Property(id=100, name="区2", address="東京都", price=2000000.0)
        test_db_session.add(prop2)

        with pytest.raises(IntegrityError):
            test_db_session.commit()

    def test_auto_increment_id(self, test_db_session):
        """Test that IDs auto-increment properly."""
        props = []
        for i in range(5):
            prop = models.Property(name=f"自動区{i}", address="東京都", price=float(i * 100000))
            test_db_session.add(prop)
            test_db_session.commit()
            test_db_session.refresh(prop)
            props.append(prop)

        # Verify IDs are incrementing
        ids = [p.id for p in props]
        assert ids == sorted(ids)  # IDs should be in ascending order
        assert len(set(ids)) == len(ids)  # All IDs should be unique

    def test_nullable_fields(self, test_db_session):
        """Test that fields can be null."""
        property_obj = models.Property(
            name=None,
            address=None,
            price=None
        )

        test_db_session.add(property_obj)
        test_db_session.commit()
        test_db_session.refresh(property_obj)

        assert property_obj.id is not None
        assert property_obj.name is None
        assert property_obj.address is None
        assert property_obj.price is None


@pytest.mark.integration
class TestDatabaseQueries:
    """Test complex database queries."""

    def test_query_with_multiple_filters(self, test_db_session):
        """Test querying with multiple filter conditions."""
        properties = [
            models.Property(name="新宿区", address="東京都", price=1500000.0),
            models.Property(name="横浜市", address="神奈川県", price=500000.0),
            models.Property(name="渋谷区", address="東京都", price=1800000.0),
        ]

        test_db_session.add_all(properties)
        test_db_session.commit()

        # Query for Tokyo properties with price > 1,600,000
        results = test_db_session.query(models.Property).filter(
            models.Property.address == "東京都",
            models.Property.price > 1600000.0
        ).all()

        assert len(results) == 1
        assert results[0].name == "渋谷区"

    def test_query_with_or_condition(self, test_db_session):
        """Test querying with OR conditions."""
        from sqlalchemy import or_

        properties = [
            models.Property(name="新宿区", address="東京都", price=1500000.0),
            models.Property(name="横浜市", address="神奈川県", price=500000.0),
            models.Property(name="さいたま市", address="埼玉県", price=300000.0),
        ]

        test_db_session.add_all(properties)
        test_db_session.commit()

        # Query for properties in Tokyo OR Kanagawa
        results = test_db_session.query(models.Property).filter(
            or_(
                models.Property.address == "東京都",
                models.Property.address == "神奈川県"
            )
        ).all()

        assert len(results) == 2

    def test_query_with_like(self, test_db_session):
        """Test querying with LIKE pattern matching."""
        properties = [
            models.Property(name="新宿区", address="東京都", price=1500000.0),
            models.Property(name="新橋区", address="東京都", price=1600000.0),
            models.Property(name="渋谷区", address="東京都", price=1800000.0),
        ]

        test_db_session.add_all(properties)
        test_db_session.commit()

        # Query for properties starting with "新"
        results = test_db_session.query(models.Property).filter(
            models.Property.name.like("新%")
        ).all()

        assert len(results) == 2
        assert all(p.name.startswith("新") for p in results)

    def test_query_ordering(self, test_db_session):
        """Test query result ordering."""
        properties = [
            models.Property(name="C区", address="東京都", price=300000.0),
            models.Property(name="A区", address="東京都", price=100000.0),
            models.Property(name="B区", address="東京都", price=200000.0),
        ]

        test_db_session.add_all(properties)
        test_db_session.commit()

        # Order by price ascending
        results_asc = test_db_session.query(models.Property).order_by(
            models.Property.price.asc()
        ).all()

        assert results_asc[0].price == 100000.0
        assert results_asc[1].price == 200000.0
        assert results_asc[2].price == 300000.0

        # Order by price descending
        results_desc = test_db_session.query(models.Property).order_by(
            models.Property.price.desc()
        ).all()

        assert results_desc[0].price == 300000.0
        assert results_desc[1].price == 200000.0
        assert results_desc[2].price == 100000.0

    def test_query_aggregation(self, test_db_session):
        """Test query aggregation functions."""
        from sqlalchemy import func

        properties = [
            models.Property(name="区1", address="東京都", price=100000.0),
            models.Property(name="区2", address="東京都", price=200000.0),
            models.Property(name="区3", address="東京都", price=300000.0),
        ]

        test_db_session.add_all(properties)
        test_db_session.commit()

        # Count
        count = test_db_session.query(func.count(models.Property.id)).scalar()
        assert count == 3

        # Average
        avg_price = test_db_session.query(func.avg(models.Property.price)).scalar()
        assert avg_price == 200000.0

        # Min and Max
        min_price = test_db_session.query(func.min(models.Property.price)).scalar()
        max_price = test_db_session.query(func.max(models.Property.price)).scalar()
        assert min_price == 100000.0
        assert max_price == 300000.0

    def test_query_grouping(self, test_db_session):
        """Test query grouping."""
        from sqlalchemy import func

        properties = [
            models.Property(name="区1", address="東京都", price=100000.0),
            models.Property(name="区2", address="東京都", price=200000.0),
            models.Property(name="市1", address="神奈川県", price=300000.0),
        ]

        test_db_session.add_all(properties)
        test_db_session.commit()

        # Group by address and count
        results = test_db_session.query(
            models.Property.address,
            func.count(models.Property.id)
        ).group_by(models.Property.address).all()

        assert len(results) == 2
        address_counts = {address: count for address, count in results}
        assert address_counts["東京都"] == 2
        assert address_counts["神奈川県"] == 1


@pytest.mark.integration
class TestCRUDWithDatabase:
    """Test CRUD operations with real database."""

    def test_full_crud_cycle(self, test_db_session):
        """Test Create, Read, Update, Delete cycle."""
        # Create
        property_data = schemas.PropertyCreate(
            name="CRUD区",
            address="東京都",
            price=1000000.0
        )
        created = crud.create_property(test_db_session, property_data)
        assert created.id is not None

        # Read
        read = crud.get_property(test_db_session, created.id)
        assert read is not None
        assert read.name == "CRUD区"

        # Update
        read.price = 1500000.0
        test_db_session.commit()
        updated = crud.get_property(test_db_session, created.id)
        assert updated.price == 1500000.0

        # Delete
        test_db_session.delete(updated)
        test_db_session.commit()
        deleted = crud.get_property(test_db_session, created.id)
        assert deleted is None

    def test_crud_list_pagination(self, test_db_session):
        """Test CRUD list with pagination."""
        # Create 15 properties
        for i in range(15):
            property_data = schemas.PropertyCreate(
                name=f"ページ区{i}",
                address="東京都",
                price=float(i * 100000)
            )
            crud.create_property(test_db_session, property_data)

        # Get first page
        page1 = crud.get_properties(test_db_session, skip=0, limit=5)
        assert len(page1) == 5

        # Get second page
        page2 = crud.get_properties(test_db_session, skip=5, limit=5)
        assert len(page2) == 5

        # Get third page
        page3 = crud.get_properties(test_db_session, skip=10, limit=5)
        assert len(page3) == 5

        # Verify no overlap
        all_ids = [p.id for p in page1 + page2 + page3]
        assert len(all_ids) == len(set(all_ids))

    def test_concurrent_crud_operations(self, test_db_session):
        """Test multiple CRUD operations in sequence."""
        created_properties = []

        # Create multiple properties
        for i in range(5):
            property_data = schemas.PropertyCreate(
                name=f"並行区{i}",
                address="東京都",
                price=float(i * 100000)
            )
            created = crud.create_property(test_db_session, property_data)
            created_properties.append(created)

        # Read all
        all_properties = crud.get_properties(test_db_session, skip=0, limit=10)
        assert len(all_properties) >= 5

        # Update some
        for prop in created_properties[:3]:
            prop.price *= 1.1
        test_db_session.commit()

        # Delete some
        for prop in created_properties[3:]:
            test_db_session.delete(prop)
        test_db_session.commit()

        # Verify final state
        remaining = crud.get_properties(test_db_session, skip=0, limit=10)
        remaining_ids = [p.id for p in remaining]

        for prop in created_properties[:3]:
            assert prop.id in remaining_ids

        for prop in created_properties[3:]:
            assert prop.id not in remaining_ids


@pytest.mark.integration
class TestDatabasePerformance:
    """Test database performance characteristics."""

    def test_bulk_insert_performance(self, test_db_session):
        """Test inserting a large number of records."""
        properties = [
            models.Property(name=f"大量区{i}", address="東京都", price=float(i * 100000))
            for i in range(100)
        ]

        # Bulk add
        test_db_session.add_all(properties)
        test_db_session.commit()

        # Verify
        count = test_db_session.query(models.Property).count()
        assert count == 100

    def test_index_performance(self, test_db_session):
        """Test that indexed columns perform well."""
        # Create many properties
        for i in range(100):
            prop = models.Property(name=f"インデックス区{i}", address="東京都", price=float(i * 100000))
            test_db_session.add(prop)
        test_db_session.commit()

        # Query by indexed column (name)
        result = test_db_session.query(models.Property).filter(
            models.Property.name == "インデックス区50"
        ).first()

        assert result is not None
        assert result.name == "インデックス区50"

    def test_pagination_large_dataset(self, test_db_session):
        """Test pagination with large dataset."""
        # Create 200 properties
        for i in range(200):
            prop = models.Property(name=f"区{i}", address="東京都", price=float(i * 100000))
            test_db_session.add(prop)
        test_db_session.commit()

        # Test pagination at different offsets
        page_size = 20
        for page_num in range(10):
            skip = page_num * page_size
            page = crud.get_properties(test_db_session, skip=skip, limit=page_size)
            assert len(page) == page_size


@pytest.mark.integration
class TestDatabaseEdgeCases:
    """Test edge cases in database operations."""

    def test_unicode_edge_cases(self, test_db_session):
        """Test various Unicode characters."""
        property_obj = models.Property(
            name="特殊文字区🏢🗼",
            address="東京都⛩️",
            price=1000000.0
        )

        test_db_session.add(property_obj)
        test_db_session.commit()
        test_db_session.refresh(property_obj)

        assert "🏢" in property_obj.name
        assert "⛩️" in property_obj.address

    def test_very_long_strings(self, test_db_session):
        """Test handling of very long strings."""
        long_name = "区" * 1000
        property_obj = models.Property(
            name=long_name,
            address="東京都",
            price=1000000.0
        )

        test_db_session.add(property_obj)
        test_db_session.commit()
        test_db_session.refresh(property_obj)

        assert property_obj.name == long_name

    def test_extreme_price_values(self, test_db_session):
        """Test extreme price values."""
        properties = [
            models.Property(name="最小区", address="東京都", price=0.01),
            models.Property(name="最大区", address="東京都", price=999999999999.99),
            models.Property(name="ゼロ区", address="東京都", price=0.0),
        ]

        test_db_session.add_all(properties)
        test_db_session.commit()

        for prop in properties:
            test_db_session.refresh(prop)
            assert prop.id is not None

    def test_empty_strings(self, test_db_session):
        """Test handling of empty strings."""
        property_obj = models.Property(
            name="",
            address="",
            price=1000000.0
        )

        test_db_session.add(property_obj)
        test_db_session.commit()
        test_db_session.refresh(property_obj)

        assert property_obj.name == ""
        assert property_obj.address == ""
