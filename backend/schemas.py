"""
Pydantic schemas for request/response validation
FHIR-compliant data models and validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class ICDMapping(BaseModel):
    """ICD-11 mapping information"""
    icd_code: str = Field(..., description="ICD-11 code")
    icd_title: str = Field(..., description="ICD-11 title/description")
    similarity_score: float = Field(..., description="Mapping similarity score (0-1)")

class AYUSHConceptResponse(BaseModel):
    """Response model for AYUSH terminology concepts"""
    code: str = Field(..., description="AYUSH code identifier")
    term: str = Field(..., description="Display term for the concept")
    system: str = Field(..., description="AYUSH system: Ayurveda, Siddha, or Unani")
    native_term: Optional[str] = Field(None, description="Native language term")
    icd_mappings: List[ICDMapping] = Field(default=[], description="ICD-11 mappings")

class LookupResponse(BaseModel):
    """Response model for terminology lookup operations"""
    concepts: List[AYUSHConceptResponse]
    totalCount: int = Field(..., description="Total number of matching concepts")

class FHIRParameter(BaseModel):
    """FHIR Parameters resource parameter"""
    name: str
    valueUri: Optional[str] = None
    valueCode: Optional[str] = None
    valueString: Optional[str] = None

from typing import Literal

class TranslateRequest(BaseModel):
    """FHIR Parameters resource for $translate operation"""
    resourceType: Literal["Parameters"] = "Parameters"
    parameter: List[FHIRParameter]

class ConceptMatch(BaseModel):
    """Individual concept mapping match"""
    namasteCode: str
    namasteTerm: str
    originalTerm: str
    system: str
    icd11Code: Optional[str]
    icd11Term: Optional[str]
    equivalence: str
    confidence: float
    mappingType: str
    clinicalNotes: str

class TranslateResponse(BaseModel):
    """Response model for concept translation"""
    result: bool
    message: Optional[str] = None
    match: Optional[List[ConceptMatch]] = None

class FHIRResource(BaseModel):
    """Generic FHIR resource"""
    resourceType: str
    id: Optional[str] = None
    # Allow additional fields
    
    class Config:
        extra = "allow"

class FHIRBundleEntry(BaseModel):
    """FHIR Bundle entry"""
    resource: Dict[str, Any]
    request: Optional[Dict[str, Any]] = None

class EncounterRequest(BaseModel):
    """FHIR Bundle for encounter ingestion"""
    resourceType: Literal["Bundle"] = "Bundle"
    type: Literal["transaction"] = "transaction"
    entry: List[FHIRBundleEntry]

class StatisticsResponse(BaseModel):
    """System statistics response"""
    total_terms: int
    total_mappings: int
    total_encounters: int
    system_distribution: Dict[str, int]
    equivalence_distribution: Dict[str, int]

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    database_status: str

# Validation helpers
class NAMASTECodeValidator:
    """Validator for NAMASTE codes"""
    
    @staticmethod
    def validate_code_format(code: str) -> bool:
        """Validate NAMASTE code format (e.g., AAE-16, SSE-12, UUE-11)"""
        if not code or len(code) < 5:
            return False
        
        # Basic pattern: three letters, hyphen, numbers
        parts = code.split('-')
        if len(parts) != 2:
            return False
        
        prefix, suffix = parts
        if len(prefix) != 3 or not prefix.isalpha():
            return False
        
        if not suffix.isdigit():
            return False
        
        # Check system prefixes
        valid_prefixes = ['AAE', 'AYU', 'SSE', 'SID', 'UUE', 'UNA']
        if prefix.upper() not in valid_prefixes:
            return False
        
        return True
    
    @staticmethod
    def validate_system(system: str) -> bool:
        """Validate AYUSH system"""
        return system in ['ayurveda', 'siddha', 'unani']

class ICD11CodeValidator:
    """Validator for ICD-11 codes"""
    
    @staticmethod
    def validate_code_format(code: str) -> bool:
        """Validate ICD-11 code format"""
        if not code or len(code) < 2:
            return False
        
        # ICD-11 codes can be alphanumeric with various patterns
        # Basic validation - starts with letter or number
        return code[0].isalnum()
    
    @staticmethod
    def validate_linearization(linearization: str) -> bool:
        """Validate ICD-11 linearization"""
        valid_linearizations = ['mms', 'phc', 'tm2']
        return linearization.lower() in valid_linearizations

