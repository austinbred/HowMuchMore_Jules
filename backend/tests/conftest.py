import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Assuming your main FastAPI app and Base are here:
# Adjust paths as necessary if your app/Base structure is different.
# These imports need to resolve correctly from the backend/tests directory.
# This implies that the 'backend' directory itself might need to be in PYTHONPATH for tests to run,
# or tests are run with `python -m pytest` from the `backend` directory.
from ..app.main import app # The FastAPI application instance
from ..app.database import Base, get_db # The SQLAlchemy Base and original get_db dependency

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL_TEST = "sqlite:///:memory:" # In-memory SQLite for tests

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL_TEST,
    connect_args={"check_same_thread": False} # Needed for SQLite
)
SessionLocal_test = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

# Fixture to create tables for each test function (or session)
@pytest.fixture(scope="function") # Use "session" scope if tables can persist across tests
def setup_database():
    Base.metadata.create_all(bind=engine_test) # Create tables
    yield
    Base.metadata.drop_all(bind=engine_test)   # Drop tables after tests

# Fixture for a test database session
@pytest.fixture
def db_session(setup_database: None) -> Generator[Session, None, None]:
    """Yields a SQLAlchemy session for a test. Rolls back changes after test."""
    # `setup_database` fixture ensures tables are created and dropped.
    db = SessionLocal_test()
    try:
        yield db
    finally:
        db.rollback() # Ensure changes are rolled back if not committed (though typically tests shouldn't commit)
        db.close()

# --- TestClient Setup ---
@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Provides a TestClient instance for API testing, with get_db dependency overridden.
    """

    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            # Session is managed by db_session fixture
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up dependency override after test
    del app.dependency_overrides[get_db]

# --- Mock Authentication (Placeholder) ---
# You'll likely need a fixture to mock `get_current_active_user`
# For example:
# @pytest.fixture
# def mock_auth_user(mocker): # Assuming pytest-mock is available or use unittest.mock
#     mock_user_data = {"email": "testuser@example.com", "username": "testuser", "is_active": True}
#     # This path needs to be the *actual path to where get_current_active_user is imported in your endpoint files*
#     # e.g., "backend.app.api.endpoints.user.get_current_active_user"
#     # For now, this is a conceptual placeholder.
#     # You'd use mocker.patch('path.to.get_current_active_user', return_value=mock_user_data)
#     # The actual mocking will be done in specific test files or a more sophisticated fixture.
#     pass
