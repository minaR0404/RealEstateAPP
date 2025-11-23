"""
Unit tests for models.py

Tests the SQLAlchemy Property model.
"""
import pytest
from sqlalchemy.exc import IntegrityError
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import models


@pytest.mark.unit
class TestPropertyModel:
    """Test cases for the Property model."""

    def test_property_creation(self, test_db_session):
        """Test creating a property instance."""
        property_obj = models.Property(
            name="新宿区",
            address="東京都",
            price=1500000.0
        )

        test_db_session.add(property_obj)
        test_db_session.commit()
        test_db_session.refresh(property_obj)

        assert property_obj.id is not None
        assert property_obj.name == "新宿区"
        assert property_obj.address == "東京都"
        assert property_obj.price == 1500000.0

    def test_property_repr(self, test_db_session):
        """Test property string representation."""
        property_obj = models.Property(
            name="渋谷区",
            address="東京都",
            price=1800000.0
        )

        test_db_session.add(property_obj)
        test_db_session.commit()

        # Check that the object can be converted to string
        str_repr = str(property_obj)
        assert str_repr is not None

    def test_property_with_all_fields(self, test_db_session):
        """Test creating property with explicit ID."""
        property_obj = models.Property(
            id=100,
            name="千代田区",
            address="東京都",
            price=3862500.0
        )

        test_db_session.add(property_obj)
        test_db_session.commit()
        test_db_session.refresh(property_obj)

        assert property_obj.id == 100
        assert property_obj.name == "千代田区"
        assert property_obj.address == "東京都"
        assert property_obj.price == 3862500.0

    def test_property_with_none_values(self, test_db_session):
        """Test that properties can have None values for optional fields."""
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

    def test_property_update(self, test_db_session):
        """Test updating a property."""
        property_obj = models.Property(
            name="横浜市",
            address="神奈川県",
            price=500000.0
        )

        test_db_session.add(property_obj)
        test_db_session.commit()
        property_id = property_obj.id

        # Update the property
        property_obj.price = 600000.0
        test_db_session.commit()
        test_db_session.refresh(property_obj)

        assert property_obj.id == property_id
        assert property_obj.price == 600000.0

    def test_property_delete(self, test_db_session):
        """Test deleting a property."""
        property_obj = models.Property(
            name="さいたま市",
            address="埼玉県",
            price=300000.0
        )

        test_db_session.add(property_obj)
        test_db_session.commit()
        property_id = property_obj.id

        # Delete the property
        test_db_session.delete(property_obj)
        test_db_session.commit()

        # Verify deletion
        deleted_property = test_db_session.query(models.Property).filter(
            models.Property.id == property_id
        ).first()
        assert deleted_property is None

    def test_property_query_by_name(self, test_db_session):
        """Test querying properties by name (which has an index)."""
        property1 = models.Property(name="港区", address="東京都", price=2000000.0)
        property2 = models.Property(name="品川区", address="東京都", price=1200000.0)

        test_db_session.add_all([property1, property2])
        test_db_session.commit()

        # Query by name
        result = test_db_session.query(models.Property).filter(
            models.Property.name == "港区"
        ).first()

        assert result is not None
        assert result.name == "港区"
        assert result.price == 2000000.0

    def test_property_query_by_address(self, test_db_session):
        """Test querying properties by address."""
        properties = [
            models.Property(name="横浜市", address="神奈川県", price=500000.0),
            models.Property(name="川崎市", address="神奈川県", price=600000.0),
            models.Property(name="新宿区", address="東京都", price=1500000.0),
        ]

        test_db_session.add_all(properties)
        test_db_session.commit()

        # Query by address
        results = test_db_session.query(models.Property).filter(
            models.Property.address == "神奈川県"
        ).all()

        assert len(results) == 2
        assert all(p.address == "神奈川県" for p in results)

    def test_property_query_by_price_range(self, test_db_session):
        """Test querying properties within a price range."""
        properties = [
            models.Property(name="区A", address="東京都", price=100000.0),
            models.Property(name="区B", address="東京都", price=500000.0),
            models.Property(name="区C", address="東京都", price=1000000.0),
            models.Property(name="区D", address="東京都", price=2000000.0),
        ]

        test_db_session.add_all(properties)
        test_db_session.commit()

        # Query properties with price between 400k and 1500k
        results = test_db_session.query(models.Property).filter(
            models.Property.price >= 400000.0,
            models.Property.price <= 1500000.0
        ).all()

        assert len(results) == 2
        assert all(400000.0 <= p.price <= 1500000.0 for p in results)

    def test_property_unique_ids(self, test_db_session):
        """Test that property IDs are unique (primary key constraint)."""
        property1 = models.Property(id=1, name="区1", address="東京都", price=100000.0)
        property2 = models.Property(id=1, name="区2", address="東京都", price=200000.0)

        test_db_session.add(property1)
        test_db_session.commit()

        test_db_session.add(property2)
        with pytest.raises(IntegrityError):
            test_db_session.commit()

    def test_property_ordering(self, test_db_session):
        """Test ordering properties by different fields."""
        properties = [
            models.Property(name="C区", address="東京都", price=300000.0),
            models.Property(name="A区", address="東京都", price=100000.0),
            models.Property(name="B区", address="東京都", price=200000.0),
        ]

        test_db_session.add_all(properties)
        test_db_session.commit()

        # Order by name
        results = test_db_session.query(models.Property).order_by(
            models.Property.name
        ).all()

        assert results[0].name == "A区"
        assert results[1].name == "B区"
        assert results[2].name == "C区"

        # Order by price descending
        results = test_db_session.query(models.Property).order_by(
            models.Property.price.desc()
        ).all()

        assert results[0].price == 300000.0
        assert results[1].price == 200000.0
        assert results[2].price == 100000.0

    def test_property_count(self, test_db_session, seed_test_properties):
        """Test counting properties."""
        count = test_db_session.query(models.Property).count()
        assert count == 5  # seed_test_properties creates 5 properties

    def test_property_with_japanese_characters(self, test_db_session):
        """Test that Japanese characters are properly stored and retrieved."""
        property_obj = models.Property(
            name="東京都千代田区",
            address="東京都",
            price=3000000.0
        )

        test_db_session.add(property_obj)
        test_db_session.commit()
        test_db_session.refresh(property_obj)

        assert property_obj.name == "東京都千代田区"
        assert property_obj.address == "東京都"

    def test_property_with_zero_price(self, test_db_session):
        """Test property with zero price (edge case)."""
        property_obj = models.Property(
            name="無料区",
            address="東京都",
            price=0.0
        )

        test_db_session.add(property_obj)
        test_db_session.commit()
        test_db_session.refresh(property_obj)

        assert property_obj.price == 0.0

    def test_property_with_negative_price(self, test_db_session):
        """Test property with negative price (should be allowed by model but might not make sense)."""
        property_obj = models.Property(
            name="マイナス区",
            address="東京都",
            price=-100000.0
        )

        test_db_session.add(property_obj)
        test_db_session.commit()
        test_db_session.refresh(property_obj)

        assert property_obj.price == -100000.0

    def test_property_with_large_price(self, test_db_session):
        """Test property with very large price value."""
        property_obj = models.Property(
            name="高額区",
            address="東京都",
            price=999999999.99
        )

        test_db_session.add(property_obj)
        test_db_session.commit()
        test_db_session.refresh(property_obj)

        assert property_obj.price == 999999999.99
