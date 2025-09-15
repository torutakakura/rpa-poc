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

export interface TaskProgress {
  taskId: string
  progress: number
  message: string
}

export function useRPA() {
  const [status, setStatus] = useState<RPAStatus>({
    connected: false,
    connecting: false,
    error: null,
    capabilities: null
  })

  const [tasks, setTasks] = useState<Map<string, TaskProgress>>(new Map())
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

    setStatus((prev) => ({ ...prev, connecting: true, error: null }))

    try {
      const result = await ipcRenderer.invoke('rpa:start')
      if (result.success) {
        // 機能を取得
        const capabilities = await ipcRenderer.invoke('rpa:getCapabilities')
        setStatus({
          connected: true,
          connecting: false,
          error: null,
          capabilities
        })
        return true
      } else {
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
  }, [ipcRenderer])

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
        setTasks(new Map())
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

  // タスク実行
  const runTask = useCallback(
    async (name: string, params?: any): Promise<string> => {
      if (!ipcRenderer) throw new Error('Not connected')
      const taskId = await ipcRenderer.invoke('rpa:runTask', name, params)
      
      // タスクを追跡
      setTasks((prev) => {
        const next = new Map(prev)
        next.set(taskId, { taskId, progress: 0, message: 'Starting...' })
        return next
      })
      
      return taskId
    },
    [ipcRenderer]
  )

  // タスクキャンセル
  const cancelTask = useCallback(
    async (taskId: string) => {
      if (!ipcRenderer) throw new Error('Not connected')
      return await ipcRenderer.invoke('rpa:cancelTask', taskId)
    },
    [ipcRenderer]
  )


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


  // イベントリスナーを設定
  useEffect(() => {
    if (!ipcRenderer) return

    const handleLog = (_event: any, params: any) => {
      setLogs((prev) => [...prev.slice(-99), params]) // 最新100件を保持
    }

    const handleTaskStarted = (_event: any, params: any) => {
      setTasks((prev) => {
        const next = new Map(prev)
        next.set(params.task_id, {
          taskId: params.task_id,
          progress: 0,
          message: `Task ${params.name} started`
        })
        return next
      })
    }

    const handleTaskProgress = (_event: any, params: any) => {
      setTasks((prev) => {
        const next = new Map(prev)
        const task = next.get(params.task_id)
        if (task) {
          task.progress = params.progress
          task.message = params.message
        }
        return next
      })
    }

    const handleTaskCompleted = (_event: any, params: any) => {
      setTasks((prev) => {
        const next = new Map(prev)
        next.delete(params.task_id)
        return next
      })
    }

    const handleTaskFailed = (_event: any, params: any) => {
      setTasks((prev) => {
        const next = new Map(prev)
        next.delete(params.task_id)
        return next
      })
      console.error('Task failed:', params)
    }

    const handleError = (_event: any, params: any) => {
      console.error('RPA error:', params)
      setStatus((prev) => ({ ...prev, error: params.error }))
    }

    ipcRenderer.on('rpa:log', handleLog)
    ipcRenderer.on('rpa:task_started', handleTaskStarted)
    ipcRenderer.on('rpa:task_progress', handleTaskProgress)
    ipcRenderer.on('rpa:task_completed', handleTaskCompleted)
    ipcRenderer.on('rpa:task_failed', handleTaskFailed)
    ipcRenderer.on('rpa:error', handleError)

    return () => {
      ipcRenderer.removeListener('rpa:log', handleLog)
      ipcRenderer.removeListener('rpa:task_started', handleTaskStarted)
      ipcRenderer.removeListener('rpa:task_progress', handleTaskProgress)
      ipcRenderer.removeListener('rpa:task_completed', handleTaskCompleted)
      ipcRenderer.removeListener('rpa:task_failed', handleTaskFailed)
      ipcRenderer.removeListener('rpa:error', handleError)
    }
  }, [ipcRenderer])

  return {
    // 状態
    status,
    tasks: Array.from(tasks.values()),
    logs,

    // メソッド
    connect,
    disconnect,
    ping,
    runTask,
    cancelTask,
    call,
    executeOperation
  }
}
