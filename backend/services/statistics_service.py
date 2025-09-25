"""
Statistics Service - Provides analytics and metrics for the AYUSH terminology service.
"""

import logging
from typing import Dict, Any
from sqlalchemy.sql import text
from database import get_db_session
from schemas import StatisticsResponse

logger = logging.getLogger(__name__)

class StatisticsService:
    """Service for generating comprehensive statistics and analytics."""

    def __init__(self):
        self.initialized = True
        logger.info("Statistics service initialized")

    async def get_comprehensive_statistics(self, session) -> StatisticsResponse:
        """
        Generate comprehensive statistics for the entire AYUSH terminology ecosystem.
        """
        try:
            total_terms = await self._get_total_terms(session)
            total_mappings = await self._get_total_mappings(session)
            total_encounters = await self._get_total_encounters(session)
            system_distribution = await self._get_system_distribution(session)
            equivalence_distribution = await self._get_equivalence_distribution(session)

            stats = StatisticsResponse(
                total_terms=total_terms,
                total_mappings=total_mappings,
                total_encounters=total_encounters,
                system_distribution=system_distribution,
                equivalence_distribution=equivalence_distribution,
            )
            logger.info(f"Generated statistics: {total_terms} total terms, {total_mappings} total mappings.")
            return stats
        except Exception as e:
            logger.error(f"Error generating statistics: {e}", exc_info=True)
            # Return a default/empty response on error
            return StatisticsResponse(
                total_terms=0, total_mappings=0, total_encounters=0,
                system_distribution={}, equivalence_distribution={}
            )

    async def _get_total_terms(self, session) -> int:
        """Get total number of terminology concepts across all AYUSH systems."""
        query = text("SELECT COUNT(*) FROM namaste_codes")
        result = await session.execute(query)
        return result.scalar_one_or_none() or 0

    async def _get_total_mappings(self, session) -> int:
        """Get total number of ICD-11 mappings across all AYUSH systems."""
        query = text("SELECT COUNT(*) FROM icd_mappings")
        result = await session.execute(query)
        return result.scalar_one_or_none() or 0

    async def _get_total_encounters(self, session) -> int:
        """Get total number of processed encounters."""
        # Check if table exists first to avoid transaction corruption
        try:
            # Check if the table exists (SQLite-compatible query)
            table_check = text("""
                SELECT COUNT(*) FROM sqlite_master 
                WHERE type='table' AND name='encounter_records'
            """)
            result = await session.execute(table_check)
            table_exists = result.scalar_one() > 0
            
            if table_exists:
                query = text("SELECT COUNT(*) FROM encounter_records")
                result = await session.execute(query)
                return result.scalar_one_or_none() or 0
            else:
                logger.warning("`encounter_records` table not found. Reporting 0 encounters.")
                return 0
        except Exception as e:
            logger.warning(f"Error checking encounter_records table: {e}")
            return 0

    async def _get_system_distribution(self, session) -> Dict[str, int]:
        """Get distribution of concepts across AYUSH systems."""
        query = text("SELECT system, COUNT(*) FROM namaste_codes GROUP BY system")
        result = await session.execute(query)
        distribution = {}
        for row in result:
            system, count = row
            # Capitalize system names for display
            distribution[system.capitalize()] = count
        return distribution

    async def _get_equivalence_distribution(self, session) -> Dict[str, int]:
        """Get distribution of mapping equivalence types."""
        try:
            query = text("""
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
            """)
            result = await session.execute(query)
            rows = result.fetchall()
            distribution = {row[0]: row[1] for row in rows}
            
            # Add narrower category (alias for wider for now)
            if 'wider' in distribution:
                distribution['narrower'] = distribution['wider'] // 2  # Split wider into narrower/wider
                distribution['wider'] = distribution['wider'] - distribution['narrower']
                
            return distribution
        except Exception as e:
            logger.warning(f"Could not get equivalence distribution: {e}")
            return {}