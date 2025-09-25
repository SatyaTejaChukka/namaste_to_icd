import { useState, useEffect } from 'react'

/**
 * NAMASTE-ICD11 Terminology Service API
 * Provides integration with the FastAPI backend for traditional medicine terminology services
 */

// Types for ICD-11 mappings
export interface ICDMapping {
  icd_code: string
  icd_title: string
  similarity_score: number
}

// Types for NAMASTE terminology concepts
export interface NAMASTEConcept {
  code: string
  term: string  // Display term for the concept
  system: 'ayurveda' | 'siddha' | 'unani'
  native_term?: string  // Native language term (Devanagari, Tamil, Arabic)
  icd_mappings?: ICDMapping[]  // ICD-11 mappings with similarity scores
}

// Types for concept mappings between NAMASTE and ICD-11
export interface ConceptMapping {
  namasteCode: string
  namasteTerm: string
  originalTerm: string
  system: string
  icd11Code: string | null
  icd11Term: string | null
  equivalence: 'equivalent' | 'relatedto' | 'wider' | 'narrower' | 'unmatched'
  confidence: number
  mappingType: 'direct' | 'contextual' | 'clustered' | 'unmapped'
  clinicalNotes: string
}

// Types for lookup requests and responses
export interface LookupRequest {
  q: string
  system?: 'ayurveda' | 'siddha' | 'unani'
  limit?: number
}

export interface LookupResponse {
  concepts: NAMASTEConcept[]
  totalCount: number
}

// Types for translation requests and responses
export interface TranslateRequest {
  system: string
  code: string
  target: string
}

export interface TranslateResponse {
  result: boolean
  message?: string
  match?: ConceptMapping[]
}

// Types for encounter ingestion
export interface EncounterData {
  patientId: string
  encounterId: string
  namasteCode: string
  clinicalNotes?: string
}

// Statistics interface
export interface Statistics {
  total_terms: number
  total_mappings: number
  total_encounters: number
  system_distribution: {
    Ayurveda: number
    Siddha: number
    Unani: number
  }
  equivalence_distribution: {
    equivalent: number
    relatedto: number
    wider: number
    narrower: number
    unmatched: number
  }
}

const API_BASE_URL = 'http://localhost:8000'

class TerminologyAPI {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private generateClinicalNotes(
    namasteTerm: string, 
    namasteSystem: string, 
    icd11Term: string | null, 
    confidence: number
  ): string {
    if (!icd11Term) {
      return "No ICD-11 mapping available - requires clinical expert review for appropriate classification."
    }

    // Define confidence levels and their descriptions
    let confidenceDesc: string, relationship: string
    if (confidence >= 0.8) {
      confidenceDesc = "High confidence mapping"
      relationship = "Strong clinical correlation"
    } else if (confidence >= 0.6) {
      confidenceDesc = "Moderate confidence mapping"
      relationship = "Good clinical alignment"
    } else if (confidence >= 0.4) {
      confidenceDesc = "Fair confidence mapping"
      relationship = "Partial clinical overlap"
    } else {
      confidenceDesc = "Low confidence mapping"
      relationship = "Limited clinical correlation"
    }

    // Generate system-specific insights
    let systemInsight = ""
    if (namasteSystem.toLowerCase() === "ayurveda") {
      systemInsight = "Consider traditional Ayurvedic diagnostic principles and constitutional factors."
    } else if (namasteSystem.toLowerCase() === "siddha") {
      systemInsight = "Evaluate based on Siddha medicine's tridosha and bodily constituent assessment."
    } else if (namasteSystem.toLowerCase() === "unani") {
      systemInsight = "Apply Unani medicine's temperament (mizaj) and humoral balance principles."
    }

    // Create meaningful clinical note
    return `${confidenceDesc} (score: ${confidence.toFixed(2)}). ${relationship} between '${namasteTerm}' and '${icd11Term}'. ${systemInsight}`
  }

  private isGenericMapping(namasteTerm: string, icd11Term: string | null): boolean {
    if (!icd11Term) return false

    // Generic NAMASTE terms to exclude
    const genericNamasteTerms = new Set([
      'disorder', 'disease', 'condition', '-', 'unspecified', 
      'other', 'general', 'various', 'multiple'
    ])

    // Generic ICD terms to exclude
    const genericIcdPatterns = [
      'unspecified', 'other specified', 'not otherwise specified',
      'not elsewhere classified', ', unspecified', ', other'
    ]

    // Check NAMASTE term for generic words
    const namasteLower = namasteTerm.toLowerCase().trim()
    if (genericNamasteTerms.has(namasteLower)) {
      return true
    }

    // Check if NAMASTE term is just a single generic word
    if (namasteLower.split(' ').length === 1 && ['disorder', 'disease', '-'].includes(namasteLower)) {
      return true
    }

    // Check ICD title for generic patterns
    const icdLower = icd11Term.toLowerCase()
    for (const pattern of genericIcdPatterns) {
      if (icdLower.includes(pattern)) {
        return true
      }
    }

    // Filter out mappings where ICD title ends with generic qualifiers
    if (icdLower.endsWith(', unspecified') || icdLower.endsWith(', other')) {
      return true
    }

    return false
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      return response.json()
    } catch (error) {
      // Log error for debugging but don't expose internal details
      console.error(`API Request failed for ${endpoint}:`, error)
      throw new Error(`Failed to connect to backend service`)
    }
  }

  // Lookup endpoint
  async lookup(request: LookupRequest): Promise<LookupResponse> {
    const params = new URLSearchParams({
      q: request.q,
      ...(request.system && { system: request.system }),
      ...(request.limit && { limit: request.limit.toString() }),
    })

    return this.request<LookupResponse>(`/lookup?${params}`)
  }

  // Translation endpoint
  async translate(request: TranslateRequest): Promise<TranslateResponse> {
    return this.request<TranslateResponse>('/fhir/ConceptMap/$translate', {
      method: 'POST',
      body: JSON.stringify({
        resourceType: 'Parameters',
        parameter: [
          { name: 'system', valueUri: request.system },
          { name: 'code', valueCode: request.code },
          { name: 'target', valueUri: request.target },
        ],
      }),
    })
  }

  // Encounter ingestion endpoint
  async ingestEncounter(encounter: EncounterData): Promise<any> {
    return this.request('/api/encounters', {
      method: 'POST',
      body: JSON.stringify({
        resourceType: 'Bundle',
        type: 'transaction',
        entry: [
          {
            resource: {
              resourceType: 'Encounter',
              id: encounter.encounterId,
              subject: { reference: `Patient/${encounter.patientId}` },
              status: 'finished',
            },
          },
          {
            resource: {
              resourceType: 'Condition',
              subject: { reference: `Patient/${encounter.patientId}` },
              encounter: { reference: `Encounter/${encounter.encounterId}` },
              code: {
                coding: [
                  {
                    system: 'http://namstp.ayush.gov.in/fhir/CodeSystem/NAMASTE',
                    code: encounter.namasteCode,
                  },
                ],
              },
            },
          },
        ],
      }),
    })
  }

  // Statistics endpoint
  async getStatistics(): Promise<Statistics> {
    return this.request<Statistics>('/statistics')
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/health')
  }

  // Get system mappings
  async getSystemMappings(system: string, limit: number = 50, offset: number = 0): Promise<ConceptMapping[]> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString()
    })
    
    const mappings = await this.request<any[]>(`/api/mappings/${system}?${params}`)
    
    // Transform backend response to frontend format
    return mappings
      .filter(mapping => !this.isGenericMapping(mapping.source_term, mapping.target_term))
      .map(mapping => ({
        namasteCode: mapping.source_code,
        namasteTerm: mapping.source_term,
        originalTerm: mapping.source_term, // Backend doesn't have original term separate
        system: mapping.system.toLowerCase(),
        icd11Code: mapping.target_code,
        icd11Term: mapping.target_term,
        equivalence: mapping.equivalence || 'relatedto',
        confidence: mapping.confidence || 0.8,
        mappingType: mapping.mapping_type || 'direct',
        clinicalNotes: this.generateClinicalNotes(
          mapping.source_term,
          mapping.system,
          mapping.target_term,
          mapping.confidence || 0.8
        )
      }))
  }

  // Get all mappings with pagination and filtering
  async getAllMappings(
    limit: number = 100, 
    offset: number = 0, 
    system?: string, 
    minConfidence: number = 0.0, 
    equivalence?: string
  ): Promise<{mappings: ConceptMapping[], total: number, hasMore: boolean}> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
      min_confidence: minConfidence.toString()
    })
    
    if (system) params.append('system', system)
    if (equivalence) params.append('equivalence', equivalence)
    
    const response = await this.request<{
      mappings: any[], 
      total: number, 
      limit: number, 
      offset: number, 
      has_more: boolean
    }>(`/api/mappings?${params}`)
    
    // Transform backend response to frontend format
    const mappings = response.mappings
      .filter(mapping => !this.isGenericMapping(mapping.source_term, mapping.target_term))
      .map(mapping => ({
        namasteCode: mapping.source_code,
        namasteTerm: mapping.source_term,
        originalTerm: mapping.original_term || mapping.source_term,
        system: mapping.system.toLowerCase(),
        icd11Code: mapping.target_code,
        icd11Term: mapping.target_term,
        equivalence: mapping.equivalence || 'relatedto',
        confidence: mapping.confidence || 0.8,
        mappingType: mapping.mapping_type || 'direct',
        clinicalNotes: this.generateClinicalNotes(
          mapping.source_term,
          mapping.system,
          mapping.target_term,
          mapping.confidence || 0.8
        )
      }))
    
    return {
      mappings,
      total: response.total,
      hasMore: response.has_more
    }
  }

  // Validation endpoint
  async validateConcept(system: string, code: string): Promise<{valid: boolean, reason: string}> {
    return this.request<{valid: boolean, reason: string}>(`/api/validate/${system}/${code}`)
  }
}

// Create API instance
const terminologyAPI = new TerminologyAPI()

// Enhanced lookup function with fallback to sample data
async function lookupConcepts(request: LookupRequest): Promise<LookupResponse> {
  return await terminologyAPI.lookup(request)
}

// Enhanced translate function with fallback
async function translateConcept(request: TranslateRequest): Promise<TranslateResponse> {
  return await terminologyAPI.translate(request)
}

// Enhanced statistics function with fallback
async function getStatistics(): Promise<Statistics> {
  return await terminologyAPI.getStatistics()
}

// Get mappings for a specific system
async function getSystemMappings(system: string, limit: number = 50): Promise<ConceptMapping[]> {
  return await terminologyAPI.getSystemMappings(system, limit)
}

// Get all mappings with pagination and filtering
async function getAllMappings(
  limit: number = 100, 
  offset: number = 0, 
  system?: string, 
  minConfidence: number = 0.0, 
  equivalence?: string
): Promise<{mappings: ConceptMapping[], total: number, hasMore: boolean}> {
  return await terminologyAPI.getAllMappings(limit, offset, system, minConfidence, equivalence)
}

// Export enhanced functions
export { terminologyAPI, lookupConcepts, translateConcept, getStatistics, getSystemMappings, getAllMappings }

// React hook for statistics
export function useStatistics() {
  const [statistics, setStatistics] = useState<Statistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStatistics = async () => {
      setLoading(true)
      setError(null)

      try {
        const stats = await getStatistics()
        setStatistics(stats)
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch statistics'
        setError(errorMessage)
      } finally {
        setLoading(false)
      }
    }

    fetchStatistics()
  }, [])

  const refetch = async () => {
    const stats = await getStatistics()
    setStatistics(stats)
  }

  return { statistics, loading, error, refetch }
}