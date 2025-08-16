# AI-Powered Recipe Finder

A FastAPI-based web application that helps users find recipes based on available ingredients. Users can create accounts, add their own recipes, and search through a database of recipes using ingredient-based queries.

## Features

- **User Authentication**: Secure signup and login with JWT tokens
- **Recipe Management**: Create, read, update, and delete recipes
- **Ingredient Search**: Find recipes based on available ingredients
- **User Ownership**: Users can manage their own recipes
- **RESTful API**: Clean, documented API endpoints
- **Database**: SQLite database with SQLAlchemy ORM

## Project Structure

```
recipe_finder/
├── backend/                 # Backend API code
│   ├── __init__.py
│   ├── main.py             # FastAPI application and endpoints
│   ├── models.py           # SQLAlchemy database models
│   ├── schemas.py          # Pydantic data validation schemas
│   ├── crud.py            # Database CRUD operations
│   ├── auth.py            # Authentication and JWT handling
│   └── database.py        # Database connection and setup
├── frontend/               # Frontend web interface
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── tests/                  # Comprehensive test suite
│   ├── __init__.py
│   ├── conftest.py        # Pytest configuration and fixtures
│   ├── test_models.py     # Database model tests
│   ├── test_schemas.py    # Pydantic schema tests
│   ├── test_auth.py       # Authentication tests
│   ├── test_crud.py       # CRUD operation tests
│   ├── test_api.py        # API endpoint tests
│   └── test_integration.py # Integration and workflow tests
├── requirements.txt        # Python dependencies
├── pytest.ini            # Pytest configuration
├── run_tests.py          # Test runner script
├── run.py                # Application entry point
└── setup.py              # Project setup
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd recipe_finder
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python run.py
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /signup` - User registration
- `POST /login` - User authentication

### Recipes
- `GET /recipes` - List all recipes (with pagination)
- `POST /recipes` - Create a new recipe
- `GET /recipes/{recipe_id}` - Get a specific recipe
- `PUT /recipes/{recipe_id}` - Update a recipe (owner only)
- `DELETE /recipes/{recipe_id}` - Delete a recipe (owner only)

### Search
- `GET /search?q=ingredient1,ingredient2` - Search recipes by ingredients

## Testing

This project includes a comprehensive test suite with **90%+ coverage** target. The tests cover:

- **Unit Tests**: Individual functions and methods
- **Integration Tests**: Complete workflows and API interactions
- **Model Tests**: Database models and relationships
- **Schema Tests**: Data validation and serialization
- **Authentication Tests**: JWT tokens and password handling
- **CRUD Tests**: Database operations
- **API Tests**: HTTP endpoints and error handling

### Running Tests

#### Quick Start
```bash
# Install test dependencies
python run_tests.py install

# Run all tests with coverage
python run_tests.py coverage

# Run specific test types
python run_tests.py unit        # Unit tests only
python run_tests.py integration # Integration tests only
python run_tests.py all         # All tests
```

#### Manual Test Execution
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/test_models.py -v

# Run specific test class
pytest tests/test_models.py::TestUserModel -v

# Run specific test method
pytest tests/test_models.py::TestUserModel::test_create_user -v

# Run tests matching a pattern
pytest -k "user" -v

# Run tests with detailed output
pytest -v -s
```

### Test Coverage

The test suite provides comprehensive coverage:

- **Models**: Database models, relationships, and constraints
- **Schemas**: Pydantic validation and data transformation
- **Authentication**: Password hashing, JWT creation/validation
- **CRUD Operations**: All database operations with edge cases
- **API Endpoints**: HTTP methods, status codes, error handling
- **Integration**: Complete user workflows and data persistence
- **Edge Cases**: Special characters, large data, concurrent operations

### Test Configuration

The project uses `pytest.ini` for configuration:
- Coverage target: 90%
- HTML and XML coverage reports
- Automatic test discovery
- Warning filters

### Test Database

Tests use a temporary SQLite database that is:
- Created fresh for each test session
- Isolated from the main application database
- Automatically cleaned up after tests complete

## Development

### Adding New Tests

1. **Create test file** in the `tests/` directory
2. **Follow naming convention**: `test_<module_name>.py`
3. **Use descriptive test names**: `test_<functionality>_<scenario>`
4. **Include edge cases** and error scenarios
5. **Maintain coverage** above 90%

### Test Structure

```python
class TestFeatureName:
    """Test cases for specific feature."""
    
    def test_scenario_description(self, fixture_name):
        """Test description explaining what is being tested."""
        # Arrange
        # Act
        # Assert
```

### Running Tests During Development

```bash
# Watch for changes and run tests automatically
pytest-watch

# Run tests in parallel (faster execution)
pytest -n auto

# Generate coverage badge
pytest --cov=backend --cov-report=xml
```

## Contributing

1. **Write tests** for new features
2. **Maintain test coverage** above 90%
3. **Follow test naming conventions**
4. **Include integration tests** for complex workflows
5. **Test edge cases** and error conditions

## License

This project is licensed under the MIT License - see the LICENSE file for details.
