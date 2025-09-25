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
    
    def _generate_clinical_notes(self, namaste_term: str, namaste_system: str, icd_title: str, similarity_score: float) -> str:
        """Generate meaningful clinical notes based on mapping data."""
        
        # Define confidence levels and their descriptions
        if similarity_score >= 0.8:
            confidence_desc = "High confidence mapping"
            relationship = "Strong clinical correlation"
        elif similarity_score >= 0.6:
            confidence_desc = "Moderate confidence mapping"
            relationship = "Good clinical alignment"
        elif similarity_score >= 0.4:
            confidence_desc = "Fair confidence mapping"
            relationship = "Partial clinical overlap"
        else:
            confidence_desc = "Low confidence mapping"
            relationship = "Limited clinical correlation"
        
        # Generate system-specific insights
        system_insight = ""
        if namaste_system.lower() == "ayurveda":
            system_insight = "Consider traditional Ayurvedic diagnostic principles and constitutional factors."
        elif namaste_system.lower() == "siddha":
            system_insight = "Evaluate based on Siddha medicine's tridosha and bodily constituent assessment."
        elif namaste_system.lower() == "unani":
            system_insight = "Apply Unani medicine's temperament (mizaj) and humoral balance principles."
        
        # Create meaningful clinical note
        return f"{confidence_desc} (score: {similarity_score:.2f}). {relationship} between '{namaste_term}' and '{icd_title}'. {system_insight}"
    
    def _is_generic_mapping(self, namaste_term: str, icd_title: str) -> bool:
        """Check if a mapping contains generic/vague terms that should be filtered out."""
        
        # Generic NAMASTE terms to exclude
        generic_namaste_terms = {
            'disorder', 'disease', 'condition', '-', 'unspecified', 
            'other', 'general', 'various', 'multiple'
        }
        
        # Generic ICD terms to exclude
        generic_icd_patterns = [
            'unspecified', 'other specified', 'not otherwise specified',
            'not elsewhere classified', ', unspecified', ', other'
        ]
        
        # Check NAMASTE term for generic words
        namaste_lower = namaste_term.lower().strip()
        if namaste_lower in generic_namaste_terms:
            return True
        
        # Check if NAMASTE term is just a single generic word
        if len(namaste_lower.split()) == 1 and namaste_lower in ['disorder', 'disease', '-']:
            return True
            
        # Check ICD title for generic patterns
        icd_lower = icd_title.lower()
        for pattern in generic_icd_patterns:
            if pattern in icd_lower:
                return True
        
        # Filter out mappings where ICD title ends with generic qualifiers
        if icd_lower.endswith(', unspecified') or icd_lower.endswith(', other'):
            return True
            
        return False

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

        # Query the icd_mappings table joined with namaste_codes 
        sql_query = """
            SELECT
                nc.code, nc.display, nc.native_term, nc.system,
                im.icd_code, im.icd_title, 'relatedto' as equivalence, im.similarity_score,
                'direct' as mapping_type
            FROM icd_mappings im
            JOIN namaste_codes nc ON im.namc_code = nc.code
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
                    # Filter out generic mappings
                    if self._is_generic_mapping(row[1], row[5]):  # row[1] = nc.display, row[5] = im.icd_title
                        logger.info(f"Skipping generic mapping: {row[1]} -> {row[5]}")
                        continue
                    
                    # Generate meaningful clinical notes
                    clinical_notes = self._generate_clinical_notes(
                        namaste_term=row[1],      # nc.display
                        namaste_system=row[3],    # nc.system
                        icd_title=row[5],         # im.icd_title
                        similarity_score=row[7] or 0.8  # im.similarity_score
                    )
                    
                    match = ConceptMatch(
                        namasteCode=row[0],         # nc.code
                        namasteTerm=row[1],         # nc.display
                        originalTerm=row[2],        # nc.native_term
                        system=row[3].capitalize(), # nc.system
                        icd11Code=row[4],           # im.icd_code
                        icd11Term=row[5],           # im.icd_title
                        equivalence=row[6] or 'relatedto',  # equivalence
                        confidence=row[7] or 0.8,   # im.similarity_score
                        mappingType=row[8] or 'direct',     # mapping_type
                        clinicalNotes=clinical_notes        # Generated clinical notes
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

            # Use the correct icd_mappings and namaste_codes tables
            sql_query = """
                SELECT 
                    nc.code,
                    nc.display,
                    im.icd_code,
                    im.icd_title,
                    im.similarity_score,
                    'relatedto' as equivalence,
                    'direct' as mapping_type
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
                    "target_code": row[2],
                    "target_term": row[3],
                    "confidence": row[4],
                    "equivalence": row[5],
                    "mapping_type": row[6],
                    "system": system.title()
                }
                for row in rows
            ]
            logger.info(f"Found {len(mappings)} mappings for system: '{system}'")
            return mappings
        except Exception as e:
            logger.error(f"Database error getting system mappings for '{system}': {e}")
            return []

    async def get_all_mappings(
        self,
        session,
        limit: int = 100,
        offset: int = 0,
        system: Optional[str] = None,
        min_confidence: float = 0.0,
        equivalence: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all ICD-11 mappings with optional filtering and pagination.
        """
        try:
            # Build base query
            where_conditions = ["im.icd_code IS NOT NULL"]
            params = {'limit': limit, 'offset': offset, 'min_confidence': min_confidence}
            
            # Add system filter
            if system and system.lower() in ['ayurveda', 'siddha', 'unani']:
                where_conditions.append("nc.system = :system")
                params['system'] = system.lower()
            
            # Add confidence filter
            where_conditions.append("im.similarity_score >= :min_confidence")
            
            # Add equivalence filter (for future use when we have equivalence data)
            if equivalence:
                # For now, we'll use similarity score ranges to simulate equivalence
                if equivalence == 'equivalent':
                    where_conditions.append("im.similarity_score >= 0.8")
                elif equivalence == 'relatedto':
                    where_conditions.append("im.similarity_score >= 0.5 AND im.similarity_score < 0.8")
                elif equivalence == 'unmatched':
                    where_conditions.append("im.similarity_score < 0.5")
            
            where_clause = " AND ".join(where_conditions)
            
            # Get total count
            count_query = f"""
                SELECT COUNT(*)
                FROM namaste_codes nc
                JOIN icd_mappings im ON nc.code = im.namc_code
                WHERE {where_clause}
            """
            
            count_result = await session.execute(text(count_query), params)
            total_count = count_result.scalar()
            
            # Get mappings
            sql_query = f"""
                SELECT 
                    nc.code,
                    nc.display,
                    nc.native_term,
                    nc.system,
                    im.icd_code,
                    im.icd_title,
                    im.similarity_score,
                    CASE 
                        WHEN im.similarity_score >= 0.8 THEN 'equivalent'
                        WHEN im.similarity_score >= 0.5 THEN 'relatedto'
                        ELSE 'unmatched'
                    END as equivalence,
                    'direct' as mapping_type
                FROM namaste_codes nc
                JOIN icd_mappings im ON nc.code = im.namc_code
                WHERE {where_clause}
                ORDER BY im.similarity_score DESC, nc.system, nc.code
                LIMIT :limit OFFSET :offset
            """
            
            result = await session.execute(text(sql_query), params)
            rows = result.fetchall()
            
            # Filter out generic mappings and create response
            mappings = []
            for row in rows:
                # Check if this is a generic mapping that should be filtered
                if not self._is_generic_mapping(row[1], row[5]):  # row[1] = nc.display, row[5] = im.icd_title
                    mappings.append({
                        "source_code": row[0],
                        "source_term": row[1],
                        "original_term": row[2] or row[1],
                        "target_code": row[4],
                        "target_term": row[5],
                        "confidence": row[6],
                        "equivalence": row[7],
                        "mapping_type": row[8],
                        "system": row[3].title()
                    })
            
            logger.info(f"Found {len(mappings)} mappings (total: {total_count})")
            return {
                "mappings": mappings,
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + len(mappings) < total_count
            }
        except Exception as e:
            logger.error(f"Database error getting all mappings: {e}")
            return {
                "mappings": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "has_more": False
            }