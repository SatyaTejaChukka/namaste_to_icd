import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { MagnifyingGlass, Leaf, Globe, BookOpen, CircleNotch } from '@phosphor-icons/react'
import { lookupConcepts, useStatistics, type NAMASTEConcept } from '@/services/terminologyAPI'
import BackendStatusIndicator from '@/components/BackendStatusIndicator'

export default function TerminologyExplorer() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedSystem, setSelectedSystem] = useState<'all' | 'ayurveda' | 'siddha' | 'unani'>('all')
  const [selectedTerm, setSelectedTerm] = useState<NAMASTEConcept | null>(null)
  const [searchResults, setSearchResults] = useState<NAMASTEConcept[]>([])
  const [searchLoading, setSearchLoading] = useState(false)
  const [searchError, setSearchError] = useState<string | null>(null)

  // Get statistics for counts
  const { statistics, loading: statsLoading } = useStatistics()

  // Search function with debouncing
  useEffect(() => {
    const performSearch = async () => {
      if (!searchTerm.trim()) {
        setSearchResults([])
        setSearchError(null)
        return
      }

      setSearchLoading(true)
      setSearchError(null)

      try {
        const response = await lookupConcepts({
          q: searchTerm,
          system: selectedSystem === 'all' ? undefined : selectedSystem,
          limit: 20
        })
        setSearchResults(response.concepts)
      } catch (error) {
        setSearchError(error instanceof Error ? error.message : 'Failed to search terms')
      } finally {
        setSearchLoading(false)
      }
    }

    const timeoutId = setTimeout(performSearch, 300)
    return () => clearTimeout(timeoutId)
  }, [searchTerm, selectedSystem])

  // Load initial terms when no search term
  useEffect(() => {
    if (!searchTerm.trim()) {
      const loadInitialTerms = async () => {
        try {
          const response = await lookupConcepts({
            q: '',
            system: selectedSystem === 'all' ? undefined : selectedSystem,
            limit: 20
          })
          setSearchResults(response.concepts)
        } catch (error) {
          console.error('Failed to load initial terms:', error)
          setSearchError('Failed to connect to backend')
          setSearchResults([])
        }
      }
      loadInitialTerms()
    }
  }, [selectedSystem])

  // Use search results 
  const terminologies = searchResults
  const filteredTerminologies = terminologies.filter(term => {
    const matchesSystem = selectedSystem === 'all' || term.system === selectedSystem
    return matchesSystem
  })

  const getSystemIcon = (system: string) => {
    switch (system) {
      case 'ayurveda':
        return <Leaf className="h-4 w-4" />
      case 'siddha':
        return <Globe className="h-4 w-4" />
      case 'unani':
        return <BookOpen className="h-4 w-4" />
      default:
        return <MagnifyingGlass className="h-4 w-4" />
    }
  }

  const getSystemColor = (system: string) => {
    switch (system) {
      case 'ayurveda':
        return 'bg-traditional'
      case 'siddha':
        return 'bg-accent'
      case 'unani':
        return 'bg-secondary'
      default:
        return 'bg-muted'
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Backend Status and Search Panel */}
      <div className="lg:col-span-1 space-y-4">
        <BackendStatusIndicator />
        
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MagnifyingGlass className="h-5 w-5" />
              Search Terminologies
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Input
                placeholder="Search by code, term, or definition..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </div>
            
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium mb-3">Filter by System</h4>
                <div className="space-y-2">
                  <Button
                    variant={selectedSystem === 'all' ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSelectedSystem('all')}
                    className="w-full justify-start"
                  >
                    <Globe className="h-4 w-4" />
                    <span className="ml-2">All Systems</span>
                    <Badge variant="secondary" className="ml-auto">
                      {statsLoading ? "..." : (statistics?.total_terms || 0).toLocaleString()}
                    </Badge>
                  </Button>
                  
                  {(['ayurveda', 'siddha', 'unani'] as const).map(system => (
                    <Button
                      key={system}
                      variant={selectedSystem === system ? "default" : "outline"}
                      size="sm"
                      onClick={() => setSelectedSystem(system)}
                      className="w-full justify-start"
                    >
                      {getSystemIcon(system)}
                      <span className="ml-2 capitalize">{system}</span>
                      <Badge variant="secondary" className="ml-auto">
                        {statsLoading ? "..." : (statistics?.system_distribution?.[system.charAt(0).toUpperCase() + system.slice(1)] || 0).toLocaleString()}
                      </Badge>
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Stats</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Total Terms</span>
                <Badge variant="secondary">
                  {statsLoading ? "..." : (statistics?.total_terms || 0).toLocaleString()}
                </Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">ICD-11 Mappings</span>
                <Badge variant="secondary">
                  {statsLoading ? "..." : (statistics?.total_mappings || 0).toLocaleString()}
                </Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Ayurveda Terms</span>
                <Badge className={getSystemColor('ayurveda')}>
                  {statsLoading ? "..." : (statistics?.system_distribution?.Ayurveda || 0).toLocaleString()}
                </Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Siddha Terms</span>
                <Badge className={getSystemColor('siddha')}>
                  {statsLoading ? "..." : (statistics?.system_distribution?.Siddha || 0).toLocaleString()}
                </Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Unani Terms</span>
                <Badge className={getSystemColor('unani')}>
                  {statsLoading ? "..." : (statistics?.system_distribution?.Unani || 0).toLocaleString()}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Results Panel */}
      <div className="lg:col-span-3 space-y-4">
        {selectedTerm ? (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Term Details</CardTitle>
                <Button variant="outline" size="sm" onClick={() => setSelectedTerm(null)}>
                  Back to Results
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">NAMASTE Code</label>
                  <p className="text-lg font-mono">{selectedTerm.code}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">System</label>
                  <div className="flex items-center gap-2 mt-1">
                    {getSystemIcon(selectedTerm.system)}
                    <span className="capitalize font-medium">{selectedTerm.system}</span>
                  </div>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-muted-foreground">English Term</label>
                <p className="text-xl mt-1">{selectedTerm.term}</p>
              </div>

              {selectedTerm.native_term && (
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Native Term</label>
                  <p className="text-xl mt-1" style={{ fontFamily: 'serif' }}>{selectedTerm.native_term}</p>
                </div>
              )}

              <div>
                <label className="text-sm font-medium text-muted-foreground">System Description</label>
                <p className="mt-1 leading-relaxed">{selectedTerm.system.charAt(0).toUpperCase() + selectedTerm.system.slice(1)} traditional medicine system</p>
              </div>

              {selectedTerm.icd_mappings && selectedTerm.icd_mappings.length > 0 && (
                <div>
                  <label className="text-sm font-medium text-muted-foreground">
                    ICD-11 Mappings ({selectedTerm.icd_mappings.length})
                  </label>
                  <div className="mt-2 space-y-3">
                    {selectedTerm.icd_mappings.map((mapping, index) => (
                      <div key={index} className="p-3 border rounded-lg bg-blue-50/50">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1">
                            <div className="font-medium text-blue-700">
                              {mapping.icd_code}
                            </div>
                            <div className="text-sm text-gray-700 mt-1">
                              {mapping.icd_title}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-xs text-muted-foreground">Similarity</div>
                            <div className={`text-sm font-medium ${
                              mapping.similarity_score >= 0.8 ? 'text-green-600' :
                              mapping.similarity_score >= 0.6 ? 'text-yellow-600' : 'text-red-600'
                            }`}>
                              {(mapping.similarity_score * 100).toFixed(1)}%
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <label className="text-sm font-medium text-muted-foreground">Category</label>
                <Badge variant="outline" className="mt-1">
                  {selectedTerm.system} terminology
                </Badge>
              </div>
            </CardContent>
          </Card>
        ) : (
          <>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">
                Search Results ({filteredTerminologies.length})
              </h3>
              {searchTerm && (
                <Button variant="outline" size="sm" onClick={() => setSearchTerm('')}>
                  Clear Search
                </Button>
              )}
            </div>

            <div className="space-y-3">
              {(searchLoading || statsLoading) && (
                <div className="flex items-center justify-center p-8">
                  <CircleNotch className="h-6 w-6 animate-spin text-primary" />
                  <span className="ml-2 text-muted-foreground">Loading...</span>
                </div>
              )}

              {searchError && (
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800 mb-2">
                    {searchError.includes('sample data') ? '📋 Demo Mode: ' : '⚠️ '}{searchError}
                  </p>
                  {searchError.includes('sample data') && (
                    <div className="text-xs text-blue-600 space-y-1">
                      <div><strong>Try searching:</strong></div>
                      <div>• "sandhi" → Sandhigatavata (AAE-16)</div>
                      <div>• "fever" → Humma, Kaichal</div>
                      <div>• "vata" → Multiple Vata disorders</div>
                      <div>• "arthritis" → Joint-related conditions</div>
                    </div>
                  )}
                </div>
              )}

              {!searchLoading && !searchError && filteredTerminologies.map((term) => (
                <Card 
                  key={term.code}
                  className="cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => setSelectedTerm(term)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge variant="outline" className="font-mono text-xs">
                            {term.code}
                          </Badge>
                          <Badge className={`${getSystemColor(term.system)} text-xs`}>
                            {getSystemIcon(term.system)}
                            <span className="ml-1 capitalize">{term.system}</span>
                          </Badge>
                          {term.icd_mappings && term.icd_mappings.length > 0 && (
                            <Badge variant="secondary" className="text-xs">
                              {term.icd_mappings.length} ICD mapping{term.icd_mappings.length > 1 ? 's' : ''}
                            </Badge>
                          )}
                        </div>
                        <h4 className="font-medium text-lg truncate">{term.term}</h4>
                        {term.native_term && (
                          <p className="text-muted-foreground text-sm mb-1" style={{ fontFamily: 'serif' }}>
                            {term.native_term}
                          </p>
                        )}
                        <p className="text-muted-foreground text-xs mb-2">{term.code}</p>
                        
                        {/* Show best ICD mapping */}
                        {term.icd_mappings && term.icd_mappings.length > 0 && (
                          <div className="mt-2 p-2 bg-muted/50 rounded text-xs">
                            <div className="font-medium text-blue-700">
                              ICD-11: {term.icd_mappings[0].icd_code}
                            </div>
                            <div className="text-muted-foreground line-clamp-1">
                              {term.icd_mappings[0].icd_title}
                            </div>
                            <div className="text-xs text-green-600 mt-1">
                              Score: {(term.icd_mappings[0].similarity_score * 100).toFixed(1)}%
                            </div>
                          </div>
                        )}
                        
                        <p className="text-sm line-clamp-2 mt-2">Traditional {term.system} medicine concept</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}

              {!searchLoading && !searchError && filteredTerminologies.length === 0 && (
                <Card>
                  <CardContent className="p-8 text-center">
                    <MagnifyingGlass className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="font-medium mb-2">No terms found</h3>
                    <p className="text-muted-foreground">
                      Try adjusting your search criteria or browse all systems.
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}