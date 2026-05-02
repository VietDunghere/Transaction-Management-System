# Transaction Management System - Backend

FastAPI backend service for the Banking Transaction Management System. Handles transaction processing, AI fraud detection, loan scoring, and data warehouse synchronization.

## System Requirements

- **Python**: 3.9+ (Recommended: 3.11 LTS or 3.12)
- **Package Manager**: pip
- **Oracle Database**: 19c+ (or Oracle XE)
- **OS**: Windows, macOS, Linux
- **RAM**: 4GB minimum (8GB recommended for ML model training)

## Installation & Setup

### 1. Clone Repository and Create Virtual Environment

```bash
# Clone repository
git clone <repository-url>
cd Transaction-Management-System/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

### 3. Configure Environment Variables

Create `.env` file in the `backend/` directory:

```env
# Application
APP_NAME=Transaction Management System Backend
APP_VERSION=1.0.0
DEBUG=False
LOG_LEVEL=INFO

# Database Configuration
DB_DRIVER=oracle+oracledb
DB_USER=system
DB_PASSWORD=<your-password>
DB_HOST=localhost
DB_PORT=1521
DB_SID=xe
DB_THIN_MODE=True

# JWT Authentication
SECRET_KEY=<generate-a-strong-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_PREFIX=/api/v1
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Machine Learning
ML_MODEL_PATH=./ml_models
FRAUD_SCORE_THRESHOLD=0.5
LOAN_PD_THRESHOLD=0.3

# Logging
STRUCTLOG_LEVEL=INFO

# External Services (if needed)
EXTERNAL_API_TIMEOUT=30
```

> **Note**: `.env` file should NOT be committed to git. Add it to `.gitignore`.

### 4. Setup Database

```bash
# Run migrations to create schema
alembic upgrade head

# (Optional) Seed sample data
python seed.py
```

## Development Commands

### Run Development Server

```bash
# Start FastAPI dev server with auto-reload
uvicorn main:app --reload --port 8000

# Server runs at http://localhost:8000
# API docs available at http://localhost:8000/docs (Swagger)
# ReDoc available at http://localhost:8000/redoc
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "migration description"

# Apply pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Machine Learning

```bash
# Train/retrain fraud detection model
python train_loan_model.py

# Output: ml_models/loan_model.pkl
```

### Testing

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py

# Run tests with coverage report
pytest --cov=app --cov-report=html

# Watch mode (auto-run on file changes)
pytest-watch
```

### Code Quality

```bash
# Type checking with mypy
mypy app/

# Linting
pylint app/

# Format code with black
black app/

# Sort imports
isort app/
```

### Demo & Data Generation

```bash
# Run demo transactions
python demo_transactions.py

# Generate fake test data
python -c "from db.fake_data import generate_fake_data; generate_fake_data(100)"
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/                    # API v1 routes
│   │       ├── __init__.py
│   │       ├── analyst.py         # Analyst routes
│   │       ├── auth.py            # Authentication routes
│   │       ├── cases.py           # Case management routes
│   │       ├── dashboard.py       # Dashboard routes
│   │       ├── health.py          # Health check
│   │       ├── loans.py           # Loan routes
│   │       ├── reports.py         # Report routes
│   │       ├── transactions.py    # Transaction routes
│   │       └── users.py           # User management routes
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Settings & environment vars
│   │   ├── security.py            # JWT, password hashing
│   │   └── logging.py             # Structured logging setup
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py             # Database session management
│   │   └── base.py                # SQLAlchemy Base
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                # User model
│   │   ├── transaction.py         # Transaction model
│   │   ├── loan.py                # Loan application model
│   │   ├── audit.py               # Audit log model
│   │   └── ...
│   ├── repositories/              # Data access layer
│   ├── schemas/                   # Pydantic request/response models
│   ├── services/                  # Business logic layer
│   │   ├── auth_service.py
│   │   ├── fraud_service.py       # ML fraud detection
│   │   ├── loan_service.py        # ML loan scoring
│   │   ├── transaction_service.py
│   │   └── ...
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── exceptions.py          # Custom exceptions
│   │   ├── validators.py          # Data validation utilities
│   │   └── helpers.py
│   └── __main__.py
├── migrations/
│   ├── env.py                     # Alembic environment
│   ├── script.py.mako             # Alembic migration template
│   └── versions/                  # Migration files
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures & config
│   ├── test_auth.py
│   ├── test_transactions.py
│   ├── test_loans.py
│   ├── test_audit.py
│   └── ...
├── ml_models/
│   ├── loan_model.pkl             # Trained model (not committed)
│   └── loan_model_metadata.json   # Model metadata & hyperparameters
├── db/
│   ├── ERD.sql                    # Entity Relationship Diagram (SQL)
│   ├── Fake_data.sql              # Test data
│   └── news/                      # Database model files (Erwin)
├── docs/
│   ├── ENDPOINT_TEST_REPORT.md    # API test results
│   ├── API_DESIGN.md              # API design documentation
│   └── ...
├── main.py                        # FastAPI app entry point
├── seed.py                        # Database seeding script
├── train_loan_model.py            # ML model training script
├── demo_transactions.py           # Demo data generator
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables (not committed)
├── .env.example                   # Environment template
├── alembic.ini                    # Alembic configuration
├── docker-compose.yml             # Docker services (Oracle, etc.)
└── Dockerfile                     # Backend container
```

## Tech Stack

| Layer                   | Technology        | Version |
| ----------------------- | ----------------- | ------- |
| **Framework**           | FastAPI           | 0.111+  |
| **Server**              | Uvicorn           | 0.29+   |
| **Language**            | Python            | 3.9+    |
| **Database (OLTP)**     | Oracle DB         | 19c+    |
| **ORM**                 | SQLAlchemy        | 2.0+    |
| **Migrations**          | Alembic           | 1.13+   |
| **Auth**                | JWT (python-jose) | 3.3+    |
| **Validation**          | Pydantic          | 2.7+    |
| **ML - Classification** | scikit-learn      | 1.4+    |
| **ML - Boosting**       | XGBoost           | 2.0+    |
| **ML - Optimization**   | LightGBM          | 4.0+    |
| **ML - Tuning**         | Optuna            | 3.6+    |
| **Data Processing**     | Pandas            | 2.2+    |
| **Numerical**           | NumPy             | 1.26+   |
| **Logging**             | structlog         | 24.1+   |
| **Testing**             | Pytest            | 8.2+    |
| **Async Testing**       | pytest-asyncio    | 0.23+   |

## Key Dependencies

### Core Framework

- **FastAPI**: High-performance async API framework with auto-documentation
- **Uvicorn**: ASGI server for running FastAPI

### Database & ORM

- **SQLAlchemy**: SQL toolkit & ORM for database operations
- **oracledb**: Oracle thin mode driver (no Oracle Client installation needed)
- **Alembic**: Database migration tool

### Authentication & Security

- **python-jose**: JWT token handling
- **passlib**: Password hashing & verification
- **bcrypt**: Cryptographic password hashing

### Machine Learning

- **scikit-learn**: ML algorithms (fraud detection baseline)
- **XGBoost**: Gradient boosting for classification
- **LightGBM**: Faster boosting alternative to XGBoost
- **Optuna**: Hyperparameter optimization with Bayesian search
- **Pandas**: Data manipulation & analysis
- **NumPy**: Numerical computing

### Validation & Settings

- **Pydantic**: Data validation & schema serialization
- **pydantic-settings**: Environment variable management

### Utilities

- **structlog**: Structured logging for better log analysis
- **httpx**: Async HTTP client for testing & internal API calls
- **imbalanced-learn**: Handle imbalanced datasets in ML

### Development & Testing

- **pytest**: Test framework
- **pytest-asyncio**: Async test support

## Workflow

### Feature Development

1. **Create a feature branch**

    ```bash
    git checkout -b feature/your-feature-name
    ```

2. **Run development server**

    ```bash
    uvicorn main:app --reload
    ```

3. **API auto-documentation**
    - Open http://localhost:8000/docs for interactive Swagger UI
    - Test endpoints directly in the browser

4. **Write tests using TDD**

    ```bash
    pytest tests/test_your_feature.py -v
    ```

5. **Create database migration (if needed)**

    ```bash
    alembic revision --autogenerate -m "add new field"
    alembic upgrade head
    ```

6. **Code quality checks**

    ```bash
    pytest --cov=app
    mypy app/
    ```

7. **Commit & Push**
    ```bash
    git add .
    git commit -m "feat: add your feature"
    git push origin feature/your-feature-name
    ```

## Testing

### Unit Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_transactions.py

# Run specific test function
pytest tests/test_transactions.py::test_create_transaction

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html
```

### Test Structure

```
tests/
├── conftest.py                # Shared fixtures (DB session, mocks, etc.)
├── test_auth.py               # Authentication tests
├── test_transactions.py       # Transaction endpoint tests
├── test_loans.py              # Loan processing tests
├── test_audit.py              # Audit logging tests
└── ...
```

### Example Test

```python
# tests/test_transactions.py
import pytest
from app.schemas.transaction import TransactionCreate

@pytest.mark.asyncio
async def test_create_transaction(client, db_session):
    payload = {
        "customer_id": 123,
        "amount": 5000000,
        "transaction_type": "TRANSFER"
    }
    response = await client.post("/api/v1/transactions", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "PENDING"
```

## Troubleshooting

### Database Connection Issues

```bash
# Test Oracle connection
python -c "import oracledb; conn = oracledb.connect('system/password@localhost:1521/xe'); print('Connected!')"

# Check database configuration
cat .env | grep DB_

# Reset database (WARNING: deletes all data)
alembic downgrade base
alembic upgrade head
```

### Virtual Environment Issues

```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Import Errors

```bash
# Ensure backend is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or use python -m to run modules
python -m pytest tests/
```

### Port Already in Use

```bash
# Run on different port
uvicorn main:app --reload --port 8001

# Kill process using port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Oracle Thin Mode Issues

```bash
# Verify thin mode is working
python -c "import oracledb; print(oracledb.thin_mode)"

# If issues persist, check tnsnames.ora or use connection string:
# oracle+oracledb://user:password@hostname:1521/?service_name=xe
```

## Setup Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created & activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with database credentials
- [ ] Oracle database accessible
- [ ] Database migrations run (`alembic upgrade head`)
- [ ] Development server starts (`uvicorn main:app --reload`)
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Tests pass (`pytest`)
- [ ] No import errors (`python -c "from app import main"`)

## Running with Docker

```bash
# Build & run all services (FastAPI + Oracle)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## Deployment

### Production Build

```bash
# Install production dependencies only
pip install -r requirements.txt --no-dev

# Run with production ASGI server (Gunicorn + Uvicorn)
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables

```bash
# Use strong SECRET_KEY
openssl rand -hex 32

# Set DEBUG=False
DEBUG=False

# Use external database (not localhost)
DB_HOST=production-oracle-server
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

See [docs/API_DESIGN.md](../docs/API_DESIGN.md) for detailed endpoint documentation.

## Database Schema

- **OLTP (Operational)**: TRANSACTIONS_LIVE, USERS, CUSTOMERS, AUDIT_LOGS
- **OLAP (Analytics)**: FACT_TRANSACTIONS, DIM_TIME, DIM_CUSTOMER, DIM_LOCATION

See [docs/DATABASE_SETUP.md](../docs/DATABASE_SETUP.md) and [db/ERD.sql](./db/ERD.sql).

## ML Models

### Fraud Detection

- **Algorithm**: XGBoost / LightGBM
- **Input**: Transaction features (amount, type, customer history, etc.)
- **Output**: Fraud probability score (0-1)
- **Threshold**: 0.5 (configurable via FRAUD_SCORE_THRESHOLD)

### Loan Scoring

- **Algorithm**: XGBoost / LightGBM
- **Input**: Customer profile, income, credit history
- **Output**: Default probability (PD) score
- **Threshold**: 0.3 (configurable via LOAN_PD_THRESHOLD)

See [train_loan_model.py](./train_loan_model.py) for model training.

## Contributing

1. Follow project conventions from copilot-instructions.md
2. Write tests for all new features (TDD)
3. Ensure all tests pass: `pytest`
4. Run type checking: `mypy app/`
5. Keep commit messages descriptive
6. Submit a pull request

## Support & Resources

- [System Workflow](../docs/SYSTEM_WORKFLOW.md)
- [API Design](../docs/API_DESIGN.md)
- [Database Setup](../docs/DATABASE_SETUP.md)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Oracle DB Docs](https://oracle.github.io/python-oracledb/)
