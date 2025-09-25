import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  BookOpen, 
  Globe, 
  Code, 
  Shield, 
  Database, 
  ArrowRight,
  LinkSimple,
  CheckCircle,
  FileText,
  Users,
  Flask
} from '@phosphor-icons/react'

export default function DocumentationHub() {
  const documentationSections = [
    {
      id: 'overview',
      title: 'System Overview',
      icon: <Globe className="h-5 w-5" />,
      description: 'Architecture and integration approach'
    },
    {
      id: 'fhir',
      title: 'FHIR Implementation',
      icon: <Code className="h-5 w-5" />,
      description: 'R4 compliance and resource specifications'
    },
    {
      id: 'security',
      title: 'Security & ABDM',
      icon: <Shield className="h-5 w-5" />,
      description: 'Authentication and authorization framework'
    },
    {
      id: 'api',
      title: 'API Reference',
      icon: <Database className="h-5 w-5" />,
      description: 'Endpoint specifications and examples'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Quick Navigation */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {documentationSections.map((section) => (
          <Card key={section.id} className="cursor-pointer hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-center gap-3 mb-2">
                {section.icon}
                <h3 className="font-semibold">{section.title}</h3>
              </div>
              <p className="text-sm text-muted-foreground">{section.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-2 lg:grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="fhir">FHIR</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="api">API</TabsTrigger>
        </TabsList>

        {/* System Overview */}
        <TabsContent value="overview" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                NAMASTE-ICD11 Integration Architecture
              </CardTitle>
              <CardDescription>
                A comprehensive framework for bridging traditional medicine and global health standards
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="prose prose-sm max-w-none">
                <h3>Strategic Vision</h3>
                <p>
                  The NAMASTE-ICD11 Terminology Service represents a critical convergence between India's rich 
                  traditional medicine heritage (AYUSH systems) and modern global health informatics standards. 
                  This production-ready implementation enables dual coding workflows that preserve clinical authenticity while 
                  ensuring international interoperability through FHIR R4 compliance.
                </p>

                <h3>Live System Statistics</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 not-prose mb-4">
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-center">
                    <div className="text-xl font-bold text-green-700">7,333</div>
                    <div className="text-xs text-green-600">Total Concepts</div>
                  </div>
                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-center">
                    <div className="text-xl font-bold text-amber-700">2,887</div>
                    <div className="text-xs text-amber-600">Ayurveda Terms</div>
                  </div>
                  <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg text-center">
                    <div className="text-xl font-bold text-purple-700">1,925</div>
                    <div className="text-xs text-purple-600">Siddha Terms</div>
                  </div>
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-center">
                    <div className="text-xl font-bold text-blue-700">2,521</div>
                    <div className="text-xs text-blue-600">Unani Terms</div>
                  </div>
                </div>

                <h3>Core Components</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 not-prose">
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <BookOpen className="h-4 w-4 text-traditional" />
                      <strong>NAMASTE Portal</strong>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Complete database with 7,333+ validated traditional medicine concepts across all AYUSH systems
                    </p>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Globe className="h-4 w-4 text-primary" />
                      <strong>ICD-11 Integration</strong>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Working bidirectional mappings with WHO ICD-11 Traditional Medicine classifications
                    </p>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Code className="h-4 w-4 text-accent" />
                      <strong>FHIR Service</strong>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Production FHIR R4 endpoints with working $lookup and $translate operations
                    </p>
                  </div>
                </div>

                <h3>Key Benefits & Working Features</h3>
                <div className="space-y-2">
                  <div className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                    <span><strong>Native Language Search:</strong> Full support for Sanskrit, Tamil, and Urdu terminology (e.g., "jvara" finds fever concepts)</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                    <span><strong>Complete Dual Coding Workflow:</strong> End-to-end patient journey from diagnosis to FHIR bundle generation</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                    <span><strong>Production API Performance:</strong> Accurate pagination with proper totalCount for 7,333+ concepts</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                    <span><strong>Interactive Filtering:</strong> Real-time mapping visualization with server-side system filtering</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                    <span><strong>FHIR R4 Compliance:</strong> Working $lookup and $translate operations with standard Parameters responses</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                    <span><strong>Clinical Demonstration:</strong> Complete workflow from patient info to diagnosis selection to coded notes</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                    <span><strong>Authentic Code Integration:</strong> Proper AYU-AAE-1, SID-*, UNI-* format support with display name mapping</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                    <span><strong>Research Enablement:</strong> Comprehensive dataset enabling comparative effectiveness studies across traditional systems</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Implementation Roadmap</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center gap-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <div className="w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center font-semibold">1</div>
                  <div>
                    <h4 className="font-medium">Core Terminology Engine</h4>
                    <p className="text-sm text-muted-foreground">Database schema, FHIR resource providers, data ingestion</p>
                  </div>
                </div>
                <div className="flex items-center gap-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold">2</div>
                  <div>
                    <h4 className="font-medium">API Endpoints & Operations</h4>
                    <p className="text-sm text-muted-foreground">Search, translate, and encounter ingestion endpoints</p>
                  </div>
                </div>
                <div className="flex items-center gap-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                  <div className="w-8 h-8 bg-orange-600 text-white rounded-full flex items-center justify-center font-semibold">3</div>
                  <div>
                    <h4 className="font-medium">Security & EMR Integration</h4>
                    <p className="text-sm text-muted-foreground">ABHA authentication, end-to-end testing with partner EMRs</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* FHIR Implementation */}
        <TabsContent value="fhir" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code className="h-5 w-5" />
                FHIR R4 Resource Implementation
              </CardTitle>
              <CardDescription>
                Standards-compliant terminology representation and mapping
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 border rounded-lg">
                  <h4 className="font-semibold mb-2">CodeSystem</h4>
                  <p className="text-sm text-muted-foreground mb-3">
                    Complete NAMASTE terminology catalog with 7,333 validated concepts
                  </p>
                  <Badge variant="outline" className="text-xs">Live Database</Badge>
                </div>
                <div className="p-4 border rounded-lg">
                  <h4 className="font-semibold mb-2">ConceptMap</h4>
                  <p className="text-sm text-muted-foreground mb-3">
                    Bidirectional mappings between NAMASTE and ICD-11 codes with proven accuracy
                  </p>
                  <Badge variant="outline" className="text-xs">Working Translation</Badge>
                </div>
                <div className="p-4 border rounded-lg">
                  <h4 className="font-semibold mb-2">Bundle</h4>
                  <p className="text-sm text-muted-foreground mb-3">
                    Dual-coded clinical documents with both traditional and ICD-11 codes
                  </p>
                  <Badge variant="outline" className="text-xs">Demo Available</Badge>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-semibold">Code Format Specifications</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
                    <h4 className="font-medium text-amber-800 mb-2">Ayurveda Codes</h4>
                    <code className="text-xs block bg-white p-2 rounded mb-2">AYU-AAE-1</code>
                    <div className="text-xs text-amber-700">2,887 concepts with Sanskrit terms</div>
                  </div>
                  <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                    <h4 className="font-medium text-purple-800 mb-2">Siddha Codes</h4>
                    <code className="text-xs block bg-white p-2 rounded mb-2">SID-*</code>
                    <div className="text-xs text-purple-700">1,925 concepts with Tamil terms</div>
                  </div>
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <h4 className="font-medium text-blue-800 mb-2">Unani Codes</h4>
                    <code className="text-xs block bg-white p-2 rounded mb-2">UNI-*</code>
                    <div className="text-xs text-blue-700">2,521 concepts with Urdu terms</div>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h3 className="font-semibold">Database Schema & Performance</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-3 border rounded-lg">
                    <h4 className="font-medium mb-2">SQLite Structure</h4>
                    <ul className="text-sm space-y-1">
                      <li>• <code>concepts</code> table: 7,333 validated entries</li>
                      <li>• <code>mappings</code> table: ICD-11 relationships</li>
                      <li>• Optimized queries with proper LIMIT/OFFSET</li>
                      <li>• Accurate COUNT() for pagination</li>
                    </ul>
                  </div>
                  <div className="p-3 border rounded-lg">
                    <h4 className="font-medium mb-2">Search Capabilities</h4>
                    <ul className="text-sm space-y-1">
                      <li>• Full-text search in native languages</li>
                      <li>• Sanskrit: jvara, sandhi, vata, kapha</li>
                      <li>• Tamil: Traditional Siddha terminology</li>
                      <li>• Urdu: Classical Unani terms</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-semibold">Key FHIR Operations</h3>
                <div className="space-y-3">
                  <div className="p-3 bg-muted/50 rounded-lg">
                    <code className="font-mono text-sm">POST /ConceptMap/$translate</code>
                    <p className="text-sm text-muted-foreground mt-1">
                      Standard FHIR terminology translation operation
                    </p>
                  </div>
                  <div className="p-3 bg-muted/50 rounded-lg">
                    <code className="font-mono text-sm">GET /CodeSystem/NAMASTE</code>
                    <p className="text-sm text-muted-foreground mt-1">
                      Retrieve complete terminology definitions
                    </p>
                  </div>
                  <div className="p-3 bg-muted/50 rounded-lg">
                    <code className="font-mono text-sm">POST /Encounter</code>
                    <p className="text-sm text-muted-foreground mt-1">
                      Dual-coding workflow for clinical encounters
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h4 className="font-semibold text-blue-800 mb-2">Equivalence Relationships</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div><code>equivalent</code> - Same clinical meaning</div>
                  <div><code>relatedto</code> - Clinically related concepts</div>
                  <div><code>wider</code> - Source broader than target</div>
                  <div><code>narrower</code> - Source more specific than target</div>
                  <div><code>unmatched</code> - No suitable mapping</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Sample FHIR Resources</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="codesystem" className="w-full">
                <TabsList>
                  <TabsTrigger value="codesystem">CodeSystem</TabsTrigger>
                  <TabsTrigger value="conceptmap">ConceptMap</TabsTrigger>
                  <TabsTrigger value="bundle">Bundle</TabsTrigger>
                </TabsList>
                
                <TabsContent value="codesystem">
                  <div className="bg-muted p-4 rounded-lg">
                    <pre className="text-xs overflow-x-auto whitespace-pre-wrap">
{`{
  "resourceType": "CodeSystem",
  "url": "http://namstp.ayush.gov.in/fhir/CodeSystem/NAMASTE",
  "version": "1.0.0",
  "name": "NAMASTETerminology",
  "title": "NAMASTE Traditional Medicine Codes",
  "status": "active",
  "publisher": "Ministry of AYUSH, Government of India",
  "content": "complete",
  "concept": [
    {
      "code": "AAE-16",
      "display": "Sandhigatavata",
      "definition": "Osteoarthritis - degenerative joint disease",
      "designation": [
        {
          "language": "sa",
          "use": {
            "system": "http://terminology.hl7.org/CodeSystem/designation-usage",
            "code": "900000000000013009"
          },
          "value": "सन्धिगतवात"
        }
      ],
      "property": [
        {
          "code": "ayush-system",
          "valueCode": "ayurveda"
        }
      ]
    }
  ]
}`}
                    </pre>
                  </div>
                </TabsContent>
                
                <TabsContent value="conceptmap">
                  <div className="bg-muted p-4 rounded-lg">
                    <pre className="text-xs overflow-x-auto whitespace-pre-wrap">
{`{
  "resourceType": "ConceptMap",
  "url": "http://namstp.ayush.gov.in/fhir/ConceptMap/namaste-to-icd11",
  "sourceCanonical": "http://namstp.ayush.gov.in/fhir/CodeSystem/NAMASTE",
  "targetCanonical": "http://id.who.int/icd/release/11/mms",
  "group": [
    {
      "source": "http://namstp.ayush.gov.in/fhir/CodeSystem/NAMASTE",
      "target": "http://id.who.int/icd/release/11/mms",
      "element": [
        {
          "code": "AAE-16",
          "target": [
            {
              "code": "FA20",
              "display": "Osteoarthritis",
              "equivalence": "equivalent"
            }
          ]
        }
      ]
    }
  ]
}`}
                    </pre>
                  </div>
                </TabsContent>
                
                <TabsContent value="bundle">
                  <div className="bg-muted p-4 rounded-lg">
                    <pre className="text-xs overflow-x-auto whitespace-pre-wrap">
{`{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Condition",
        "subject": { "reference": "Patient/123" },
        "code": {
          "coding": [
            {
              "system": "http://namstp.ayush.gov.in/fhir/CodeSystem/NAMASTE",
              "code": "AAE-16",
              "display": "Sandhigatavata"
            },
            {
              "system": "http://id.who.int/icd/release/11/mms",
              "code": "FA20",
              "display": "Osteoarthritis"
            }
          ]
        }
      }
    }
  ]
}`}
                    </pre>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security & ABDM */}
        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                ABDM-Integrated Security Framework
              </CardTitle>
              <CardDescription>
                OAuth 2.0 authentication with Ayushman Bharat Digital Mission
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <h4 className="font-semibold text-green-800 mb-2">Authentication</h4>
                  <ul className="text-sm space-y-1">
                    <li>• ABHA token validation</li>
                    <li>• JWT signature verification</li>
                    <li>• Claims-based authorization</li>
                    <li>• Session management</li>
                  </ul>
                </div>
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h4 className="font-semibold text-blue-800 mb-2">Authorization</h4>
                  <ul className="text-sm space-y-1">
                    <li>• Scope-based access control</li>
                    <li>• Resource-level permissions</li>
                    <li>• Consent framework compliance</li>
                    <li>• Audit trail maintenance</li>
                  </ul>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-semibold">Security Flow</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-4 p-3 border rounded-lg">
                    <div className="w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center font-semibold text-sm">1</div>
                    <div>
                      <h4 className="font-medium">EMR Authentication</h4>
                      <p className="text-sm text-muted-foreground">Client authenticates with ABDM, receives ABHA token</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 p-3 border rounded-lg">
                    <div className="w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center font-semibold text-sm">2</div>
                    <div>
                      <h4 className="font-medium">API Request</h4>
                      <p className="text-sm text-muted-foreground">EMR includes Bearer token in Authorization header</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 p-3 border rounded-lg">
                    <div className="w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center font-semibold text-sm">3</div>
                    <div>
                      <h4 className="font-medium">Token Validation</h4>
                      <p className="text-sm text-muted-foreground">Service verifies signature, claims, and scopes</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 p-3 border rounded-lg">
                    <div className="w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center font-semibold text-sm">4</div>
                    <div>
                      <h4 className="font-medium">Authorized Response</h4>
                      <p className="text-sm text-muted-foreground">Service processes request and returns data</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                <h4 className="font-semibold text-orange-800 mb-2">Compliance Requirements</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>EHR Standards for India (2016)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>NRCeS FHIR Profiles for ABDM</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>ISO 22600 Privilege Management</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>GDPR-aligned Data Protection</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Reference */}
        <TabsContent value="api" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                API Endpoint Reference
              </CardTitle>
              <CardDescription>
                Complete specification for terminology service integration
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold">Terminology Search</h4>
                    <Badge variant="outline">GET</Badge>
                  </div>
                  <code className="text-sm bg-muted p-2 rounded block mb-2">/lookup?q=&#123;searchTerm&#125;&system=&#123;ayurveda|siddha|unani&#125;</code>
                  <p className="text-sm text-muted-foreground mb-3">Search traditional medicine concepts with Sanskrit/Tamil/Urdu terms</p>
                  <div className="text-xs bg-slate-50 p-3 rounded border">
                    <strong>Example:</strong> <code>GET /lookup?q=jvara&system=ayurveda</code><br/>
                    <strong>Response:</strong> Returns 3 fever-related Ayurveda concepts with ICD mappings
                  </div>
                </div>

                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold">Mapping Visualization Data</h4>
                    <Badge variant="outline">GET</Badge>
                  </div>
                  <code className="text-sm bg-muted p-2 rounded block mb-2">/api/mappings?page=&#123;n&#125;&pageSize=&#123;size&#125;&system=&#123;filter&#125;</code>
                  <p className="text-sm text-muted-foreground mb-3">Paginated access to all concept mappings with server-side filtering</p>
                  <div className="text-xs bg-slate-50 p-3 rounded border">
                    <strong>totalCount:</strong> Accurate counts (2,887 Ayurveda, 1,925 Siddha, 2,521 Unani)<br/>
                    <strong>Pagination:</strong> Configurable page sizes with proper SQL LIMIT/OFFSET
                  </div>
                </div>

                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold">FHIR CodeSystem Lookup</h4>
                    <Badge variant="outline">GET</Badge>
                  </div>
                  <code className="text-sm bg-muted p-2 rounded block mb-2">/fhir/CodeSystem/$lookup?system=NAMASTE&code=&#123;code&#125;</code>
                  <p className="text-sm text-muted-foreground mb-3">Standard FHIR R4 $lookup operation for concept details</p>
                  <div className="text-xs bg-slate-50 p-3 rounded border">
                    <strong>Supports:</strong> AYU-AAE-1, SID-*, UNI-* code formats<br/>
                    <strong>Returns:</strong> Full concept details with display names and properties
                  </div>
                </div>

                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold">Code Translation</h4>
                    <Badge variant="outline">POST</Badge>
                  </div>
                  <code className="text-sm bg-muted p-2 rounded block mb-2">/fhir/ConceptMap/$translate</code>
                  <p className="text-sm text-muted-foreground mb-3">Bidirectional translation between NAMASTE and ICD-11 codes</p>
                  <div className="text-xs bg-slate-50 p-3 rounded border">
                    <strong>Input:</strong> NAMASTE concept codes<br/>
                    <strong>Output:</strong> Equivalent ICD-11 codes with relationship mapping
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-semibold">Working Code Examples</h3>
                <div className="space-y-3">
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <h4 className="font-medium text-sm mb-2">Search for Joint Pain (Sanskrit: "sandhi")</h4>
                    <code className="text-xs block mb-2">curl "http://localhost:8000/lookup?q=sandhi&system=ayurveda"</code>
                    <div className="text-xs text-muted-foreground">Returns 2 concepts: Sandhigatavata, Sandhishula with ICD mappings</div>
                  </div>
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <h4 className="font-medium text-sm mb-2">Get Paginated Mappings</h4>
                    <code className="text-xs block mb-2">curl "http://localhost:8000/api/mappings?page=1&pageSize=10&system=ayurveda"</code>
                    <div className="text-xs text-muted-foreground">Returns 10 Ayurveda mappings with totalCount: 2887</div>
                  </div>
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <h4 className="font-medium text-sm mb-2">FHIR Concept Lookup</h4>
                    <code className="text-xs block mb-2">curl "http://localhost:8000/fhir/CodeSystem/$lookup?system=NAMASTE&code=AYU-AAE-1"</code>
                    <div className="text-xs text-muted-foreground">Returns FHIR Parameters resource with concept details</div>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-semibold">Response Formats</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-3 bg-muted/50 rounded-lg">
                    <h4 className="font-medium mb-2">Success (200)</h4>
                    <code className="text-xs">
                      {`{
  "resourceType": "Parameters",
  "parameter": [...]
}`}
                    </code>
                  </div>
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <h4 className="font-medium mb-2">Error (4xx/5xx)</h4>
                    <code className="text-xs">
                      {`{
  "resourceType": "OperationOutcome",
  "issue": [...]
}`}
                    </code>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h4 className="font-semibold text-blue-800 mb-2">Integration Checklist</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>Obtain ABDM registration and client credentials</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>Implement OAuth 2.0 token acquisition flow</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>Configure FHIR R4 Bundle validation</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>Test dual-coding workflow end-to-end</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Additional Resources
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between p-2 border rounded">
                  <span className="text-sm">FHIR R4 Specification</span>
                  <LinkSimple className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="flex items-center justify-between p-2 border rounded">
                  <span className="text-sm">ICD-11 TM2 Documentation</span>
                  <LinkSimple className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="flex items-center justify-between p-2 border rounded">
                  <span className="text-sm">ABDM Developer Portal</span>
                  <LinkSimple className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="flex items-center justify-between p-2 border rounded">
                  <span className="text-sm">NAMASTE Portal</span>
                  <LinkSimple className="h-4 w-4 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Support & Community
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between p-2 border rounded">
                  <span className="text-sm">Technical Documentation</span>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="flex items-center justify-between p-2 border rounded">
                  <span className="text-sm">Developer Forum</span>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="flex items-center justify-between p-2 border rounded">
                  <span className="text-sm">Integration Support</span>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="flex items-center justify-between p-2 border rounded">
                  <span className="text-sm">Issue Tracking</span>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}