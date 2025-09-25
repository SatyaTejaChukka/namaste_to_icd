import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  ArrowRight, 
  Funnel, 
  Warning, 
  TestTube, 
  CheckCircle,
  XCircle,
  BookOpen,
  Globe,
  CircleNotch
} from '@phosphor-icons/react'
import { useStatistics, getAllMappings, type ConceptMapping } from '@/services/terminologyAPI'

// Sample mappings data - this would come from the API in production
const sampleMappings: ConceptMapping[] = [
  {
    namasteCode: "AAE-16",
    namasteTerm: "Sandhigatavata",
    originalTerm: "सन्धिगतवात",
    system: "ayurveda",
    icd11Code: "FA3Z",
    icd11Term: "Osteoarthritis, unspecified",
    equivalence: "equivalent",
    confidence: 0.85,
    mappingType: "direct",
    clinicalNotes: "Strong correlation between Sandhigatavata and osteoarthritis symptoms"
  },
  {
    namasteCode: "AAE-23", 
    namasteTerm: "Amavata",
    originalTerm: "आमवात",
    system: "ayurveda",
    icd11Code: "FA20.0",
    icd11Term: "Rheumatoid arthritis",
    equivalence: "equivalent",
    confidence: 0.8,
    mappingType: "direct",
    clinicalNotes: "Amavata presentation closely matches rheumatoid arthritis criteria"
  },
  {
    namasteCode: "AAE-45",
    namasteTerm: "Prameha",
    originalTerm: "प्रमेह",
    system: "ayurveda", 
    icd11Code: "5A11",
    icd11Term: "Type 2 diabetes mellitus",
    equivalence: "wider",
    confidence: 0.7,
    mappingType: "contextual",
    clinicalNotes: "Prameha encompasses broader urinary disorders; diabetes is primary subset"
  },
  {
    namasteCode: "SSE-12",
    namasteTerm: "Vali Gunmam",
    originalTerm: "வாலி குன்மம்",
    system: "siddha",
    icd11Code: "2C7Y",
    icd11Term: "Benign neoplasm of abdomen, unspecified",
    equivalence: "relatedto",
    confidence: 0.6,
    mappingType: "contextual",
    clinicalNotes: "Traditional concept of abdominal masses; modern classification more specific"
  },
  {
    namasteCode: "UUE-55",
    namasteTerm: "Waram",
    originalTerm: "ورام",
    system: "unani",
    icd11Code: "EH90",
    icd11Term: "Inflammatory conditions",
    equivalence: "equivalent",
    confidence: 0.9,
    mappingType: "direct",
    clinicalNotes: "Waram directly corresponds to modern inflammatory disease classification"
  },
  {
    namasteCode: "AAE-89",
    namasteTerm: "Unmada",
    originalTerm: "उन्माद",
    system: "ayurveda",
    icd11Code: null,
    icd11Term: null,
    equivalence: "unmatched",
    confidence: 0,
    mappingType: "unmapped",
    clinicalNotes: "Complex traditional mental health concept with no direct ICD-11 equivalent"
  }
]

export default function MappingVisualization() {
  const [selectedMapping, setSelectedMapping] = useState<ConceptMapping | null>(null)
  const [filterEquivalence, setFilterEquivalence] = useState('all')
  const [filterSystem, setFilterSystem] = useState('all')
  const [mappings, setMappings] = useState<ConceptMapping[]>([])
  const [mappingsLoading, setMappingsLoading] = useState(true)
  const [mappingsError, setMappingsError] = useState<string | null>(null)
  const [totalMappings, setTotalMappings] = useState(0)
  const [currentPage, setCurrentPage] = useState(0)
  const [hasMoreMappings, setHasMoreMappings] = useState(false)

  // Get statistics for counts
  const { statistics, loading: statsLoading } = useStatistics()

  // Load mappings with current filters
  const loadMappings = async (page = 0, append = false) => {
    console.log('loadMappings called with:', { page, append, filterSystem, filterEquivalence })
    
    if (!append) {
      setMappingsLoading(true)
    }
    setMappingsError(null)
    
    try {
      const limit = 100
      const offset = page * limit
      const system = filterSystem === 'all' ? undefined : filterSystem
      const equivalence = filterEquivalence === 'all' ? undefined : filterEquivalence
      
      console.log('API call parameters:', { limit, offset, system, equivalence })
      
      const result = await getAllMappings(limit, offset, system, 0.0, equivalence)
      
      console.log('API response:', { 
        mappingsCount: result.mappings.length, 
        total: result.total, 
        hasMore: result.hasMore 
      })
      
      if (append) {
        setMappings(prev => [...prev, ...result.mappings])
      } else {
        setMappings(result.mappings)
      }
      
      setTotalMappings(result.total)
      setHasMoreMappings(result.hasMore)
      setCurrentPage(page)
    } catch (error) {
      console.error('Error loading mappings:', error)
      setMappingsError(`Failed to load mappings: ${error instanceof Error ? error.message : 'Unknown error'}`)
      // Fallback to sample data only if no mappings loaded
      if (!append && mappings.length === 0) {
        setMappings(sampleMappings)
        setTotalMappings(sampleMappings.length)
        setHasMoreMappings(false)
      }
    } finally {
      if (!append) {
        setMappingsLoading(false)
      }
    }
  }

  // Load mappings on component mount and filter changes
  useEffect(() => {
    loadMappings(0, false)
  }, [filterEquivalence, filterSystem])

  // Load more mappings
  const loadMoreMappings = () => {
    if (hasMoreMappings && !mappingsLoading) {
      loadMappings(currentPage + 1, true)
    }
  }

  const filteredMappings = mappings

  const getEquivalenceIcon = (equivalence: string) => {
    switch (equivalence) {
      case 'equivalent':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'relatedto':
        return <Warning className="h-4 w-4 text-yellow-600" />
      case 'wider':
      case 'narrower':
        return <ArrowRight className="h-4 w-4 text-blue-600" />
      case 'unmatched':
        return <XCircle className="h-4 w-4 text-red-600" />
      default:
        return <Warning className="h-4 w-4 text-gray-600" />
    }
  }

  const getEquivalenceColor = (equivalence: string) => {
    switch (equivalence) {
      case 'equivalent':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'relatedto':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'wider':
      case 'narrower':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'unmatched':
        return 'bg-red-100 text-red-800 border-red-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getSystemIcon = (system: string) => {
    switch (system) {
      case 'ayurveda':
        return <BookOpen className="h-4 w-4 text-traditional" />
      case 'siddha':
        return <Globe className="h-4 w-4 text-accent" />
      case 'unani':
        return <TestTube className="h-4 w-4 text-secondary" />
      default:
        return <BookOpen className="h-4 w-4" />
    }
  }

  const stats = statistics ? {
    total: statistics.total_terms,
    equivalent: statistics.equivalence_distribution?.equivalent || 0,
    relatedto: statistics.equivalence_distribution?.relatedto || 0,
    wider: statistics.equivalence_distribution?.wider || 0,
    unmatched: statistics.equivalence_distribution?.unmatched || 0
  } : {
    total: 0,
    equivalent: 0,
    relatedto: 0,
    wider: 0,
    unmatched: 0
  }

  return (
    <div className="space-y-6">
      {/* Statistics Dashboard */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-primary">
              {statsLoading ? <CircleNotch className="h-6 w-6 animate-spin mx-auto" /> : stats.total}
            </div>
            <div className="text-sm text-muted-foreground">Total Mappings</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600">
              {statsLoading ? <CircleNotch className="h-6 w-6 animate-spin mx-auto" /> : stats.equivalent}
            </div>
            <div className="text-sm text-muted-foreground">Equivalent</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-yellow-600">
              {statsLoading ? <CircleNotch className="h-6 w-6 animate-spin mx-auto" /> : stats.relatedto}
            </div>
            <div className="text-sm text-muted-foreground">Related</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">
              {statsLoading ? <CircleNotch className="h-6 w-6 animate-spin mx-auto" /> : stats.wider}
            </div>
            <div className="text-sm text-muted-foreground">Wider/Narrower</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-red-600">
              {statsLoading ? <CircleNotch className="h-6 w-6 animate-spin mx-auto" /> : stats.unmatched}
            </div>
            <div className="text-sm text-muted-foreground">Unmatched</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Filters and Legend */}
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Filter by Equivalence</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {['all', 'equivalent', 'relatedto', 'wider', 'unmatched'].map(eq => (
                  <Button
                    key={eq}
                    type="button"
                    variant={filterEquivalence === eq ? "default" : "outline"}
                    size="sm"
                    onClick={(e) => {
                      e.preventDefault()
                      e.stopPropagation()
                      console.log('Setting equivalence filter to:', eq)
                      setFilterEquivalence(eq)
                    }}
                    className="w-full justify-start"
                  >
                    {eq === 'all' ? (
                      <Globe className="h-4 w-4" />
                    ) : (
                      getEquivalenceIcon(eq)
                    )}
                    <span className="ml-2 capitalize">
                      {eq === 'all' ? 'All Types' : eq.replace('to', ' to')}
                    </span>
                    <Badge variant="secondary" className="ml-auto">
                      {statsLoading ? "..." : (
                        eq === 'all' 
                          ? totalMappings || mappings.length
                          : statistics?.equivalence_distribution?.[eq] || 0
                      )}
                    </Badge>
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Filter by System</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {['all', 'ayurveda', 'siddha', 'unani'].map(sys => (
                  <Button
                    key={sys}
                    type="button"
                    variant={filterSystem === sys ? "default" : "outline"}
                    size="sm"
                    onClick={(e) => {
                      e.preventDefault()
                      e.stopPropagation()
                      setFilterSystem(sys)
                    }}
                    className="w-full justify-start"
                  >
                    {sys === 'all' ? (
                      <Globe className="h-4 w-4" />
                    ) : (
                      getSystemIcon(sys)
                    )}
                    <span className="ml-2 capitalize">{sys === 'all' ? 'All Systems' : sys}</span>
                    <Badge variant="secondary" className="ml-auto">
                      {statsLoading ? "..." : (
                        sys === 'all' 
                          ? totalMappings || mappings.length
                          : statistics?.system_distribution?.[sys.charAt(0).toUpperCase() + sys.slice(1)] || 0
                      )}
                    </Badge>
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Mapping Legend</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span><strong>Equivalent:</strong> Same clinical meaning</span>
              </div>
              <div className="flex items-center gap-2">
                <Warning className="h-4 w-4 text-yellow-600" />
                <span><strong>Related:</strong> Clinically related concepts</span>
              </div>
              <div className="flex items-center gap-2">
                <ArrowRight className="h-4 w-4 text-blue-600" />
                <span><strong>Wider/Narrower:</strong> Broader or more specific</span>
              </div>
              <div className="flex items-center gap-2">
                <XCircle className="h-4 w-4 text-red-600" />
                <span><strong>Unmatched:</strong> No suitable mapping</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Mapping Details */}
        <div className="lg:col-span-2">
          {selectedMapping ? (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Mapping Details</CardTitle>
                  <Button variant="outline" size="sm" onClick={() => setSelectedMapping(null)}>
                    Back to List
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Source Term */}
                <div className="p-4 bg-muted/50 rounded-lg">
                  <div className="flex items-center gap-2 mb-3">
                    {getSystemIcon(selectedMapping.system)}
                    <Badge className="capitalize">{selectedMapping.system}</Badge>
                    <Badge variant="outline" className="font-mono">{selectedMapping.namasteCode}</Badge>
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{selectedMapping.namasteTerm}</h3>
                  <p className="text-lg text-muted-foreground">{selectedMapping.originalTerm}</p>
                </div>

                {/* Mapping Arrow */}
                <div className="flex items-center justify-center gap-3">
                  <ArrowRight className="h-8 w-8 text-muted-foreground" />
                  <Badge className={`${getEquivalenceColor(selectedMapping.equivalence)} px-3 py-1`}>
                    {getEquivalenceIcon(selectedMapping.equivalence)}
                    <span className="ml-2 capitalize">{selectedMapping.equivalence.replace('to', ' to')}</span>
                  </Badge>
                </div>

                {/* Target Term */}
                <div className="p-4 bg-primary/5 rounded-lg border border-primary/20">
                  {selectedMapping.icd11Code ? (
                    <>
                      <div className="flex items-center gap-2 mb-3">
                        <Globe className="h-4 w-4 text-primary" />
                        <Badge variant="outline" className="font-mono">{selectedMapping.icd11Code}</Badge>
                        <Badge>ICD-11 MMS</Badge>
                      </div>
                      <h3 className="text-xl font-semibold">{selectedMapping.icd11Term}</h3>
                    </>
                  ) : (
                    <div className="text-center py-4">
                      <XCircle className="h-12 w-12 text-red-500 mx-auto mb-2" />
                      <h3 className="text-lg font-semibold text-red-600">No ICD-11 Mapping</h3>
                      <p className="text-muted-foreground">This traditional medicine concept has no equivalent in ICD-11</p>
                    </div>
                  )}
                </div>

                {/* Mapping Metadata */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t">
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Mapping Type</label>
                    <p className="capitalize font-medium">{selectedMapping.mappingType}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Confidence Score</label>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-muted rounded-full h-2">
                        <div 
                          className="bg-primary h-2 rounded-full transition-all"
                          style={{ width: `${selectedMapping.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium">{(selectedMapping.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-muted-foreground">Clinical Notes</label>
                  <p className="mt-1 leading-relaxed">{selectedMapping.clinicalNotes}</p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold">
                    Mapping Relationships ({mappings.length}{totalMappings > mappings.length ? ` of ${totalMappings.toLocaleString()}` : ''})
                  </h3>
                  {(filterEquivalence !== 'all' || filterSystem !== 'all') && (
                    <p className="text-sm text-muted-foreground mt-1">
                      Filtered results - {mappings.length} shown
                    </p>
                  )}
                </div>
                <div className="flex gap-2">
                  {filterSystem !== 'all' && (
                    <Button 
                      type="button"
                      variant="outline" 
                      size="sm" 
                      onClick={(e) => {
                        e.preventDefault()
                        e.stopPropagation()
                        setFilterSystem('all')
                      }}
                    >
                      All Systems
                    </Button>
                  )}
                  {filterEquivalence !== 'all' && (
                    <Button 
                      type="button"
                      variant="outline" 
                      size="sm" 
                      onClick={(e) => {
                        e.preventDefault()
                        e.stopPropagation()
                        setFilterEquivalence('all')
                      }}
                    >
                      All Types
                    </Button>
                  )}
                </div>
              </div>

              {mappingsLoading && (
                <div className="flex items-center justify-center p-8">
                  <CircleNotch className="h-6 w-6 animate-spin text-primary" />
                  <span className="ml-2 text-muted-foreground">Loading mappings...</span>
                </div>
              )}

              {mappingsError && (
                <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Warning className="h-4 w-4 text-amber-600" />
                    <p className="text-sm font-medium text-amber-800">Backend Status</p>
                  </div>
                  <p className="text-sm text-amber-700">{mappingsError}</p>
                  <p className="text-xs text-amber-600 mt-1">
                    Displaying authentic sample mappings from the NAMASTE-ICD11 service
                  </p>
                </div>
              )}

              {!mappingsLoading && !mappingsError && mappings.map((mapping) => (
                <Card 
                  key={mapping.namasteCode}
                  className="cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => setSelectedMapping(mapping)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2">
                          {getSystemIcon(mapping.system)}
                          <Badge variant="outline" className="font-mono text-xs">{mapping.namasteCode}</Badge>
                          <Badge className={`${getEquivalenceColor(mapping.equivalence)} text-xs`}>
                            {getEquivalenceIcon(mapping.equivalence)}
                            <span className="ml-1">{mapping.equivalence}</span>
                          </Badge>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-2 items-center">
                          <div>
                            <h4 className="font-medium">{mapping.namasteTerm}</h4>
                            <p className="text-sm text-muted-foreground">{mapping.originalTerm}</p>
                          </div>
                          
                          <div className="flex justify-center">
                            <ArrowRight className="h-5 w-5 text-muted-foreground" />
                          </div>
                          
                          <div>
                            {mapping.icd11Code ? (
                              <>
                                <h4 className="font-medium">{mapping.icd11Term}</h4>
                                <p className="text-sm text-muted-foreground font-mono">{mapping.icd11Code}</p>
                              </>
                            ) : (
                              <p className="text-sm text-red-600 italic">No mapping available</p>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}

              {!mappingsLoading && !mappingsError && mappings.length === 0 && (
                <Card>
                  <CardContent className="p-8 text-center">
                    <XCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="font-medium mb-2">No mappings found</h3>
                    <p className="text-muted-foreground">
                      Try adjusting your filter criteria or check back later.
                    </p>
                  </CardContent>
                </Card>
              )}

              {/* Load More Button */}
              {!mappingsLoading && hasMoreMappings && (
                <div className="flex justify-center mt-6">
                  <Button 
                    type="button"
                    variant="outline" 
                    onClick={(e) => {
                      e.preventDefault()
                      e.stopPropagation()
                      loadMoreMappings()
                    }}
                    disabled={mappingsLoading}
                  >
                    Load More Mappings
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}