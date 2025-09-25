import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle, XCircle, Clock, RefreshCw, WifiOff, Server } from '@phosphor-icons/react'
import { terminologyAPI } from '@/services/terminologyAPI'

export default function BackendStatusIndicator() {
  const [status, setStatus] = useState<{
    isConnected: boolean
    isHealthy: boolean
    latency: number
    version: string
    error?: string
  } | null>(null)
  const [loading, setLoading] = useState(true)
  const [isRetrying, setIsRetrying] = useState(false)

  const checkHealth = async () => {
    const startTime = Date.now()
    
    try {
      await terminologyAPI.healthCheck()
      const latency = Date.now() - startTime
      
      setStatus({
        isConnected: true,
        isHealthy: true,
        latency,
        version: '1.0.0'
      })
    } catch (error) {
      setStatus({
        isConnected: false,
        isHealthy: false,
        latency: 0,
        version: 'Unknown',
        error: error instanceof Error ? error.message : 'Connection failed'
      })
    }
  }

  useEffect(() => {
    checkHealth().finally(() => setLoading(false))
    
    // Check every 30 seconds
    const interval = setInterval(checkHealth, 30000)
    
    return () => clearInterval(interval)
  }, [])

  const handleRetry = async () => {
    setIsRetrying(true)
    await checkHealth()
    setIsRetrying(false)
  }

  const getStatusIcon = () => {
    if (loading || isRetrying) {
      return <RefreshCw className="h-4 w-4 animate-spin" />
    }
    
    if (!status) {
      return <Clock className="h-4 w-4 text-muted-foreground" />
    }
    
    if (status.isConnected && status.isHealthy) {
      return <CheckCircle className="h-4 w-4 text-green-600" />
    }
    
    if (status.isConnected && !status.isHealthy) {
      return <XCircle className="h-4 w-4 text-yellow-600" />
    }
    
    return <WifiOff className="h-4 w-4 text-red-600" />
  }

  const getStatusText = () => {
    if (loading) return "Checking..."
    if (!status) return "Unknown"
    
    if (status.isConnected && status.isHealthy) {
      return "Connected"
    }
    
    if (status.isConnected && !status.isHealthy) {
      return "Degraded"
    }
    
    return "Disconnected"
  }

  const getStatusColor = () => {
    if (loading || !status) return "outline"
    
    if (status.isConnected && status.isHealthy) return "default"
    if (status.isConnected && !status.isHealthy) return "secondary" 
    return "destructive"
  }

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Server className="h-5 w-5 text-muted-foreground" />
            <CardTitle className="text-sm">Backend Service</CardTitle>
          </div>
          <Badge variant={getStatusColor()} className="flex items-center gap-1">
            {getStatusIcon()}
            {getStatusText()}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-3">
        {status && (
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-muted-foreground">Latency:</span>
              <span className="ml-2 font-mono">{status.latency}ms</span>
            </div>
            <div>
              <span className="text-muted-foreground">Version:</span>
              <span className="ml-2 font-mono">{status.version}</span>
            </div>
          </div>
        )}

        {status?.error && (
          <Alert variant="destructive">
            <AlertDescription className="text-xs">
              Connection Error: {status.error}
            </AlertDescription>
          </Alert>
        )}

        {!status?.isConnected && (
          <div className="space-y-2">
            <Alert>
              <AlertDescription className="text-xs">
                Backend server not accessible. Make sure the development server is running:
              </AlertDescription>
            </Alert>
            
            <div className="bg-muted/50 p-3 rounded text-xs font-mono space-y-1">
              <div>1. Open terminal</div>
              <div>2. cd backend</div>
              <div>3. python start_dev_server.py</div>
            </div>

            <Button 
              size="sm" 
              variant="outline" 
              onClick={handleRetry}
              disabled={isRetrying}
              className="w-full"
            >
              {isRetrying ? (
                <RefreshCw className="h-3 w-3 animate-spin mr-2" />
              ) : (
                <RefreshCw className="h-3 w-3 mr-2" />
              )}
              Retry Connection
            </Button>
          </div>
        )}

        {status?.isConnected && status.isHealthy && (
          <div className="text-xs text-green-600 text-center">
            ✅ Backend ready for terminology search
          </div>
        )}
      </CardContent>
    </Card>
  )
}