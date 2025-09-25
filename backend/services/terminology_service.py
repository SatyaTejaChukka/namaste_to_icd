"""
Terminology Service - Handles AYUSH concept search and FHIR CodeSystem operations.
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.sql import text
from database import get_db_session
from schemas import AYUSHConceptResponse

logger = logging.getLogger(__name__)

class TerminologyService:
    """Service for managing AYUSH terminology concepts and search operations."""

    def __init__(self):
        self.initialized = True
        logger.info("Terminology service initialized")

    async def search_concepts(
        self,
        session,
        query: str,
        system: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search AYUSH concepts across Ayurveda, Siddha, and Unani systems.
        Includes ICD-11 mappings and native language terms.
        """
        if not query.strip():
            return []

        search_pattern = f"%{query.lower()}%"
        params = {'query': search_pattern, 'limit': limit}

        # Search query with ICD mappings and native terms
        base_query = """
        SELECT 
            nc.code, 
            nc.display, 
            nc.system,
            nc.native_term,
            im.icd_code,
            im.icd_title,
            im.similarity_score
        FROM namaste_codes nc
        LEFT JOIN icd_mappings im ON nc.code = im.namc_code 
        WHERE (LOWER(nc.code) LIKE :query OR LOWER(nc.display) LIKE :query OR LOWER(nc.native_term) LIKE :query)
        """
        
        # Add system filter if specified
        if system:
            system = system.lower()
            if system in ['ayurveda', 'siddha', 'unani']:
                base_query += " AND LOWER(nc.system) = :system"
                params['system'] = system
            else:
                return []  # Invalid system
        
        # Add ordering and limit
        sql_query = base_query + " ORDER BY nc.display, im.similarity_score DESC LIMIT :limit"

        try:
            result = await session.execute(text(sql_query), params)
            rows = result.fetchall()

            # Group by concept and collect mappings
            concepts_dict = {}
            for row in rows:
                code = row[0]
                if code not in concepts_dict:
                    concepts_dict[code] = {
                        "code": code,
                        "term": row[1],
                        "system": row[2],
                        "native_term": row[3],
                        "icd_mappings": []
                    }
                
                # Add ICD mapping if it exists
                if row[4]:  # icd_code exists
                    concepts_dict[code]["icd_mappings"].append({
                        "icd_code": row[4],
                        "icd_title": row[5],
                        "similarity_score": row[6]
                    })

            concepts = list(concepts_dict.values())
            logger.info(f"Found {len(concepts)} concepts for query: '{query}'")
            return concepts
        except Exception as e:
            logger.error(f"Database search error for query '{query}': {e}")
            return []

    async def get_system_concepts(
        self,
        session,
        system: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get concepts from a specific AYUSH system with pagination.
        Includes ICD-11 mappings and native language terms.
        """
        try:
            system = system.lower()
            if system not in ['ayurveda', 'siddha', 'unani']:
                return []

            sql_query = """
            SELECT 
                nc.code, 
                nc.display, 
                nc.system,
                nc.native_term,
                im.icd_code,
                im.icd_title,
                im.similarity_score
            FROM (
                SELECT code, display, system, native_term
                FROM namaste_codes 
                WHERE LOWER(system) = :system 
                ORDER BY display
                LIMIT :limit OFFSET :offset
            ) nc
            LEFT JOIN icd_mappings im ON nc.code = im.namc_code 
            ORDER BY nc.display, im.similarity_score DESC
            """
            params = {'system': system, 'limit': limit, 'offset': offset}
            
            result = await session.execute(text(sql_query), params)
            rows = result.fetchall()

            # Group by concept and collect mappings
            concepts_dict = {}
            for row in rows:
                code = row[0]
                if code not in concepts_dict:
                    concepts_dict[code] = {
                        "code": code,
                        "term": row[1],
                        "system": row[2],
                        "native_term": row[3],
                        "icd_mappings": []
                    }
                
                # Add ICD mapping if it exists
                if row[4]:  # icd_code exists
                    concepts_dict[code]["icd_mappings"].append({
                        "icd_code": row[4],
                        "icd_title": row[5],
                        "similarity_score": row[6]
                    })

            concepts = list(concepts_dict.values())
            logger.info(f"Found {len(concepts)} concepts for system: '{system}'")
            return concepts
        except Exception as e:
            logger.error(f"Database error getting system concepts for '{system}': {e}")
            return []

    async def get_system_concepts_count(
        self,
        session,
        system: str
    ) -> int:
        """
        Get total count of concepts in a specific AYUSH system.
        """
        try:
            system = system.lower()
            if system not in ['ayurveda', 'siddha', 'unani']:
                return 0

            sql_query = """
            SELECT COUNT(DISTINCT nc.code)
            FROM namaste_codes nc
            WHERE LOWER(nc.system) = :system
            """
            params = {'system': system}
            
            result = await session.execute(text(sql_query), params)
            count = result.scalar()
            
            logger.info(f"Total concepts count for system '{system}': {count}")
            return count or 0
        except Exception as e:
            logger.error(f"Database error getting system concepts count for '{system}': {e}")
            return 0

    async def get_concept_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific AYUSH concept by its code from any system."""
        params = {'code': code}
        sql_query = "SELECT code, display, system FROM namaste_codes WHERE code = :code LIMIT 1"
        
        async with get_db_session() as session:
            result = await session.execute(text(sql_query), params)
            row = result.fetchone()

            if row:
                return {"code": row[0], "term": row[1], "system": row[2]}
            return None

    async def get_fhir_codesystem(self) -> Dict[str, Any]:
        """
        Generate a simplified FHIR R4 CodeSystem resource for all AYUSH terminologies.
        """
        sql_query = """
            (SELECT code, term, 'Ayurveda' as system FROM ayurveda_terms)
            UNION ALL
            (SELECT code, term, 'Siddha' as system FROM siddha_terms)
            UNION ALL
            (SELECT code, term, 'Unani' as system FROM unani_terms)
            ORDER BY system, code
        """
        async with get_db_session() as session:
            result = await session.execute(text(sql_query))
            rows = result.fetchall()

        concepts = [
            {
                "code": row[0],
                "display": row[1],
                "property": [{"code": "ayush-system", "valueCode": row[2].lower()}],
            }
            for row in rows
        ]

        codesystem = {
            "resourceType": "CodeSystem",
            "id": "ayush-terminology",
            "url": "http://your-domain.com/fhir/CodeSystem/AYUSH",
            "version": "1.0.0",
            "name": "AYUSHTerminology",
            "title": "AYUSH Standardized Terminologies",
            "status": "active",
            "experimental": False,
            "date": "2025-09-15",
            "publisher": "Your Organization Name",
            "description": "Unified terminology system for Ayurveda, Siddha, and Unani.",
            "content": "complete",
            "count": len(concepts),
            "property": [
                {
                    "code": "ayush-system",
                    "uri": "http://your-domain.com/fhir/property/ayush-system",
                    "description": "The AYUSH system the concept belongs to.",
                    "type": "code",
                }
            ],
            "concept": concepts,
        }
        return codesystem