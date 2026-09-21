# Candidate Tracker API

A small FastAPI CRUD service for managing candidate information.

The API supports creating, viewing, updating, and deleting candidates. It uses Pydantic for request validation, SQLAlchemy as the ORM, PostgreSQL for data persistence, Alembic for database migrations, Docker Compose for local development, and JWT-based authentication.

## Features

- Create candidates
- View all candidates
- View a single candidate
- Update candidate information
- Delete candidates
- Validate email addresses
- Validate Nigerian phone numbers
- Persist candidate data in PostgreSQL
- Manage database schema with Alembic migrations
- Model relationships between candidates and applications
- User registration and authentication
- JWT-based protected endpoints
- Password hashing
- Rate limiting
- Global exception handling
- Interactive API documentation with Swagger/OpenAPI
- Automated tests with pytest
- Docker containerization
- Docker Compose setup with PostgreSQL
- Railway deployment

## Requirements

- Python 3.11+
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Alembic
- Docker Desktop
- Docker Compose
- python-dotenv
- pytest
- httpx
- email-validator

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/EbunAw/week2-candidate-tracker-api.git
cd week2-candidate-tracker-api