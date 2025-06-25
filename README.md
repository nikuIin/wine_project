# Vino Project Backend

This is the backend service for the Vino project, built with FastAPI and utilizing JWT for authentication.

### Features

*   **JWT Authentication:** Secure user authentication and authorization using JSON Web Tokens.
*   **User Registration and Login:** Allows users to register and log in to the system.
*   **Token Refreshing:** Provides token refreshing mechanism to extend user sessions securely.
*   **Protected Routes:** Demonstrates how to protect routes using JWT authentication.
*   **Asynchronous Database Interaction:** Uses SQLAlchemy with asyncpg for asynchronous database operations.
*   **Dependency Injection:** Leverages FastAPI's dependency injection system for modular and testable code.
*   **Configuration with Pydantic:** Uses Pydantic for environment variable parsing and configuration management.
*   **Logging:** Implements structured logging for easier debugging and monitoring.
*   **Testing:** Includes comprehensive unit tests.

### Prerequisites

*   Python 3.13+
*   Docker (optional, for database)
*   A PostgreSQL database (can be local or remote)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd backend
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    # .\.venv\Scripts\activate  # Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r pyproject.toml
    ```

4.  **Set up the database:**

    *   Create a PostgreSQL database.  You can use Docker for this:

        ```bash
        docker run --name postgres -e POSTGRES_USER=root -e POSTGRES_PASSWORD=root -e POSTGRES_DB=db -p 5432:5432 postgres:latest
        ```

    *   Update the database connection settings in the `.env` file (create it if it doesn't exist):

        ```
        DB_TYPE=postgresql
        DB_HOST=localhost
        DB_PORT=5432
        DB_USER=root
        DB_PASSWORD=root
        DB_NAME=db
        ```

5.  **Run database migrations:**

    ```bash
    uv run alembic upgrade head
    ```

### Running the Application

1.  **Start the application:**

    ```bash
    uvicorn src.main:app --reload
    ```

    This will start the FastAPI application, and `--reload` enables automatic reloading on code changes.

### API Endpoints

*   `/api/v1/auth/token/` (POST):  Get JWT tokens (login).  Requires `login` and `password` in the request body.
*   `/api/v1/auth/register/` (POST): Register a new user. Requires `login` and `password` in the request body.
*   `/api/v1/auth/refresh/` (POST):  Refresh JWT tokens.  Requires a valid refresh token in a cookie.
*   `/api/v1/auth/protected` (GET): Protected endpoint (requires a valid access token in a cookie).

### Testing

1.  **Run unit tests:**

    ```bash
    uv run pytest
    ```

    or to see the coverage:
        ```bash
        uv run pytest --cov=./src
        ```

### Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py          # API router
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── depends.py      # Dependencies
│   │       ├── endpoints/
│   │       │   └── auth.py     # Authentication endpoints
│   │       └── routes.py      # Version 1 routes
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration settings
│   │   ├── general_constants.py
│   │   ├── logger/
│   │   │   ├── __init__.py
│   │   │   ├── filters.py      # Custom filters
│   │   │   └── logger.py      # Logger configuration
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base_models.py     # Base model
│   │   ├── dependencies/
│   │   │   └── postgres_helper.py
│   │   └── models.py          # Database models
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── auth_master.py # Auth management
│   │   │   ├── token.py        # Token entities
│   │   │   └── user.py         # User entities
│   │   └── exceptions.py      # Custom exceptions
│   ├── main.py                # Main application entry point
│   ├── repository/
│   │   ├── __init__.py
│   │   ├── sql_queries/
│   │   │   ├── token_queries.py
│   │   │   └── user_queries.py
│   │   ├── token_repository.py # Token repository
│   │   └── user_repository.py  # User repository
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── token_schema.py    # Token schemas
│   │   └── user_schema.py     # User schemas
│   └── use_cases/
│       ├── __init__.py
│       ├── token_service.py   # Token service
│       └── user_service.py    # User service
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest configurations
│   └── unit/
│       ├── __init__.py
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── entities/
│       │   │   └── conftest.py
│       │   └── token_test.py
├── .env                     # Environment variables
├── .gitignore
├── alembic.ini              # Alembic configuration
├── Makefile                 # Makefile for common tasks
├── pyproject.toml           # Project dependencies
├── pytest.ini               # Pytest configuration
└── README.md                # This file
```

### Contributing

Contributions are welcome!  Please feel free to submit pull requests.
