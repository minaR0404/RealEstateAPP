"""
Unit tests for schemas.py

Tests Pydantic schemas for data validation.
"""
import pytest
from pydantic import ValidationError
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import schemas


@pytest.mark.unit
class TestPropertyBase:
    """Test cases for PropertyBase schema."""

    def test_property_base_valid_data(self):
        """Test creating PropertyBase with valid data."""
        data = {
            "name": "新宿区",
            "address": "東京都",
            "price": 1500000.0
        }

        property_base = schemas.PropertyBase(**data)

        assert property_base.name == "新宿区"
        assert property_base.address == "東京都"
        assert property_base.price == 1500000.0

    def test_property_base_with_japanese(self):
        """Test PropertyBase with Japanese characters."""
        data = {
            "name": "東京都千代田区",
            "address": "東京都",
            "price": 3862500.0
        }

        property_base = schemas.PropertyBase(**data)

        assert property_base.name == "東京都千代田区"
        assert property_base.address == "東京都"

    def test_property_base_missing_name(self):
        """Test that PropertyBase requires name field."""
        data = {
            "address": "東京都",
            "price": 1500000.0
        }

        with pytest.raises(ValidationError) as exc_info:
            schemas.PropertyBase(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_property_base_missing_address(self):
        """Test that PropertyBase requires address field."""
        data = {
            "name": "新宿区",
            "price": 1500000.0
        }

        with pytest.raises(ValidationError) as exc_info:
            schemas.PropertyBase(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("address",) for error in errors)

    def test_property_base_missing_price(self):
        """Test that PropertyBase requires price field."""
        data = {
            "name": "新宿区",
            "address": "東京都"
        }

        with pytest.raises(ValidationError) as exc_info:
            schemas.PropertyBase(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("price",) for error in errors)

    def test_property_base_invalid_price_type(self):
        """Test that PropertyBase validates price as float."""
        data = {
            "name": "新宿区",
            "address": "東京都",
            "price": "not a number"
        }

        with pytest.raises(ValidationError) as exc_info:
            schemas.PropertyBase(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("price",) for error in errors)

    def test_property_base_price_type_coercion(self):
        """Test that PropertyBase coerces integer to float for price."""
        data = {
            "name": "新宿区",
            "address": "東京都",
            "price": 1500000  # Integer, not float
        }

        property_base = schemas.PropertyBase(**data)

        assert property_base.price == 1500000.0
        assert isinstance(property_base.price, float)

    def test_property_base_negative_price(self):
        """Test PropertyBase with negative price (allowed by schema)."""
        data = {
            "name": "新宿区",
            "address": "東京都",
            "price": -1500000.0
        }

        property_base = schemas.PropertyBase(**data)

        assert property_base.price == -1500000.0

    def test_property_base_zero_price(self):
        """Test PropertyBase with zero price."""
        data = {
            "name": "新宿区",
            "address": "東京都",
            "price": 0.0
        }

        property_base = schemas.PropertyBase(**data)

        assert property_base.price == 0.0

    def test_property_base_very_large_price(self):
        """Test PropertyBase with very large price value."""
        data = {
            "name": "新宿区",
            "address": "東京都",
            "price": 999999999999.99
        }

        property_base = schemas.PropertyBase(**data)

        assert property_base.price == 999999999999.99

    def test_property_base_empty_string_name(self):
        """Test PropertyBase with empty string for name."""
        data = {
            "name": "",
            "address": "東京都",
            "price": 1500000.0
        }

        # Pydantic allows empty strings by default
        property_base = schemas.PropertyBase(**data)
        assert property_base.name == ""

    def test_property_base_extra_fields_ignored(self):
        """Test that extra fields are ignored by default."""
        data = {
            "name": "新宿区",
            "address": "東京都",
            "price": 1500000.0,
            "extra_field": "should be ignored"
        }

        property_base = schemas.PropertyBase(**data)

        assert not hasattr(property_base, "extra_field")


@pytest.mark.unit
class TestPropertyCreate:
    """Test cases for PropertyCreate schema."""

    def test_property_create_inherits_from_base(self):
        """Test that PropertyCreate inherits from PropertyBase."""
        assert issubclass(schemas.PropertyCreate, schemas.PropertyBase)

    def test_property_create_valid_data(self):
        """Test creating PropertyCreate with valid data."""
        data = {
            "name": "渋谷区",
            "address": "東京都",
            "price": 1800000.0
        }

        property_create = schemas.PropertyCreate(**data)

        assert property_create.name == "渋谷区"
        assert property_create.address == "東京都"
        assert property_create.price == 1800000.0

    def test_property_create_same_validation_as_base(self):
        """Test that PropertyCreate has same validation as PropertyBase."""
        data = {
            "name": "港区",
            "price": 2000000.0
            # Missing address
        }

        with pytest.raises(ValidationError):
            schemas.PropertyCreate(**data)

    def test_property_create_no_id_field(self):
        """Test that PropertyCreate doesn't accept id field (it's auto-generated)."""
        data = {
            "id": 100,
            "name": "千代田区",
            "address": "東京都",
            "price": 3862500.0
        }

        property_create = schemas.PropertyCreate(**data)

        # ID should be ignored since it's not in the schema
        assert not hasattr(property_create, "id")


@pytest.mark.unit
class TestProperty:
    """Test cases for Property schema (response model)."""

    def test_property_valid_data(self):
        """Test creating Property with valid data including id."""
        data = {
            "id": 1,
            "name": "新宿区",
            "address": "東京都",
            "price": 1500000.0
        }

        property_obj = schemas.Property(**data)

        assert property_obj.id == 1
        assert property_obj.name == "新宿区"
        assert property_obj.address == "東京都"
        assert property_obj.price == 1500000.0

    def test_property_requires_id(self):
        """Test that Property schema requires id field."""
        data = {
            "name": "新宿区",
            "address": "東京都",
            "price": 1500000.0
        }

        with pytest.raises(ValidationError) as exc_info:
            schemas.Property(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_property_id_must_be_integer(self):
        """Test that Property id must be an integer."""
        data = {
            "id": "not an integer",
            "name": "新宿区",
            "address": "東京都",
            "price": 1500000.0
        }

        with pytest.raises(ValidationError) as exc_info:
            schemas.Property(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_property_id_coercion(self):
        """Test that Property can coerce string numbers to int for id."""
        data = {
            "id": "123",
            "name": "新宿区",
            "address": "東京都",
            "price": 1500000.0
        }

        property_obj = schemas.Property(**data)

        assert property_obj.id == 123
        assert isinstance(property_obj.id, int)

    def test_property_from_attributes_enabled(self):
        """Test that Property has from_attributes enabled."""
        config = schemas.Property.Config
        assert hasattr(config, "from_attributes")
        assert config.from_attributes is True

    def test_property_from_orm_object(self, test_db_session, create_test_property):
        """Test creating Property schema from ORM object."""
        # Create a real ORM object
        orm_property = create_test_property(
            name="品川区",
            address="東京都",
            price=1200000.0
        )

        # Convert to Pydantic schema
        property_schema = schemas.Property.from_orm(orm_property)

        assert property_schema.id == orm_property.id
        assert property_schema.name == orm_property.name
        assert property_schema.address == orm_property.address
        assert property_schema.price == orm_property.price

    def test_property_json_serialization(self):
        """Test that Property can be serialized to JSON."""
        data = {
            "id": 1,
            "name": "中央区",
            "address": "東京都",
            "price": 2500000.0
        }

        property_obj = schemas.Property(**data)
        json_str = property_obj.json()

        assert isinstance(json_str, str)
        assert "中央区" in json_str
        assert "東京都" in json_str

    def test_property_dict_conversion(self):
        """Test converting Property to dictionary."""
        data = {
            "id": 1,
            "name": "港区",
            "address": "東京都",
            "price": 2000000.0
        }

        property_obj = schemas.Property(**data)
        property_dict = property_obj.dict()

        assert isinstance(property_dict, dict)
        assert property_dict["id"] == 1
        assert property_dict["name"] == "港区"
        assert property_dict["address"] == "東京都"
        assert property_dict["price"] == 2000000.0

    def test_property_with_all_required_fields(self):
        """Test Property with all required fields."""
        data = {
            "id": 999,
            "name": "全フィールド区",
            "address": "東京都",
            "price": 5000000.0
        }

        property_obj = schemas.Property(**data)

        assert property_obj.id == 999
        assert property_obj.name == "全フィールド区"


@pytest.mark.unit
class TestSchemaValidation:
    """Test schema validation edge cases."""

    def test_unicode_characters_in_all_schemas(self):
        """Test that all schemas handle Unicode correctly."""
        unicode_data = {
            "name": "東京都千代田区🏢",
            "address": "東京都🗼",
            "price": 1000000.0
        }

        base = schemas.PropertyBase(**unicode_data)
        create = schemas.PropertyCreate(**unicode_data)

        assert "🏢" in base.name
        assert "🗼" in base.address
        assert "🏢" in create.name
        assert "🗼" in create.address

    def test_price_precision(self):
        """Test price precision handling."""
        data = {
            "name": "精密区",
            "address": "東京都",
            "price": 1234567.123456789
        }

        property_base = schemas.PropertyBase(**data)

        # Float precision may affect exact value
        assert abs(property_base.price - 1234567.123456789) < 0.001

    def test_schema_inheritance_chain(self):
        """Test the inheritance chain of schemas."""
        # PropertyCreate should inherit from PropertyBase
        assert issubclass(schemas.PropertyCreate, schemas.PropertyBase)

        # Property should inherit from PropertyBase (implicitly through shared fields)
        # but is defined separately, so we check it has the same fields
        property_data = {
            "id": 1,
            "name": "継承区",
            "address": "東京都",
            "price": 1000000.0
        }

        property_obj = schemas.Property(**property_data)
        assert hasattr(property_obj, "name")
        assert hasattr(property_obj, "address")
        assert hasattr(property_obj, "price")
        assert hasattr(property_obj, "id")

    def test_none_values_not_allowed_for_required_fields(self):
        """Test that None values are not accepted for required fields."""
        data = {
            "name": None,
            "address": "東京都",
            "price": 1000000.0
        }

        with pytest.raises(ValidationError):
            schemas.PropertyBase(**data)
