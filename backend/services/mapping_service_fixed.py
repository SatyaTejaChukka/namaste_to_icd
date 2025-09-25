"""
Fixed Mapping Service - Handles AYUSH to ICD-11 concept mappings and FHIR translation.
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db_session
from schemas import TranslateRequest, TranslateResponse, ConceptMatch

logger = logging.getLogger(__name__)

class MappingService:
    """Service for managing concept mappings between AYUSH systems and ICD-11."""

    def __init__(self):
        self.initialized = True
        logger.info("Mapping service initialized")

    async def translate_concept(
        self,
        db: AsyncSession,
        request: TranslateRequest
    ) -> TranslateResponse:
        """
        FHIR $translate operation implementation.
        Translates an AYUSH code to its ICD-11 equivalent.
        """
        # Extract parameters from FHIR Parameters resource
        system_uri = None
        code = None
        target_uri = None
        
        logger.info(f"Processing translate request: {request}")
        
        for param in request.parameter:
            logger.info(f"Processing parameter: {param.name} = {param}")
            if param.name == "system":
                system_uri = param.valueUri
            elif param.name == "code":
                code = param.valueCode
            elif param.name == "target":
                target_uri = param.valueUri
        
        logger.info(f"Extracted - system_uri: {system_uri}, code: {code}, target_uri: {target_uri}")
        
        if not system_uri or not code:
            return TranslateResponse(
                result=False, 
                message="Missing required parameters: system and code"
            )

        # Map system URI to table name
        system = self._get_system_from_uri(system_uri)
        if not system:
            return TranslateResponse(
                result=False, 
                message=f"Unsupported system URI: {system_uri}"
            )

        try:
            # Map system to table name
            table_map = {
                'ayurveda': 'ayurveda_terms',
                'siddha': 'siddha_terms', 
                'unani': 'unani_terms'
            }
            
            if system not in table_map:
                return TranslateResponse(result=False, message=f"Unsupported system: {system}")
            
            # Check if the source code exists
            table_name = table_map[system]
            check_query = f"SELECT code, term, system FROM {table_name} WHERE code = :code"
            result = await db.execute(text(check_query), {'code': code})
            source_row = result.fetchone()
            
            if not source_row:
                return TranslateResponse(result=False, message=f"Code {code} not found in {system} system")
            
            # For demonstration, create a mock ICD-11 mapping
            # In production, this would come from actual mapping tables
            mock_icd_mappings = [
                {
                    'icd_code': 'XM7P95',
                    'icd_title': 'Traditional medicine conditions - general',
                    'equivalence': 'relatedto',
                    'confidence': 0.8
                }
            ]
            
            matches = []
            for mapping in mock_icd_mappings:
                match = ConceptMatch(
                    namasteCode=source_row[0],
                    namasteTerm=source_row[1], 
                    originalTerm=source_row[1],
                    system=source_row[2],
                    icd11Code=mapping['icd_code'],
                    icd11Term=mapping['icd_title'],
                    equivalence=mapping['equivalence'],
                    confidence=mapping['confidence'],
                    mappingType='automatic',
                    clinicalNotes='Mock mapping for demonstration'
                )
                matches.append(match)
            
            return TranslateResponse(result=True, match=matches)

        except Exception as e:
            logger.error(f"Translation error for code '{code}': {e}")
            return TranslateResponse(result=False, message=f"Translation error: {str(e)}")

    def _get_system_from_uri(self, uri: str) -> Optional[str]:
        """Helper to extract system name from a URI."""
        if not isinstance(uri, str):
            return None
        uri_lower = uri.lower()
        if 'ayurveda' in uri_lower:
            return 'ayurveda'
        elif 'siddha' in uri_lower:
            return 'siddha'
        elif 'unani' in uri_lower:
            return 'unani'
        return None

    async def get_system_mappings(
        self,
        session: AsyncSession,
        system: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all ICD-11 mappings for a specific AYUSH system.
        Returns mock mappings for demonstration.
        """
        try:
            if system.lower() not in ['ayurveda', 'siddha', 'unani']:
                return []

            # For now, return mock mappings
            # In production, this would query actual mapping tables
            mappings = [
                {
                    "source_code": f"{system.upper()}-001",
                    "source_term": f"Sample {system.title()} Term",
                    "target_code": "XM7P95",
                    "target_term": "Traditional medicine conditions - general",
                    "similarity_score": 0.85,
                    "system": system.title()
                }
            ]

            return mappings

        except Exception as e:
            logger.error(f"Error getting system mappings for '{system}': {e}")
            return []

    async def validate_mapping(
        self,
        session: AsyncSession,
        source_code: str,
        target_code: str
    ) -> bool:
        """
        Validate if a mapping between source and target codes is valid.
        Returns True for demonstration purposes.
        """
        try:
            # In production, this would validate against actual mapping rules
            return True
        except Exception as e:
            logger.error(f"Error validating mapping {source_code} -> {target_code}: {e}")
            return False