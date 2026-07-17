# FinSight API

FinSight API is a Python backend for a personal finance application. It provides APIs for managing users, transaction categories, financial accounts, and transactions, and it also includes an AI-driven flow that can interpret natural language and convert it into structured finance actions.

The project is built as a modular backend with a layered architecture. Its goal is to keep business logic organized, isolate infrastructure concerns, and make finance features easier to extend over time.

## Application Purpose

The main purpose of this application is to support personal finance operations such as:

- managing users
- organizing transaction categories
- managing financial accounts
- recording financial transactions
- enabling AI-assisted transaction input from chat-style messages

In practical terms, the application is designed to let a user say something like a spending statement in natural language, then route that request through an AI orchestrator and convert it into a structured transaction entry.

## Architecture Overview

The codebase follows a modular monolith approach with layered responsibilities inside each module.

Core ideas behind the architecture:

- business features are grouped by module
- each module keeps HTTP handling separate from business logic
- persistence logic is separated from use-case logic
- shared infrastructure such as configuration and database access lives in a common layer

## High-Level Structure

```text
app/
  main.py
  shared/
    config.py
    database.py
    security.py
  modules/
    users/
      domain/
      service_layer/
      adapters/
      entrypoints/
    transactions/
      domain/
      service_layer/
      adapters/
      entrypoints/
    ai/
      application/
      service_layer/
      adapters/
      providers/
      tools/
      entrypoints/
alembic/
scripts/
docs/
```

## Layer Responsibilities

### Entrypoints

Located in `app/modules/*/entrypoints/`.

This layer is responsible for:

- defining FastAPI routes
- receiving and validating HTTP requests
- resolving dependencies
- calling the appropriate services
- returning HTTP responses

Examples:

- `app/modules/users/entrypoints/api.py`
- `app/modules/transactions/entrypoints/api.py`
- `app/modules/ai/entrypoints/api.py`

### Service Layer

Located in `app/modules/*/service_layer/`.

This layer contains application use cases and business workflows. It coordinates repositories and enforces business rules without depending directly on HTTP details.

Examples:

- user management logic
- transaction category management
- financial account management
- transaction creation
- AI-related supporting services such as embeddings or vector store operations

### Domain

Located in `app/modules/*/domain/`.

This layer contains the main business data models used by the application, including request and response schemas for module-level operations.

Examples:

- user schemas
- transaction category schemas
- financial account schemas
- transaction schemas

### Adapters

Located in `app/modules/*/adapters/`.

This layer connects the application to external or infrastructure concerns such as the database. It contains ORM models and repository implementations.

Examples:

- SQLAlchemy ORM models
- repository classes for CRUD operations

### Shared Infrastructure

Located in `app/shared/`.

This layer contains reusable infrastructure used across modules:

- application settings and environment loading
- database engine and session dependency
- password hashing and verification helpers

## Main Modules

### Users Module

Handles user-related operations such as:

- create user
- list users
- retrieve a user by ID
- update user
- soft delete user

### Transactions Module

Handles finance data management, including:

- transaction categories
- financial accounts
- transaction records
- supporting transaction persistence

This is the central business module for the finance domain.

### AI Module

Handles AI-assisted finance interactions.

The current AI flow is centered around a finance orchestrator that:

- receives a chat message from the user
- sends the message to an LLM provider
- decides whether a tool should be called
- executes a transaction creation tool when appropriate
- returns either a conversational response or a tool execution result

This module is designed to bridge natural language input and structured finance operations.

## Request Flow

A typical HTTP request follows this path:

1. A client sends a request to a FastAPI endpoint.
2. The endpoint in the `entrypoints` layer validates input and resolves dependencies.
3. The endpoint calls a service from the `service_layer`.
4. The service executes business logic.
5. If persistence is needed, the service calls a repository in `adapters`.
6. The repository uses SQLAlchemy ORM models and the shared database session.
7. The result is returned back through the service and then the API response.

The AI route adds one more orchestration step:

1. The client sends a message to `/ai/chat`.
2. The AI orchestrator builds a system prompt and user message payload.
3. The configured LLM provider evaluates the request.
4. If a supported tool call is returned, the tool handler executes a finance operation.
5. The API returns the final structured result.

## Technology Stack

- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL via `psycopg`
- Pydantic
- `pydantic-settings`
- `pwdlib` for password hashing
- AI provider integration through Groq

## Configuration

Application settings are loaded from `.env` through `pydantic-settings`.

Important configuration values include:

- `APP_NAME`
- `DATABASE_URL`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `GROQ_API_KEY`
- `GROQ_MODEL`

## Running the Project

### 1. Create a virtual environment

```powershell
python -m venv .venv
```

### 2. Activate the environment

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file with the required settings, for example:

```env
APP_NAME=FinSight API
DATABASE_URL=postgresql+psycopg://postgres:password@127.0.0.1:5142/finsight_ai
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
SECRET_KEY=your-secret-key
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile
```

### 5. Run database migrations

```powershell
alembic upgrade head
```

### 6. Seed initial data

```powershell
python scripts\seed.py
```

### 7. Start the API server

```powershell
uvicorn app.main:app --reload
```

## API Entry Points

After the server starts, the main URLs are:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Summary

FinSight API is a modular personal finance backend that combines standard CRUD-based financial management with an AI orchestration layer. Its architecture is intended to keep the application maintainable by separating HTTP concerns, business logic, persistence, and shared infrastructure into clear layers.
