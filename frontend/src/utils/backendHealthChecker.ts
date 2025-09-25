/**
 * Backend Health Checker for NAMASTE Terminology Service
 * Monitors connection status and service health
 */

const BACKEND_URL = process.env.NODE_ENV === 'production' 
  ? 'https://api.namaste-icd11.health.gov.in' 
  : 'http://localhost:8000'

export interface BackendStatus {
  isConnected: boolean
  isHealthy: boolean
  latency: number
  version: string
  error?: string
  lastChecked: Date
}

export class BackendHealthChecker {
  private static instance: BackendHealthChecker
  private status: BackendStatus | null = null
  private listeners: ((status: BackendStatus | null) => void)[] = []
  private checkInterval: number | null = null

  static getInstance(): BackendHealthChecker {
    if (!BackendHealthChecker.instance) {
      BackendHealthChecker.instance = new BackendHealthChecker()
    }
    return BackendHealthChecker.instance
  }

  async checkHealth(): Promise<BackendStatus> {
    const startTime = performance.now()
    
    try {
      const response = await fetch(`${BACKEND_URL}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        // Add timeout
        signal: AbortSignal.timeout(5000)
      })

      const latency = Math.round(performance.now() - startTime)

      if (response.ok) {
        const healthData = await response.json()
        
        this.status = {
          isConnected: true,
          isHealthy: healthData.status === 'healthy',
          latency,
          version: healthData.version || '1.0.0',
          lastChecked: new Date()
        }
      } else {
        this.status = {
          isConnected: true,
          isHealthy: false,
          latency,
          version: 'unknown',
          error: `HTTP ${response.status}`,
          lastChecked: new Date()
        }
      }
    } catch (error) {
      const latency = Math.round(performance.now() - startTime)
      
      this.status = {
        isConnected: false,
        isHealthy: false,
        latency,
        version: 'unknown',
        error: error instanceof Error ? error.message : 'Connection failed',
        lastChecked: new Date()
      }
    }

    this.notifyListeners()
    return this.status
  }

  subscribe(listener: (status: BackendStatus | null) => void): () => void {
    this.listeners.push(listener)
    
    // Immediately notify with current status
    listener(this.status)
    
    // Return unsubscribe function
    return () => {
      const index = this.listeners.indexOf(listener)
      if (index > -1) {
        this.listeners.splice(index, 1)
      }
    }
  }

  startPeriodicCheck(intervalMs: number = 30000): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval)
    }

    // Initial check
    this.checkHealth()

    // Set up periodic checks
    this.checkInterval = window.setInterval(() => {
      this.checkHealth()
    }, intervalMs)
  }

  stopPeriodicCheck(): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval)
      this.checkInterval = null
    }
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.status))
  }

  getStatus(): BackendStatus | null {
    return this.status
  }
}

// React hook for backend status
import { useState, useEffect } from 'react'

export function useBackendStatus(enablePeriodicCheck: boolean = false): {
  status: BackendStatus | null
  loading: boolean
  checkNow: () => Promise<void>
} {
  const [status, setStatus] = useState<BackendStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checker = BackendHealthChecker.getInstance()
    
    // Subscribe to status updates
    const unsubscribe = checker.subscribe((newStatus) => {
      setStatus(newStatus)
      setLoading(false)
    })

    // Start periodic checking if enabled
    if (enablePeriodicCheck) {
      checker.startPeriodicCheck(30000) // Check every 30 seconds
    } else {
      // Just do an initial check
      checker.checkHealth().finally(() => setLoading(false))
    }

    return () => {
      unsubscribe()
      if (enablePeriodicCheck) {
        checker.stopPeriodicCheck()
      }
    }
  }, [enablePeriodicCheck])

  const checkNow = async () => {
    setLoading(true)
    const checker = BackendHealthChecker.getInstance()
    await checker.checkHealth()
    setLoading(false)
  }

  return { status, loading, checkNow }
}