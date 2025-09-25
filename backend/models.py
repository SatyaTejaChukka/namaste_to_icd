"""
Database models for the AYUSH Terminology Service.
SQLAlchemy models for Ayurveda, Siddha, Unani, and ICD-11 terminologies,
aligned with the project's architectural blueprint.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

# --- Terminology Models ---

class AyurvedaTerm(Base):
    """Ayurveda Terminology Codes"""
    __tablename__ = "ayurveda_terms"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    term = Column(String, nullable=False)
    system = Column(String, default='Ayurveda', nullable=False)

class SiddhaTerm(Base):
    """Siddha Terminology Codes"""
    __tablename__ = "siddha_terms"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    term = Column(String, nullable=False)
    system = Column(String, default='Siddha', nullable=False)

class UnaniTerm(Base):
    """Unani Terminology Codes"""
    __tablename__ = "unani_terms"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    term = Column(String, nullable=False)
    system = Column(String, default='Unani', nullable=False)

class ICD11Code(Base):
    """
    ICD-11 Classification Codes from WHO.
    Focus on Traditional Medicine Module 2 (TM2) and related codes.
    """
    __tablename__ = "icd11_codes"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    # Retaining a simplified structure as per the core requirement
    # Additional fields like definition, chapter can be added if needed
    is_tm2_module = Column(String, default='false', nullable=False)

# --- Mapping Models ---

class AyurvedaICDMapping(Base):
    """Mappings between Ayurveda and ICD-11 codes."""
    __tablename__ = "ayurveda_icd_mappings"
    id = Column(Integer, primary_key=True, index=True)
    ayurveda_code = Column(String, index=True, nullable=False)
    ayurveda_term = Column(String, nullable=False)
    icd_code = Column(String, index=True)
    icd_term = Column(String)
    match_type = Column(String) # e.g., 'Exact', 'Narrow', 'Broad'

class SiddhaICDMapping(Base):
    """Mappings between Siddha and ICD-11 codes."""
    __tablename__ = "siddha_icd_mappings"
    id = Column(Integer, primary_key=True, index=True)
    siddha_code = Column(String, index=True, nullable=False)
    siddha_term = Column(String, nullable=False)
    icd_code = Column(String, index=True)
    icd_term = Column(String)
    match_type = Column(String)

class UnaniICDMapping(Base):
    """Mappings between Unani and ICD-11 codes."""
    __tablename__ = "unani_icd_mappings"
    id = Column(Integer, primary_key=True, index=True)
    unani_code = Column(String, index=True, nullable=False)
    unani_term = Column(String, nullable=False)
    icd_code = Column(String, index=True)
    icd_term = Column(String)
    match_type = Column(String)

# --- Supporting Models from Architectural Blueprint ---

class EncounterRecord(Base):
    """
    Clinical encounter records with dual coding.
    Stores FHIR Bundle data for encounters using AYUSH terminologies.
    """
    __tablename__ = "encounter_records"
    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(String, nullable=False, index=True)
    patient_id = Column(String, nullable=False, index=True)
    ayush_codes = Column(String, nullable=False)  # Comma-separated list
    icd11_codes = Column(String)  # Auto-generated from mappings
    fhir_bundle = Column(JSON, nullable=False)  # Complete FHIR Bundle
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TerminologyVersion(Base):
    """
    Version tracking for terminology updates.
    Maintains history of AYUSH and ICD-11 updates.
    """
    __tablename__ = "terminology_versions"
    id = Column(Integer, primary_key=True, index=True)
    terminology_type = Column(String, nullable=False)  # e.g., ayurveda, siddha, icd11
    version = Column(String, nullable=False)
    release_date = Column(DateTime(timezone=True), nullable=False)
    description = Column(Text)
    is_active = Column(String, default='true', nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())