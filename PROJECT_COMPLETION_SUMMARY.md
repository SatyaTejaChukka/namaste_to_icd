# AYUSH Terminology Service

A FastAPI-based web service for mapping traditional Indian medical terminology (Ayurveda, Siddha, and Unani) to standardized ICD-11 codes. This service provides FHIR-compliant endpoints for healthcare interoperability.

## Features

- **Multi-system support**: Handles Ayurveda, Siddha, and Unani medical terminologies
- **ICD-11 mapping**: Maps traditional medical terms to WHO ICD-11 classification codes
- **FHIR compliance**: Implements FHIR R4 standard endpoints for healthcare integration
- **Cross-system search**: Unified search across all three traditional medical systems
- **Real-time analytics**: Provides statistics and insights on terminology usage
- **Async architecture**: Built with asynchronous FastAPI for high performance

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Git

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd namaste_to_icd
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Configure database connection in `Dbconnect/dbconnect.py`

4. Load the terminology data:
```bash
python corrected_data_loader.py
```

## Architecture

### Database Structure

The service uses a PostgreSQL database with the following structure:

- **ayurveda_terms** (2,888 records) - Ayurveda terminology
- **siddha_terms** (1,926 records) - Siddha terminology  
- **unani_terms** (2,522 records) - Unani terminology
- **icd11_codes** (35,339 records) - WHO ICD-11 classification codes
- **mapping tables** (19,981 total mappings) - System-specific ICD-11 mappings

### Backend Components

- `main.py` - FastAPI application and API endpoints
- `database.py` - Async SQLAlchemy database configuration
- `models.py` - Database models for each medical system
- `schemas.py` - Pydantic models for API responses
- `services/` - Business logic layer
  - `terminology_service.py` - Terminology operations
  - `mapping_service.py` - ICD-11 mapping functionality
  - `statistics_service.py` - Analytics and statistics

## Usage

### Starting the Server

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### Health Check
```http
GET /health
```

#### Search Terminology
```http
GET /api/search?q=disease&system=ayurveda
```

#### FHIR Lookup
```http
GET /fhir/CodeSystem/$lookup?system=ayurveda&code=AYU001
```

#### Get Statistics
```http
GET /api/statistics
```

#### Validate Code
```http
GET /api/validate/{system}/{code}
```

## Data

The service contains comprehensive terminology data:

- **Ayurveda**: 2,888 terms with 6,807 ICD mappings
- **Siddha**: 1,926 terms with 5,624 ICD mappings  
- **Unani**: 2,522 terms with 7,550 ICD mappings
- **ICD-11**: 35,339 classification codes

## Project Structure

```
backend/
├── main.py                    # FastAPI application
├── database.py               # Database configuration
├── models.py                 # Database models
├── schemas.py                # API response schemas
├── requirements.txt          # Python dependencies
├── corrected_data_loader.py  # Data loading utility
├── services/
│   ├── terminology_service.py
│   ├── mapping_service.py
│   └── statistics_service.py
└── Dbconnect/
    ├── *.csv                 # Terminology data files
    └── dbconnect.py          # Database connection config
```

## Dependencies

Key dependencies include:

- `fastapi` - Web framework
- `sqlalchemy` - Database ORM with async support
- `asyncpg` - PostgreSQL async driver
- `pandas` - Data processing
- `uvicorn` - ASGI server
