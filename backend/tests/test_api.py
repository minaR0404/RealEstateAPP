"""
Integration tests for FastAPI endpoints (main.py)

Tests the REST API endpoints with real HTTP requests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from database import Base, SessionLocal
import models


# Override the database for testing
@pytest.fixture(scope="function")
def test_client_with_db():
    """Create a test client with a fresh test database for each test."""
    # Create in-memory database
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Note: Since main.py doesn't use dependency injection properly,
    # we'll need to work around this by patching SessionLocal
    import database
    original_session_local = database.SessionLocal
    database.SessionLocal = TestingSessionLocal

    # Create a test session that will be used for setup/teardown
    test_session = TestingSessionLocal()

    client = TestClient(app)

    yield {"client": client, "db": test_session}

    # Cleanup
    test_session.close()
    database.SessionLocal = original_session_local
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.mark.integration
class TestGetPropertiesEndpoint:
    """Test cases for GET /properties/ endpoint."""

    def test_get_properties_empty_database(self, test_client_with_db):
        """Test getting properties from empty database."""
        client = test_client_with_db["client"]
        response = client.get("/properties/")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_properties_with_data(self, test_client_with_db):
        """Test getting properties when data exists."""
        db = test_client_with_db["db"]
        client = test_client_with_db["client"]

        # Create test data
        properties = [
            models.Property(name="新宿区", address="東京都", price=1500000.0),
            models.Property(name="渋谷区", address="東京都", price=1800000.0),
            models.Property(name="池袋区", address="東京都", price=1200000.0),
        ]
        db.add_all(properties)
        db.commit()

        response = client.get("/properties/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("id" in item for item in data)
        assert all("name" in item for item in data)
        assert all("address" in item for item in data)
        assert all("price" in item for item in data)

    def test_get_properties_with_limit(self, test_client_with_db):
        """Test pagination with custom limit."""
        db = test_client_with_db["db"]
        client = test_client_with_db["client"]

        # Create 10 properties
        for i in range(10):
            prop = models.Property(name=f"区{i}", address="東京都", price=float(i * 100000))
            db.add(prop)
        db.commit()

        response = client.get("/properties/?limit=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_get_properties_with_skip(self, test_client_with_db):
        """Test pagination with skip offset."""
        db = test_client_with_db["db"]
        client = test_client_with_db["client"]

        # Create 10 properties
        for i in range(10):
            prop = models.Property(name=f"区{i}", address="東京都", price=float(i * 100000))
            db.add(prop)
        db.commit()

        response = client.get("/properties/?skip=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5  # Remaining 5 after skipping first 5

    def test_get_properties_skip_beyond_total(self, test_client_with_db):
        """Test skip beyond total number of properties."""
        db = test_client_with_db["db"]
        client = test_client_with_db["client"]

        # Create 5 properties
        for i in range(5):
            prop = models.Property(name=f"区{i}", address="東京都", price=float(i * 100000))
            db.add(prop)
        db.commit()

        response = client.get("/properties/?skip=10")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_properties_utf8_response(self, test_client_with_db):
        """Test that response properly handles UTF-8 Japanese characters."""
        db = test_client_with_db["db"]
        client = test_client_with_db["client"]

        # Create property with Japanese text
        prop = models.Property(
            name="東京都千代田区",
            address="東京都",
            price=3862500.0
        )
        db.add(prop)
        db.commit()

        response = client.get("/properties/")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json; charset=utf-8"
        data = response.json()
        assert data[0]["name"] == "東京都千代田区"
        assert data[0]["address"] == "東京都"


@pytest.mark.integration
class TestGetPropertyByIdEndpoint:
    """Test cases for GET /properties/{property_id} endpoint."""

    def test_get_property_by_id_success(self, test_client_with_db):
        """Test getting a specific property by ID."""
        db = test_client_with_db["db"]
        client = test_client_with_db["client"]

        # Create a property
        prop = models.Property(name="新宿区", address="東京都", price=1500000.0)
        db.add(prop)
        db.commit()
        db.refresh(prop)
        property_id = prop.id

        response = client.get(f"/properties/{property_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == property_id
        assert data["name"] == "新宿区"
        assert data["address"] == "東京都"
        assert data["price"] == 1500000.0

    def test_get_property_not_found(self, test_client_with_db):
        """Test getting a property that doesn't exist."""
        client = test_client_with_db["client"]
        response = client.get("/properties/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Property not found"

    def test_get_property_utf8_response(self, test_client_with_db):
        """Test UTF-8 response for single property."""
        db = test_client_with_db["db"]
        client = test_client_with_db["client"]

        prop = models.Property(
            name="東京都千代田区",
            address="東京都",
            price=3862500.0
        )
        db.add(prop)
        db.commit()
        db.refresh(prop)
        property_id = prop.id

        response = client.get(f"/properties/{property_id}")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json; charset=utf-8"
        data = response.json()
        assert data["name"] == "東京都千代田区"

    def test_api_special_characters_in_data(self, test_client_with_db):
        """Test API with special characters in data."""
        db = test_client_with_db["db"]
        client = test_client_with_db["client"]

        prop = models.Property(
            name="特殊文字区!@#$%^&*()",
            address="東京都🗼",
            price=1000000.0
        )
        db.add(prop)
        db.commit()
        db.refresh(prop)
        property_id = prop.id

        response = client.get(f"/properties/{property_id}")
        assert response.status_code == 200
        data = response.json()
        assert "特殊文字区!@#$%^&*()" in data["name"]
        assert "🗼" in data["address"]

    def test_api_float_price_precision(self, test_client_with_db):
        """Test that API preserves price precision."""
        db = test_client_with_db["db"]
        client = test_client_with_db["client"]

        prop = models.Property(
            name="精密区",
            address="東京都",
            price=1234567.89
        )
        db.add(prop)
        db.commit()
        db.refresh(prop)
        property_id = prop.id

        response = client.get(f"/properties/{property_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["price"] == 1234567.89
