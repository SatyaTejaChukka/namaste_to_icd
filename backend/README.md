# AYUSH Terminology Backend - Comprehensive Documentation

## Overview

The AYUSH Terminology Backend is a FastAPI-based REST API service that provides FHIR R4 compliant interoperability between traditional Indian medical systems (Ayurveda, Siddha, Unani) and international healthcare standards (ICD-11). This backend implements terminology search, concept mapping, and clinical translation services for healthcare providers transitioning between traditional and modern medical practice.

## Quick Start

### Environment Setup

1. **Copy environment configuration:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file with your database credentials:**
   ```env
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=hackathon_db
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Load data (if needed):**
   ```bash
   python corrected_data_loader.py
   ```

5. **Start the server:**
   ```bash
   python start_server.py
   # or
   python main.py
   ```

## System Architecture

### Technology Stack
- **Framework**: FastAPI 0.104.1 with automatic OpenAPI documentation
- **Database**: SQLAlchemy 2.0.23 with async support (SQLite for development, PostgreSQL production-ready)
- **Validation**: Pydantic 2.5.0 for request/response validation and FHIR compliance
- **Authentication**: JWT tokens with python-jose (prepared for future implementation)
- **Testing**: Pytest with async support
- **Standards Compliance**: FHIR R4 CodeSystem and ConceptMap resources

### Core Components

```
backend/
├── main.py                     # FastAPI application with 12 endpoints
├── models.py                   # SQLAlchemy database models (9 tables)
├── schemas.py                  # Pydantic validation schemas for FHIR compliance
├── database.py                 # Async database configuration and session management
├── services/                   # Business logic layer
│   ├── terminology_service.py  # AYUSH concept search and FHIR operations
│   ├── mapping_service.py      # AYUSH-ICD11 mappings and translation
│   └── statistics_service.py   # Analytics and metrics generation
└── requirements.txt            # Python dependencies
```

## Database Schema and Tables

The system uses SQLAlchemy ORM with async support to manage terminology data across traditional Indian medical systems and their mappings to ICD-11 standards. The database design follows domain separation principles with individual tables for each AYUSH system.

### Core Terminology Tables

#### 1. AYUSH System Tables (Domain Separation)

**ayurveda_terms**
```sql
CREATE TABLE ayurveda_terms (
    id INTEGER PRIMARY KEY,
    code VARCHAR UNIQUE NOT NULL,    -- Unique Ayurveda concept identifier  
    term VARCHAR NOT NULL,           -- English display name
    system VARCHAR DEFAULT 'Ayurveda' NOT NULL
);
```
- **Purpose**: Stores authentic Ayurveda terminology concepts
- **Indexes**: Primary key (id), unique index (code) for fast lookups
- **Data Source**: Classical texts like Charaka Samhita, Sushruta Samhita
- **Example**: code='AYU_001', term='Vata Dosha Imbalance'

**siddha_terms**
```sql
CREATE TABLE siddha_terms (
    id INTEGER PRIMARY KEY,
    code VARCHAR UNIQUE NOT NULL,    -- Unique Siddha concept identifier
    term VARCHAR NOT NULL,           -- English display name  
    system VARCHAR DEFAULT 'Siddha' NOT NULL
);
```
- **Purpose**: Stores traditional Siddha medicine terminology
- **Indexes**: Primary key (id), unique index (code) for fast lookups
- **Data Source**: Traditional Siddha diagnostic categories
- **Example**: code='SID_001', term='Vali Noi (Wind-related disorder)'

**unani_terms**
```sql
CREATE TABLE unani_terms (
    id INTEGER PRIMARY KEY,
    code VARCHAR UNIQUE NOT NULL,    -- Unique Unani concept identifier
    term VARCHAR NOT NULL,           -- English display name
    system VARCHAR DEFAULT 'Unani' NOT NULL  
);
```
- **Purpose**: Stores classical Unani medicine terminology
- **Indexes**: Primary key (id), unique index (code) for fast lookups
- **Data Source**: Traditional Unani diagnostic classifications
- **Example**: code='UNA_001', term='Suda (Headache due to temperament imbalance)'

#### 2. ICD-11 Reference Table

**icd11_codes**
```sql
CREATE TABLE icd11_codes (
    id INTEGER PRIMARY KEY,
    code VARCHAR UNIQUE NOT NULL,           -- Official ICD-11 code
    title VARCHAR NOT NULL,                 -- ICD-11 official title
    is_tm2_module VARCHAR DEFAULT 'false'   -- Traditional Medicine Module 2 flag
);
```
- **Purpose**: Stores WHO ICD-11 classification codes with TM2 module focus
- **Indexes**: Primary key (id), unique index (code) for standard lookups
- **TM2 Module**: Special focus on Traditional Medicine Module 2 codes
- **Example**: code='QA02.Y', title='Traditional medicine conditions, unspecified'

### Cross-System Mapping Tables

#### 3. AYUSH to ICD-11 Mapping Tables

**ayurveda_icd_mappings**
```sql
CREATE TABLE ayurveda_icd_mappings (
    id INTEGER PRIMARY KEY,
    ayurveda_code VARCHAR NOT NULL,     -- Reference to ayurveda_terms.code
    ayurveda_term VARCHAR NOT NULL,     -- Cached Ayurveda term for performance
    icd_code VARCHAR,                   -- Reference to icd11_codes.code  
    icd_term VARCHAR,                   -- Cached ICD-11 title for performance
    match_type VARCHAR                  -- Equivalence type (Exact|Narrow|Broad)
);
```
- **Purpose**: Maps Ayurveda concepts to ICD-11 classifications
- **Indexes**: ayurveda_code, icd_code for join performance
- **Match Types**: 'Exact' (direct equivalent), 'Narrow' (more specific), 'Broad' (more general)
- **Performance**: Denormalized design with cached terms to avoid joins

**siddha_icd_mappings**
```sql
CREATE TABLE siddha_icd_mappings (
    id INTEGER PRIMARY KEY,
    siddha_code VARCHAR NOT NULL,       -- Reference to siddha_terms.code
    siddha_term VARCHAR NOT NULL,       -- Cached Siddha term
    icd_code VARCHAR,                   -- Reference to icd11_codes.code
    icd_term VARCHAR,                   -- Cached ICD-11 title  
    match_type VARCHAR                  -- Equivalence type
);
```
- **Purpose**: Maps Siddha concepts to ICD-11 classifications
- **Design Pattern**: Identical structure to Ayurveda mappings for consistency
- **Clinical Validation**: Expert-reviewed mappings with confidence indicators

**unani_icd_mappings**
```sql
CREATE TABLE unani_icd_mappings (
    id INTEGER PRIMARY KEY,
    unani_code VARCHAR NOT NULL,        -- Reference to unani_terms.code
    unani_term VARCHAR NOT NULL,        -- Cached Unani term
    icd_code VARCHAR,                   -- Reference to icd11_codes.code
    icd_term VARCHAR,                   -- Cached ICD-11 title
    match_type VARCHAR                  -- Equivalence type  
);
```
- **Purpose**: Maps Unani concepts to ICD-11 classifications
- **Consistency**: Follows same mapping pattern as other AYUSH systems
- **Traditional Context**: Preserves Unani diagnostic principles in mappings

### Operational and Management Tables

#### 4. Clinical Encounter Processing

**encounter_records**
```sql
CREATE TABLE encounter_records (
    id INTEGER PRIMARY KEY,
    encounter_id VARCHAR NOT NULL,      -- External encounter reference
    patient_id VARCHAR NOT NULL,        -- External patient reference
    ayush_codes VARCHAR NOT NULL,       -- Comma-separated AYUSH codes
    icd11_codes VARCHAR,               -- Auto-generated ICD-11 codes
    fhir_bundle JSON NOT NULL,         -- Complete FHIR Bundle data
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```
- **Purpose**: Stores clinical encounters with dual AYUSH-ICD11 coding
- **FHIR Integration**: Complete Bundle resources for interoperability
- **Indexes**: encounter_id, patient_id for clinical queries
- **Data Format**: JSON for flexible FHIR resource storage

#### 5. Version Management

**terminology_versions**
```sql
CREATE TABLE terminology_versions (
    id INTEGER PRIMARY KEY,
    terminology_type VARCHAR NOT NULL,  -- System type (ayurveda|siddha|unani|icd11)
    version VARCHAR NOT NULL,           -- Semantic version number
    release_date DATETIME NOT NULL,     -- Version release timestamp
    description TEXT,                   -- Version change description
    is_active VARCHAR DEFAULT 'true',   -- Current active version flag
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```
- **Purpose**: Tracks terminology updates and version history
- **Version Control**: Semantic versioning for terminology releases
- **Active Tracking**: Single active version per terminology type
- **Audit Trail**: Complete history of terminology changes

### Database Views and Query Patterns

#### 6. Unified Query Views

The application creates logical views for cross-system queries:

**namaste_codes (Logical View)**
```sql
-- Unified view combining all AYUSH systems
(SELECT code, term as display, 'ayurveda' as system FROM ayurveda_terms)
UNION ALL
(SELECT code, term as display, 'siddha' as system FROM siddha_terms)  
UNION ALL
(SELECT code, term as display, 'unani' as system FROM unani_terms)
```
- **Purpose**: Enables unified search across all AYUSH systems
- **Performance**: Used by TerminologyService for cross-system operations
- **Standardization**: Consistent field names across different systems

**icd_mappings (Logical View)**
```sql
-- Unified mappings across all AYUSH systems
(SELECT ayurveda_code as namc_code, icd_code, icd_term as icd_title, 
        'ayurveda' as system FROM ayurveda_icd_mappings)
UNION ALL
(SELECT siddha_code as namc_code, icd_code, icd_term as icd_title,
        'siddha' as system FROM siddha_icd_mappings)
UNION ALL  
(SELECT unani_code as namc_code, icd_code, icd_term as icd_title,
        'unani' as system FROM unani_icd_mappings)
```
- **Purpose**: Unified mapping queries for translation operations
- **FHIR Operations**: Used by MappingService for $translate operations
- **Cross-System**: Enables mapping analytics across all AYUSH systems

### Technical Implementation Details

#### Database Configuration
```python
# SQLAlchemy async engine configuration
DATABASE_URL = "sqlite+aiosqlite:///./namaste_terminology.db"
engine = create_async_engine(DATABASE_URL, echo=False)

# Session management with dependency injection
async def get_db_session():
    async with AsyncSession(engine) as session:
        yield session
```

#### Data Types and Constraints
- **Primary Keys**: Auto-incrementing integers for all tables
- **Unique Constraints**: Code fields have unique constraints to prevent duplicates
- **Indexes**: Strategic indexing on code fields and foreign key references
- **JSON Storage**: FHIR Bundle data stored as JSON for flexibility
- **String Lengths**: VARCHAR without explicit length for SQLite compatibility

#### Foreign Key Relationships
While not explicitly defined as FK constraints in SQLite, logical relationships exist:
- Mapping tables reference terminology tables via code fields
- ICD mappings reference icd11_codes.code for target classifications
- Encounter records reference multiple AYUSH codes via string storage

This database design provides robust support for traditional medicine terminology management while maintaining performance for clinical translation operations.

## API Endpoints and Database Interactions

### 1. Health Check Endpoint
```
GET /health
```
**Purpose**: Service health verification  
**Database Interaction**: None  
**Response**: Simple status message

### 2. FHIR CodeSystem Lookup
```
POST /fhir/CodeSystem/$lookup
```
**Purpose**: FHIR R4 compliant concept lookup  
**Database Interactions**:
```sql
-- Single concept lookup by code
SELECT code, display, system, native_term 
FROM namaste_codes 
WHERE code = :code
LIMIT 1

-- Alternative system-specific lookup
SELECT code, term, sanskrit_term, description
FROM ayurveda_terms  
WHERE code = :code
```
**Business Logic**: 
- Validates FHIR Parameters input structure
- Performs exact code matching across AYUSH systems
- Returns FHIR-compliant OperationOutcome resource
- Includes native language terms and system attribution

### 3. FHIR ConceptMap Translation  
```
POST /fhir/ConceptMap/$translate
```
**Purpose**: FHIR R4 compliant AYUSH→ICD-11 translation  
**Database Interactions**:
```sql
-- Primary translation query with confidence filtering
SELECT
    nc.code, nc.display, nc.native_term, nc.system,
    im.icd_code, im.icd_title, im.similarity_score
FROM icd_mappings im
JOIN namaste_codes nc ON im.namc_code = nc.code  
WHERE nc.code = :code AND nc.system = :system
```
**Business Logic** (MappingService):
- Extracts system/code from FHIR Parameters
- Filters generic/low-quality mappings using `_is_generic_mapping()`
- Generates clinical notes with `_generate_clinical_notes()`
- Applies confidence-based equivalence classification:
  - similarity_score ≥ 0.8 → "equivalent"  
  - similarity_score ≥ 0.6 → "relatedto"
  - similarity_score < 0.6 → "wider"
- Returns FHIR ConceptMap with match array

### 4. Direct Concept Lookup
```
GET /lookup?query={term}&system={system}&limit={count}
```
**Purpose**: Direct AYUSH concept search with ICD mappings  
**Database Interactions**:
```sql
-- Multi-field fuzzy search with ICD mappings
SELECT 
    nc.code, nc.display, nc.system, nc.native_term,
    im.icd_code, im.icd_title, im.similarity_score
FROM namaste_codes nc
LEFT JOIN icd_mappings im ON nc.code = im.namc_code 
WHERE (LOWER(nc.code) LIKE :query 
    OR LOWER(nc.display) LIKE :query 
    OR LOWER(nc.native_term) LIKE :query)
[AND LOWER(nc.system) = :system]  -- Optional system filter
ORDER BY nc.display, im.similarity_score DESC 
LIMIT :limit
```
**Business Logic** (TerminologyService):
- Performs case-insensitive pattern matching on code, display, and native terms
- Groups results by concept and aggregates multiple ICD mappings
- Optional system filtering for targeted searches
- Returns concepts with nested ICD mapping arrays

### 5. System Concept Browsing
```
GET /api/systems/{system}/concepts?limit={count}&offset={skip}
```
**Purpose**: Paginated browsing of system-specific concepts  
**Database Interactions**:
```sql
-- Paginated system concept retrieval with mappings
SELECT 
    nc.code, nc.display, nc.system, nc.native_term,
    im.icd_code, im.icd_title, im.similarity_score
FROM (
    SELECT code, display, system, native_term
    FROM namaste_codes 
    WHERE LOWER(system) = :system 
    ORDER BY display
    LIMIT :limit OFFSET :offset
) nc
LEFT JOIN icd_mappings im ON nc.code = im.namc_code 
ORDER BY nc.display, im.similarity_score DESC

-- Count query for pagination metadata
SELECT COUNT(DISTINCT nc.code)
FROM namaste_codes nc
WHERE LOWER(nc.system) = :system
```
**Business Logic** (TerminologyService):
- Validates system parameter (ayurveda|siddha|unani)
- Implements efficient pagination with offset/limit
- Groups concepts and aggregates mappings
- Provides total count for pagination metadata

### 6. Mapping Retrieval
```
GET /api/mappings?system={system}&limit={count}&offset={skip}&min_confidence={score}&equivalence={type}
```
**Purpose**: Comprehensive mapping browsing with filtering  
**Database Interactions**:
```sql
-- Filtered mapping retrieval with dynamic WHERE clause
SELECT 
    nc.code, nc.display, nc.native_term, nc.system,
    im.icd_code, im.icd_title, im.similarity_score,
    CASE 
        WHEN im.similarity_score >= 0.8 THEN 'equivalent'
        WHEN im.similarity_score >= 0.5 THEN 'relatedto'
        ELSE 'unmatched'
    END as equivalence
FROM namaste_codes nc
JOIN icd_mappings im ON nc.code = im.namc_code
WHERE im.icd_code IS NOT NULL
    [AND nc.system = :system]               -- Optional system filter
    [AND im.similarity_score >= :min_confidence]  -- Optional confidence filter
    [AND equivalence_condition]            -- Optional equivalence filter
ORDER BY im.similarity_score DESC, nc.system, nc.code
LIMIT :limit OFFSET :offset

-- Count query for pagination
SELECT COUNT(*) FROM namaste_codes nc
JOIN icd_mappings im ON nc.code = im.namc_code  
WHERE [dynamic_where_conditions]
```
**Business Logic** (MappingService):
- Builds dynamic WHERE clauses based on filter parameters
- Filters generic mappings using `_is_generic_mapping()`
- Calculates equivalence types from similarity scores
- Returns paginated results with metadata

### 7. System Statistics
```
GET /statistics
```
**Purpose**: Comprehensive analytics across all AYUSH systems  
**Database Interactions**:
```sql
-- Total terminology concepts
SELECT COUNT(*) FROM namaste_codes

-- Total ICD mappings  
SELECT COUNT(*) FROM icd_mappings

-- Encounters processed (with table existence check)
SELECT COUNT(*) FROM sqlite_master 
WHERE type='table' AND name='encounter_records'
-- If exists:
SELECT COUNT(*) FROM encounter_records

-- System distribution
SELECT system, COUNT(*) FROM namaste_codes GROUP BY system

-- Equivalence distribution with confidence ranges
SELECT 
    CASE 
        WHEN similarity_score >= 0.8 THEN 'equivalent'
        WHEN similarity_score >= 0.5 THEN 'relatedto'  
        WHEN similarity_score >= 0.3 THEN 'wider'
        ELSE 'unmatched'
    END as equivalence_type,
    COUNT(*) as count
FROM icd_mappings
WHERE similarity_score IS NOT NULL
GROUP BY equivalence_type
```
**Business Logic** (StatisticsService):
- Aggregates data across all database tables
- Handles missing tables gracefully (encounter_records)
- Calculates equivalence distributions from similarity scores
- Provides comprehensive ecosystem metrics

### 8. Encounter Processing  
```
POST /api/encounters
```
**Purpose**: Batch processing of clinical encounters with AYUSH codes  
**Database Interactions**:
```sql
-- Background validation of AYUSH codes
SELECT code, display, system 
FROM namaste_codes 
WHERE code IN (:code_list)

-- Encounter record insertion
INSERT INTO encounter_records 
(encounter_id, patient_id, ayush_codes, icd_mappings, processing_status, created_at)
VALUES (:encounter_id, :patient_id, :ayush_codes_json, :icd_mappings_json, 'completed', NOW())

-- Mapping lookup for encounter codes
SELECT 
    nc.code, nc.display, nc.system,
    im.icd_code, im.icd_title, im.similarity_score
FROM namaste_codes nc
LEFT JOIN icd_mappings im ON nc.code = im.namc_code
WHERE nc.code IN (:encounter_codes)
```
**Business Logic**:
- Validates all AYUSH codes in encounter
- Performs bulk mapping lookups  
- Stores processing results as JSON
- Returns mapping success/failure status

### 9. Code Validation
```
GET /api/validate/{system}/{code}
```
**Purpose**: Single code validation against specific AYUSH system  
**Database Interactions**:
```sql
-- System-specific code validation
SELECT code, display, native_term, description
FROM namaste_codes
WHERE code = :code AND system = :system
LIMIT 1
```
**Business Logic**:
- Validates system parameter
- Performs exact code matching
- Returns concept details if valid
- Provides validation status

## Service Layer Architecture

### TerminologyService
**Responsibilities**:
- AYUSH concept search across multiple fields
- System-specific concept browsing with pagination  
- FHIR CodeSystem generation
- Cross-system concept aggregation

**Key Methods**:
- `search_concepts()`: Multi-field fuzzy search with mapping aggregation
- `get_system_concepts()`: Paginated system browsing  
- `get_system_concepts_count()`: Pagination metadata
- `get_concept_by_code()`: Direct concept lookup
- `get_fhir_codesystem()`: FHIR R4 CodeSystem resource generation

### MappingService  
**Responsibilities**:
- AYUSH→ICD-11 concept translation
- Mapping quality filtering and enhancement
- Clinical notes generation
- FHIR ConceptMap operations

**Key Methods**:
- `translate_concept()`: FHIR $translate operation implementation
- `_is_generic_mapping()`: Quality filtering for generic terms
- `_generate_clinical_notes()`: Clinical context generation
- `get_system_mappings()`: System-specific mapping retrieval
- `get_all_mappings()`: Comprehensive mapping browsing

### StatisticsService
**Responsibilities**:  
- Ecosystem analytics and metrics
- Data distribution analysis
- Performance monitoring
- Business intelligence

**Key Methods**:
- `get_comprehensive_statistics()`: Full ecosystem metrics
- `_get_total_terms()`: Terminology count aggregation
- `_get_total_mappings()`: Mapping count aggregation  
- `_get_system_distribution()`: System-wise concept distribution
- `_get_equivalence_distribution()`: Mapping quality distribution

## FHIR R4 Compliance

### CodeSystem Operations
The backend implements FHIR R4 CodeSystem/$lookup operation:
- **Input**: FHIR Parameters with system URI and code
- **Processing**: Direct lookup in namaste_codes unified view
- **Output**: FHIR OperationOutcome with concept details
- **Extensions**: Native language terms and system attribution

### ConceptMap Operations  
The backend implements FHIR R4 ConceptMap/$translate operation:
- **Input**: FHIR Parameters with source system, code, and target system
- **Processing**: Mapping lookup with quality filtering and enhancement
- **Output**: FHIR ConceptMap with match array and equivalence classification
- **Extensions**: Clinical notes and confidence scoring

### Resource Generation
- **CodeSystem**: Complete AYUSH terminology as unified FHIR resource
- **ConceptMap**: Dynamic generation for translation operations  
- **OperationOutcome**: Standardized error and success responses
- **Parameters**: FHIR-compliant input/output parameter handling

## Data Quality and Filtering

### Generic Mapping Filtering
The system implements sophisticated filtering to exclude low-quality mappings:

**Generic AYUSH Terms** (Excluded):
- 'disorder', 'disease', 'condition', 'unspecified', 'other', 'general'

**Generic ICD Patterns** (Excluded):
- 'unspecified', 'other specified', 'not otherwise specified'
- ', unspecified', ', other' (suffix patterns)

### Confidence Scoring
Mapping quality is classified using similarity scores:
- **≥ 0.8**: "equivalent" - High confidence, direct clinical correlation
- **≥ 0.6**: "relatedto" - Moderate confidence, good clinical alignment  
- **≥ 0.4**: "wider" - Fair confidence, partial clinical overlap
- **< 0.4**: "unmatched" - Low confidence, limited correlation

### Clinical Notes Generation
The system automatically generates meaningful clinical notes:
- Confidence level descriptions
- System-specific clinical insights
- Traditional medicine context
- Diagnostic considerations

## Database Configuration

### Development Setup (SQLite)
```python
# database.py configuration
DATABASE_URL = "sqlite+aiosqlite:///./namaste_terminology.db"
engine = create_async_engine(DATABASE_URL, echo=False)
```

### Production Setup (PostgreSQL)
```python
# Environment-based configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
engine = create_async_engine(DATABASE_URL, pool_size=20, max_overflow=30)
```

### Session Management
- **Async Context Managers**: Proper transaction handling
- **Dependency Injection**: FastAPI integration via `get_db_session()`
- **Error Handling**: Graceful degradation on database errors

## Technical Architecture

### Async Implementation
- **Non-blocking I/O**: Full async/await implementation
- **Concurrent Requests**: FastAPI async request handling
- **Database Connections**: Async SQLAlchemy with connection pooling

## Standards Compliance

### FHIR R4 Implementation
- **CodeSystem**: Complete AYUSH terminology representation
- **ConceptMap**: Translation and mapping operations
- **OperationOutcome**: Standardized response format  
- **Parameters**: FHIR-compliant operation parameters

### Healthcare Interoperability
- **ICD-11**: International classification integration
- **Traditional Medicine**: Native language preservation
- **Clinical Context**: Meaningful mapping notes
- **Quality Assurance**: Confidence-based filtering

### API Standards
- **REST Architecture**: Resource-based URL design
- **OpenAPI 3.0**: Automatic documentation generation
- **HTTP Status Codes**: Proper error indication
- **JSON Format**: Structured response format

## Error Handling and Logging

### Database Error Handling
```python
try:
    result = await session.execute(query, params)
    # Process results
except Exception as e:
    logger.error(f"Database error: {e}", exc_info=True)
    return default_response
```

### API Error Responses
- **400 Bad Request**: Invalid parameters or malformed requests
- **404 Not Found**: Concepts or mappings not found
- **500 Internal Server Error**: Database or system errors
- **200 OK**: Successful operations with data
- **FHIR OperationOutcome**: Standardized error format for FHIR operations

### Logging Strategy
- **Structured Logging**: Consistent log format across services
- **Error Context**: Full exception traces for debugging
- **Performance Metrics**: Query timing and success rates
- **Business Metrics**: Search patterns and mapping usage

## Security Implementation
- **Input Validation**: Pydantic schema validation
- **SQL Injection Protection**: SQLAlchemy parameterized queries
- **Authentication Ready**: JWT token infrastructure prepared
- **CORS Configuration**: Secure cross-origin handling

## Future Development Areas

### Enhanced Mapping Quality
- **Machine Learning**: Automated similarity scoring improvement
- **Expert Validation**: Clinical expert review workflows
- **Feedback Integration**: User feedback incorporation
- **Version Management**: Mapping version control

### Extended FHIR Operations
- **Additional Operations**: $validate-code, $subsumes implementation
- **Bundle Resources**: Batch operation support
- **Terminology Services**: Complete FHIR terminology server
- **Subscription Support**: Real-time update notifications

### Analytics Enhancement
- **Usage Analytics**: API endpoint usage tracking
- **Quality Metrics**: Mapping accuracy measurement
- **Performance Monitoring**: Response time optimization
- **Business Intelligence**: Clinical usage insights

This comprehensive documentation provides complete understanding of how the AYUSH Terminology Backend operates, from database schema design through API endpoint implementation to FHIR standard compliance. The system is designed for production healthcare environments requiring robust traditional medicine to modern healthcare standard translation capabilities.
- **Production Ready**: SQLAlchemy ORM, comprehensive error handling, logging

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Development Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start development server:**
   ```bash
   python start_dev_server.py
   ```
   
   Or manually:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access the service:**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## 📊 Database Content

### NAMASTE Terminology
- **Ayurveda**: 30+ authentic codes from Charaka Samhita & Sushruta Samhita
- **Siddha**: 20+ traditional diagnostic categories
- **Unani**: 20+ classical Unani diagnostic terms

### ICD-11 Mappings
- Standard ICD-11 MMS codes
- Traditional Medicine Module 2 (TM2) codes
- Expert-curated mappings with equivalence relationships

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/health` | GET | Health check |
| `/lookup` | GET | Search NAMASTE terminology |
| `/ConceptMap/$translate` | POST | Translate NAMASTE to ICD-11 |
| `/Encounter` | POST | Ingest dual-coded encounters |
| `/statistics` | GET | System statistics |
| `/mappings/{code}` | GET | Detailed concept mapping |

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   FastAPI       │───▶│   SQLAlchemy    │
│   React App     │    │   Backend       │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Components
- **FastAPI**: Modern, high-performance web framework
- **SQLAlchemy**: Production-ready ORM with connection pooling
- **Pydantic**: Data validation and serialization
- **SQLite**: Development database (configurable for PostgreSQL)

## 🔒 Security

- CORS enabled for development
- Input validation with Pydantic schemas
- SQL injection protection via SQLAlchemy ORM
- Error handling without sensitive data exposure

## 📁 Project Structure

```
backend/
├── main.py              # FastAPI application
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic request/response models
├── database.py          # Database connection setup
├── data_loader.py       # Terminology data initialization
├── requirements.txt     # Python dependencies
├── start_dev_server.py  # Development server script
└── README.md           # This file
```

## 🧪 Testing

The backend includes comprehensive test data and error handling:

- Real NAMASTE terminology codes
- Authentic ICD-11 mappings
- Expert-validated clinical correlations
- Fallback mechanisms for offline development

## 🔧 Configuration

Environment variables:
- `DATABASE_URL`: Database connection string (defaults to SQLite)

## 📈 Statistics

The `/statistics` endpoint provides:
- Total terminology counts by system
- Mapping equivalence distribution
- Clinical encounter statistics
- System health metrics

## 🤝 Contributing

This backend implements the NAMASTE-ICD11 integration specification:
- WHO ICD-11 Traditional Medicine Module 2 compliance
- Ministry of AYUSH NAMASTE portal alignment
- FHIR R4 terminology services standards

## 📞 Support

For technical issues or questions about the terminology mappings, refer to:
- API Documentation: `/docs` endpoint
- FHIR Terminology Services: https://www.hl7.org/fhir/terminology-service.html
- WHO ICD-11: https://icd.who.int/en