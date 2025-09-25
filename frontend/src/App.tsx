import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { MagnifyingGlass, Globe, BookOpen, Beaker, ArrowRight, ExclamationTriangle, Server } from '@phosphor-icons/react'
import TerminologyExplorer from '@/components/TerminologyExplorer'
import MappingVisualization from '@/components/MappingVisualization'
import ClinicalDemo from '@/components/ClinicalDemo'
import DocumentationHub from '@/components/DocumentationHub'


function App() {
  const [activeTab, setActiveTab] = useState('explorer')

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-primary flex items-center justify-center">
                <Globe className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold">NAMASTE-ICD11 Service</h1>
                <p className="text-sm text-muted-foreground">Traditional Medicine & Global Health Standards</p>
              </div>
            </div>
            <Badge variant="outline" className="hidden sm:flex">
              FHIR R4 Compliant
            </Badge>
          </div>
        </div>
      </header>

      {/* Main Navigation */}
      <div className="container mx-auto px-4 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 lg:grid-cols-4 mb-8">
            <TabsTrigger value="explorer" className="flex items-center gap-2">
              <MagnifyingGlass className="h-4 w-4" />
              <span className="hidden sm:inline">Explorer</span>
            </TabsTrigger>
            <TabsTrigger value="mapping" className="flex items-center gap-2">
              <ArrowRight className="h-4 w-4" />
              <span className="hidden sm:inline">Mapping</span>
            </TabsTrigger>
            <TabsTrigger value="demo" className="flex items-center gap-2">
              <Beaker className="h-4 w-4" />
              <span className="hidden sm:inline">Demo</span>
            </TabsTrigger>
            <TabsTrigger value="docs" className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              <span className="hidden sm:inline">Docs</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="explorer" className="space-y-6">
            <div className="text-center space-y-2 mb-8">
              <h2 className="text-3xl font-bold">NAMASTE Terminology Explorer</h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Browse and search through traditional medicine diagnostic codes from Ayurveda, Siddha, and Unani systems
              </p>
            </div>
            
            <TerminologyExplorer />
          </TabsContent>

          <TabsContent value="mapping" className="space-y-6">
            <div className="text-center space-y-2 mb-8">
              <h2 className="text-3xl font-bold">ICD-11 Mapping Visualization</h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Explore the relationships between traditional medicine terms and international health standards
              </p>
            </div>
            
            <MappingVisualization />
          </TabsContent>

          <TabsContent value="demo" className="space-y-6">
            <div className="text-center space-y-2 mb-8">
              <h2 className="text-3xl font-bold">Interactive Dual-Coding Demo</h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Experience how traditional and modern medical coding work together in clinical practice
              </p>
            </div>
            <ClinicalDemo />
          </TabsContent>

          <TabsContent value="docs" className="space-y-6">
            <div className="text-center space-y-2 mb-8">
              <h2 className="text-3xl font-bold">Standards Documentation Hub</h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Comprehensive information about FHIR compliance, ABDM integration, and technical specifications
              </p>
            </div>
            <DocumentationHub />
          </TabsContent>
        </Tabs>
      </div>

      {/* Footer */}
      <footer className="border-t bg-muted/50 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="font-semibold mb-3">NAMASTE Initiative</h3>
              <p className="text-sm text-muted-foreground">
                National AYUSH Morbidity and Standardized Terminologies Electronic portal supporting traditional medicine integration.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-3">Global Standards</h3>
              <p className="text-sm text-muted-foreground">
                Compliant with WHO ICD-11 Traditional Medicine Module 2 and FHIR R4 specifications.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-3">ABDM Integration</h3>
              <p className="text-sm text-muted-foreground">
                Designed for seamless integration with India's Ayushman Bharat Digital Mission ecosystem.
              </p>
            </div>
          </div>
          <div className="border-t mt-8 pt-4 text-center text-sm text-muted-foreground">
            © 2024 Ministry of AYUSH & WHO Collaboration - Educational Demonstration
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App