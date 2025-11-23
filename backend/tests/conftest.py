"""
Pytest configuration and shared fixtures for all tests.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Base
from main import app
import models


# ========================================
# Database Fixtures
# ========================================

@pytest.fixture(scope="function")
def test_db_engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """Create a database session for testing."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine
    )
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def test_client(test_db_engine):
    """Create a FastAPI test client with test database."""
    def override_get_db():
        TestingSessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=test_db_engine
        )
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Override the database dependency
    from database import SessionLocal
    original_session = SessionLocal

    client = TestClient(app)
    yield client

    # Restore original
    SessionLocal = original_session


# ========================================
# Test Data Fixtures
# ========================================

@pytest.fixture
def sample_property_data():
    """Sample property data for testing."""
    return {
        "name": "新宿区",
        "address": "東京都",
        "price": 1500000.0
    }


@pytest.fixture
def sample_properties_data():
    """Multiple sample properties for testing."""
    return [
        {"name": "新宿区", "address": "東京都", "price": 1500000.0},
        {"name": "渋谷区", "address": "東京都", "price": 1800000.0},
        {"name": "千代田区", "address": "東京都", "price": 3862500.0},
        {"name": "横浜市", "address": "神奈川県", "price": 500000.0},
        {"name": "さいたま市", "address": "埼玉県", "price": 300000.0},
    ]


@pytest.fixture
def create_test_property(test_db_session):
    """Factory fixture to create test properties in database."""
    def _create_property(**kwargs):
        defaults = {
            "name": "テスト区",
            "address": "東京都",
            "price": 1000000.0
        }
        defaults.update(kwargs)

        property_obj = models.Property(**defaults)
        test_db_session.add(property_obj)
        test_db_session.commit()
        test_db_session.refresh(property_obj)
        return property_obj

    return _create_property


@pytest.fixture
def seed_test_properties(test_db_session, sample_properties_data):
    """Seed the test database with multiple properties."""
    properties = []
    for data in sample_properties_data:
        property_obj = models.Property(**data)
        test_db_session.add(property_obj)
        properties.append(property_obj)

    test_db_session.commit()
    for prop in properties:
        test_db_session.refresh(prop)

    return properties
