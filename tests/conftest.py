import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from backend.database import Base
from backend.main import app, get_db
from backend import models, crud, auth
from backend.schemas import UserCreate


@pytest.fixture(scope="session")
def test_db():
    """Create a test database for the test session."""
    # Create a temporary database file
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix='.db')
    os.close(temp_db_fd)
    
    # Create test database engine
    test_db_url = f"sqlite:///{temp_db_path}"
    test_engine = create_engine(
        test_db_url, connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    yield test_engine
    
    # Cleanup
    os.unlink(temp_db_path)


@pytest.fixture
def db_session(test_db):
    """Create a new database session for each test."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        # Clean up all data after each test
        session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()


@pytest.fixture
def client(db_session):
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user for authentication tests."""
    user_data = UserCreate(username="testuser", password="testpass123")
    hashed_password = auth.get_password_hash(user_data.password)
    user = crud.create_user(db_session, user_data.username, hashed_password)
    return user


@pytest.fixture
def test_user_token(test_user):
    """Create a test user access token."""
    return auth.create_access_token({"sub": test_user.username})


@pytest.fixture
def test_recipe(db_session, test_user):
    """Create a test recipe for testing."""
    recipe = crud.create_recipe(
        db_session,
        title="Test Recipe",
        description="A test recipe for testing",
        image_url="https://example.com/image.jpg",
        ingredient_names=["tomato", "cheese", "bread"],
        owner_id=test_user.id
    )
    return recipe


@pytest.fixture
def test_ingredients(db_session):
    """Create test ingredients for testing."""
    ingredients = []
    ingredient_names = ["tomato", "cheese", "bread", "milk", "eggs"]
    for name in ingredient_names:
        ingredient = crud.create_or_get_ingredient(db_session, name)
        ingredients.append(ingredient)
    return ingredients
