"""
Mapping Service - Handles AYUSH to ICD-11 concept mappings and FHIR translation.
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
                message="Required parameters 'system' and 'code' must be provided"
            )
        
        system = self._get_system_from_uri(system_uri)
        logger.info(f"Mapped system_uri '{system_uri}' to system: {system}")
        
        if not system:
            return TranslateResponse(result=False, message=f"Unsupported source system: {system_uri}")

        # Query the concept_mappings table joined with namaste_codes 
        sql_query = """
            SELECT
                nc.code, nc.display, nc.original_term, nc.system,
                cm.icd11_code, cm.icd11_term, cm.equivalence, cm.confidence,
                cm.mapping_type, cm.clinical_notes
            FROM concept_mappings cm
            JOIN namaste_codes nc ON cm.namaste_code = nc.code
            WHERE nc.code = :code AND nc.system = :system
        """
        params = {'code': code, 'system': system}

        try:
            logger.info(f"Executing query: {sql_query}")
            logger.info(f"With parameters: {params}")
            
            result = await db.execute(text(sql_query), params)
            rows = result.fetchall()
            
            logger.info(f"Query executed successfully, found {len(rows)} rows")

            if not rows:
                logger.info(f"No mapping found for code: {code} in system: {system}")
                return TranslateResponse(result=False, message=f"No mapping found for code: {code}")

            matches = []
            for i, row in enumerate(rows):
                logger.info(f"Processing row {i+1}: {row}")
                try:
                    match = ConceptMatch(
                        namasteCode=row[0],         # nc.code
                        namasteTerm=row[1],         # nc.display
                        originalTerm=row[2],        # nc.original_term
                        system=row[3].capitalize(), # nc.system
                        icd11Code=row[4],           # cm.icd11_code
                        icd11Term=row[5],           # cm.icd11_term
                        equivalence=row[6] or 'relatedto',  # cm.equivalence
                        confidence=row[7] or 0.8,   # cm.confidence
                        mappingType=row[8] or 'direct',     # cm.mapping_type
                        clinicalNotes=row[9] or 'N/A'       # cm.clinical_notes
                    )
                    matches.append(match)
                    logger.info(f"Successfully created match object: {match.namasteCode} -> {match.icd11Code}")
                except Exception as e:
                    logger.error(f"Error creating ConceptMatch from row {i+1}: {e}")
                    logger.error(f"Row data: {row}")

            logger.info(f"Created {len(matches)} matches successfully")
            return TranslateResponse(result=True, match=matches)

        except Exception as e:
            logger.error(f"Database translation error for code '{code}' in system '{system}': {e}", exc_info=True)
            return TranslateResponse(result=False, message=f"An internal error occurred during translation: {str(e)}")

    def _get_system_from_uri(self, uri: str) -> Optional[str]:
        """Helper to extract system name from a URI."""
        if not isinstance(uri, str):
            return None
        uri_lower = uri.lower()
        if 'ayurveda' in uri_lower:
            return 'ayurveda'
        if 'siddha' in uri_lower:
            return 'siddha'
        if 'unani' in uri_lower:
            return 'unani'
        return None

    async def get_system_mappings(
        self,
        session,
        system: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get ICD-11 mappings for a specific AYUSH system with pagination.
        """
        try:
            system = system.lower()
            if system not in ['ayurveda', 'siddha', 'unani']:
                return []

            # Use the icd_mappings table that contains the real data
            sql_query = """
                SELECT 
                    nc.code,
                    nc.display,
                    nc.native_term,
                    im.icd_code,
                    im.icd_title,
                    im.similarity_score,
                    im.system
                FROM namaste_codes nc
                JOIN icd_mappings im ON nc.code = im.namc_code
                WHERE nc.system = :system 
                    AND im.icd_code IS NOT NULL 
                ORDER BY im.similarity_score DESC 
                LIMIT :limit OFFSET :offset
            """

            params = {'system': system, 'limit': limit, 'offset': offset}
            result = await session.execute(text(sql_query), params)
            rows = result.fetchall()

            mappings = [
                {
                    "source_code": row[0],
                    "source_term": row[1],
                    "native_term": row[2],
                    "target_code": row[3],
                    "target_term": row[4],
                    "confidence": row[5],
                    "equivalence": "relatedto" if row[5] > 0.8 else "narrower" if row[5] > 0.6 else "wider",
                    "mapping_type": "contextual",
                    "system": system.title()
                }
                for row in rows
            ]
            logger.info(f"Found {len(mappings)} mappings for system: '{system}'")
            return mappings
        except Exception as e:
            logger.error(f"Database error getting system mappings for '{system}': {e}")
            return []