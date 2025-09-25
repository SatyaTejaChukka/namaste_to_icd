"""
AYUSH Terminology Service - FHIR-compliant Microservice

This microservice provides FHIR-compliant terminology services for Ayurveda, Siddha, and Unani (AYUSH) systems.
It implements standard FHIR operations including lookup, translate, and validation for traditional medicine terminologies.

Features:
- FHIR R4 compliant endpoints
- Support for Ayurveda, Siddha, and Unani terminologies
- ICD-11 mapping capabilities
- Real-time clinical decision support
- Secure API access with authentication
- Comprehensive audit logging
"""

from fastapi import FastAPI, HTTPException, Depends, status, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, text, or_, and_
from typing import List, Optional, Dict, Any, Union
import logging
from datetime import datetime
import asyncio

# Database and models
from database import get_db_session

# Services
from services.terminology_service import TerminologyService
from services.mapping_service import MappingService
from services.statistics_service import StatisticsService

# Schemas
from schemas import (
    LookupResponse,
    TranslateRequest,
    TranslateResponse,
    EncounterRequest,
    StatisticsResponse,
    HealthResponse,
    AYUSHConceptResponse,
    ConceptMatch,
    FHIRResource,
    NAMASTECodeValidator,
    ICD11CodeValidator
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Create FastAPI app
app = FastAPI(
    title="AYUSH Terminology Service",
    description="FHIR-compliant microservice for Ayurveda, Siddha, and Unani terminology integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
terminology_service = TerminologyService()
mapping_service = MappingService()
statistics_service = StatisticsService()

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validate JWT token and return current user
    For now, this is a placeholder - implement actual JWT validation
    """
    # TODO: Implement proper JWT validation
    return {"user_id": "demo_user", "permissions": ["read", "write"]}

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check(db: AsyncSession = Depends(get_db_session)):
    """
    Health check endpoint for monitoring service status
    """
    try:
        # Test database connection
        result = await db.execute(text("SELECT 1"))
        db_status = "healthy" if result else "unhealthy"
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version="2.0.0",
            database_status=db_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable"
        )

@app.get("/fhir/CodeSystem/$lookup", response_model=LookupResponse, tags=["FHIR Terminology"])
async def lookup_concept(
    system: str = Query(..., description="AYUSH system: ayurveda, siddha, or unani"),
    code: str = Query(..., description="AYUSH concept code"),
    property: Optional[List[str]] = Query(None, description="Properties to include"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    FHIR $lookup operation for AYUSH concepts
    
    Retrieves detailed information about a specific AYUSH concept including:
    - Display name
    - System classification
    - Related properties
    - ICD-11 mappings if available
    """
    try:
        # Validate system
        if system not in ['ayurveda', 'siddha', 'unani']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid system: {system}. Must be one of: ayurveda, siddha, unani"
            )
        
        # Get concept from namaste_codes table with native terms and ICD mappings
        result = await db.execute(
            text("""
                SELECT 
                    nc.code, 
                    nc.display, 
                    nc.native_term,
                    im.icd_code,
                    im.icd_title,
                    im.similarity_score
                FROM namaste_codes nc
                LEFT JOIN icd_mappings im ON nc.code = im.namc_code
                WHERE nc.system = :system AND nc.code = :code
            """),
            {"system": system, "code": code}
        )
        
        rows = result.fetchall()
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Concept not found: {code} in system {system}"
            )
        
        # Process the first row to get basic concept info
        first_row = rows[0]
        
        # Collect all ICD mappings for this concept
        icd_mappings = []
        for row in rows:
            if row[3]:  # if icd_code exists
                icd_mappings.append({
                    "icd_code": row[3],
                    "icd_title": row[4],
                    "similarity_score": row[5]
                })
        
        concept = AYUSHConceptResponse(
            code=first_row[0],
            term=first_row[1],
            system=system,
            native_term=first_row[2],
            icd_mappings=icd_mappings
        )
        
        return LookupResponse(
            concepts=[concept],
            totalCount=1
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lookup failed for {system}/{code}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during lookup"
        )

@app.post("/fhir/ConceptMap/$translate", response_model=TranslateResponse, tags=["FHIR Terminology"])
async def translate_concept(
    request: TranslateRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    FHIR $translate operation for concept mapping
    
    Translates AYUSH concepts to ICD-11 codes using trained mapping algorithms
    """
    try:
        return await mapping_service.translate_concept(db, request)
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Translation service error"
        )

@app.get("/lookup", response_model=LookupResponse, tags=["Search"])
async def search_concepts(
    q: str = Query(..., description="Search query"),
    system: Optional[str] = Query(None, description="Filter by AYUSH system"),
    limit: int = Query(50, description="Maximum results", le=100),
    offset: int = Query(0, description="Result offset"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Search AYUSH concepts by text query
    
    Supports fuzzy matching and filters by system
    """
    try:
        concepts_list = await terminology_service.search_concepts(db, q, system, limit)
        concepts = [AYUSHConceptResponse(**concept) for concept in concepts_list]
        return LookupResponse(concepts=concepts, totalCount=len(concepts))
    except Exception as e:
        logger.error(f"Search failed for query '{q}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search service error"
        )

@app.get("/api/systems/{system}/concepts", response_model=LookupResponse, tags=["Browse"])
async def list_system_concepts(
    system: str,
    limit: int = Query(50, description="Maximum results", le=100),
    offset: int = Query(0, description="Result offset"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List all concepts in a specific AYUSH system
    """
    try:
        if system not in ['ayurveda', 'siddha', 'unani']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid system: {system}"
            )
        
        concepts_list = await terminology_service.get_system_concepts(db, system, limit, offset)
        total_count = await terminology_service.get_system_concepts_count(db, system)
        concepts = [AYUSHConceptResponse(**concept) for concept in concepts_list]
        return LookupResponse(concepts=concepts, totalCount=total_count)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list concepts for system {system}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system concepts"
        )

@app.get("/api/mappings/{system}", tags=["Mappings"])
async def get_system_mappings(
    system: str,
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get ICD-11 mappings for a specific AYUSH system
    """
    try:
        if system not in ['ayurveda', 'siddha', 'unani']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid system: {system}"
            )
        
        return await mapping_service.get_system_mappings(db, system, limit, offset)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get mappings for system {system}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve mappings"
        )

@app.get("/api/mappings", tags=["Mappings"])
async def get_all_mappings(
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    system: Optional[str] = Query(None),
    min_confidence: float = Query(0.0),
    equivalence: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get all ICD-11 mappings with optional filtering
    """
    try:
        return await mapping_service.get_all_mappings(db, limit, offset, system, min_confidence, equivalence)
    except Exception as e:
        logger.error(f"Failed to get all mappings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve mappings"
        )

@app.get("/statistics", response_model=StatisticsResponse, tags=["Analytics"])
async def get_statistics(db: AsyncSession = Depends(get_db_session)):
    """
    Get system-wide statistics and analytics
    """
    try:
        return await statistics_service.get_comprehensive_statistics(db)
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )

@app.post("/api/encounters", tags=["Clinical"])
async def ingest_encounter(
    encounter: EncounterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Ingest FHIR encounter with AYUSH coding
    
    Processes clinical encounters and extracts AYUSH terminology for analysis
    """
    try:
        # Process encounter in background
        background_tasks.add_task(
            process_encounter_background,
            encounter,
            current_user["user_id"]
        )
        
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"message": "Encounter queued for processing", "status": "accepted"}
        )
    except Exception as e:
        logger.error(f"Failed to queue encounter: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process encounter"
        )

@app.get("/api/validate/{system}/{code}", tags=["Validation"])
async def validate_concept(
    system: str,
    code: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Validate if a concept exists in the specified system
    """
    try:
        if system not in ['ayurveda', 'siddha', 'unani']:
            return {"valid": False, "reason": f"Invalid system: {system}"}
        
        # Check if concept exists in namaste_codes table
        result = await db.execute(
            text("SELECT 1 FROM namaste_codes WHERE system = :system AND code = :code LIMIT 1"),
            {"system": system, "code": code}
        )
        
        exists = result.fetchone() is not None
        
        return {
            "valid": exists,
            "code": code,
            "system": system,
            "reason": "Found" if exists else "Code not found in system"
        }
        
    except Exception as e:
        logger.error(f"Validation failed for {system}/{code}: {e}")
        return {"valid": False, "reason": "Validation service error"}

async def process_encounter_background(encounter: EncounterRequest, user_id: str):
    """
    Background task to process clinical encounters
    """
    try:
        # TODO: Implement encounter processing logic
        # This would extract AYUSH codes from the encounter
        # and store them for analytics
        logger.info(f"Processing encounter for user {user_id}")
        
        # Simulate processing
        await asyncio.sleep(1)
        
        logger.info("Encounter processed successfully")
    except Exception as e:
        logger.error(f"Background encounter processing failed: {e}")

@app.on_event("startup")
async def startup_event():
    """
    Application startup event
    """
    logger.info("AYUSH Terminology Service starting up...")
    logger.info("Service ready to handle requests")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event
    """
    logger.info("AYUSH Terminology Service shutting down...")

if __name__ == "__main__":
    import uvicorn
    from config import config
    
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=False,
        log_level="info"
    )