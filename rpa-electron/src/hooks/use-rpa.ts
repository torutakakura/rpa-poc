/**
 * RPA Client Hook for React
 * Renderer側でRPAクライアントを使うためのフック
 */

import { useState, useEffect, useCallback } from 'react'

// ElectronのipcRenderer型定義
interface IpcRenderer {
  invoke(channel: string, ...args: any[]): Promise<any>
  on(channel: string, listener: (event: any, ...args: any[]) => void): this
  removeListener(channel: string, listener: (...args: any[]) => void): this
}

declare global {
  interface Window {
    electron?: {
      ipcRenderer: IpcRenderer
    }
  }
}

export interface RPAStatus {
  connected: boolean
  connecting: boolean
  error: string | null
  capabilities: any | null
}


export function useRPA(autoConnect = false) {
  const [status, setStatus] = useState<RPAStatus>({
    connected: false,
    connecting: false,
    error: null,
    capabilities: null
  })

  const [logs, setLogs] = useState<Array<{ level: string; message: string; timestamp: number }>>(
    []
  )

  const ipcRenderer = window.electron?.ipcRenderer

  // RPAクライアントを起動
  const connect = useCallback(async () => {
    if (!ipcRenderer) {
      setStatus((prev) => ({ ...prev, error: 'Electron IPC not available' }))
      return false
    }

    // 既に接続中または接続済みの場合は何もしない
    if (status.connecting) {
      console.log('Already connecting, skipping...')
      return false
    }

    setStatus((prev) => ({ ...prev, connecting: true, error: null }))

    try {
      const result = await ipcRenderer.invoke('rpa:start')
      if (result.success) {
        // 接続を即時に反映（能力情報は後から取得）
        setStatus({
          connected: true,
          connecting: false,
          error: null,
          capabilities: null
        })

        const delay = result.message === 'Process starting, please wait...' ? 2000 : 200
        setTimeout(async () => {
          try {
            const capabilities = await ipcRenderer.invoke('rpa:getCapabilities')
            setStatus(prev => ({
              ...prev,
              connected: true,
              connecting: false,
              capabilities
            }))
          } catch (error) {
            // 取得失敗でも接続状態は維持
            setStatus(prev => ({
              ...prev,
              connected: true,
              connecting: false,
              capabilities: null
            }))
          }
        }, delay)

        return true
      } else {
        // "Already started"エラーの場合は、既に接続されているとみなす
        if (result.error === 'Already started') {
          try {
            // 即時に接続済みを反映し、能力は後から取得
            setStatus({ connected: true, connecting: false, error: null, capabilities: null })

            setTimeout(async () => {
              try {
                const capabilities = await ipcRenderer.invoke('rpa:getCapabilities')
                setStatus(prev => ({ ...prev, capabilities }))
              } catch (error) {
                // noop
              }
            }, 200)
            return true
          } catch (innerError) {
            setStatus({
              connected: false,
              connecting: false,
              error: (innerError as Error).message,
              capabilities: null
            })
            return false
          }
        }

        setStatus({
          connected: false,
          connecting: false,
          error: result.error,
          capabilities: null
        })
        return false
      }
    } catch (error) {
      setStatus({
        connected: false,
        connecting: false,
        error: (error as Error).message,
        capabilities: null
      })
      return false
    }
  }, [ipcRenderer, status.connecting])

  // RPAクライアントを停止
  const disconnect = useCallback(async () => {
    if (!ipcRenderer) return false

    try {
      const result = await ipcRenderer.invoke('rpa:stop')
      if (result.success) {
        setStatus({
          connected: false,
          connecting: false,
          error: null,
          capabilities: null
        })
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to disconnect:', error)
      return false
    }
  }, [ipcRenderer])

  // ping
  const ping = useCallback(async () => {
    if (!ipcRenderer) throw new Error('Not connected')
    return await ipcRenderer.invoke('rpa:ping')
  }, [ipcRenderer])



  // 汎用メソッド呼び出し
  const call = useCallback(
    async (method: string, params?: any) => {
      if (!ipcRenderer) throw new Error('Not connected')
      return await ipcRenderer.invoke('rpa:call', method, params)
    },
    [ipcRenderer]
  )

  // RPA操作の実行
  const executeOperation = useCallback(
    async (operation: {
      category: string
      operation: string
      params: any
    }) => {
      if (!ipcRenderer) throw new Error('Not connected')
      return await ipcRenderer.invoke('rpa:executeOperation', operation)
    },
    [ipcRenderer]
  )

  // ワークフロー実行（複数操作の一括実行）
  const executeWorkflow = useCallback(
    async (steps: Array<{
      id: string
      category: string
      subcategory?: string
      operation: string
      params: any
      description?: string
    }>, mode: 'sequential' | 'parallel' = 'sequential') => {
      if (!ipcRenderer) throw new Error('Not connected')
      return await ipcRenderer.invoke('rpa:executeWorkflow', { steps, mode })
    },
    [ipcRenderer]
  )


  // 接続状態を確認
  const checkStatus = useCallback(async () => {
    if (!ipcRenderer) return

    try {
      // 既存の接続状態を確認
      const currentStatus = await ipcRenderer.invoke('rpa:status')
      if (currentStatus.connected) {
        // 接続されている場合、少し待ってから機能を取得
        // （エージェントが完全に起動するまで待機）
        setTimeout(async () => {
          try {
            const capabilities = await ipcRenderer.invoke('rpa:getCapabilities')
            setStatus({
              connected: true,
              connecting: false,
              error: null,
              capabilities
            })
          } catch (error) {
            // 機能取得に失敗してもエラーにはしない（接続は成功している）
            setStatus({
              connected: true,
              connecting: false,
              error: null,
              capabilities: null
            })
          }
        }, 1000)  // 1秒待機してから機能を取得
      }
    } catch (error) {
      console.error('Failed to check status:', error)
    }
  }, [ipcRenderer])

  // 初回マウント時に接続状態を確認
  useEffect(() => {
    checkStatus()
  }, [checkStatus])

  // 自動接続
  useEffect(() => {
    if (autoConnect && !status.connected && !status.connecting) {
      connect()
    }
  }, [autoConnect, status.connected, status.connecting, connect])

  // イベントリスナーを設定
  useEffect(() => {
    if (!ipcRenderer) return

    const handleLog = (_event: any, params: any) => {
      setLogs((prev) => [...prev.slice(-99), params]) // 最新100件を保持
    }


    const handleError = (_event: any, params: any) => {
      console.error('RPA error:', params)
      setStatus((prev) => ({ ...prev, error: params.error }))
    }

    ipcRenderer.on('rpa:log', handleLog)
    ipcRenderer.on('rpa:error', handleError)

    return () => {
      ipcRenderer.removeListener('rpa:log', handleLog)
      ipcRenderer.removeListener('rpa:error', handleError)
    }
  }, [ipcRenderer])

  return {
    // 状態
    status,
    logs,

    // メソッド
    connect,
    disconnect,
    ping,
    call,
    executeOperation,
    executeWorkflow
  }
}
