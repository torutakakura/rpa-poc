/**
 * RPA Agent Client
 * Python RPAエージェントとJSON-RPC over stdioで通信
 */

import { spawn, ChildProcess } from 'child_process'
import { EventEmitter } from 'events'
import * as path from 'path'

interface JsonRpcRequest {
  jsonrpc: '2.0'
  method: string
  params?: any
  id?: string | number
}

interface JsonRpcResponse {
  jsonrpc: '2.0'
  result?: any
  error?: {
    code: number
    message: string
    data?: any
  }
  id: string | number
}

interface JsonRpcNotification {
  jsonrpc: '2.0'
  method: string
  params?: any
}

type JsonRpcMessage = JsonRpcRequest | JsonRpcResponse | JsonRpcNotification

export interface RPAClientOptions {
  pythonPath?: string
  agentPath?: string
  debug?: boolean
}

export class RPAClient extends EventEmitter {
  private process: ChildProcess | null = null
  private requestId = 0
  private pendingRequests = new Map<string | number, {
    resolve: (value: any) => void
    reject: (error: any) => void
  }>()
  private buffer = ''
  private options: RPAClientOptions

  constructor(options: RPAClientOptions = {}) {
    super()
    this.options = {
      pythonPath: options.pythonPath || 'python3',
      agentPath: options.agentPath || path.join(__dirname, '../../rpa-agent/rpa_agent.py'),
      debug: options.debug || false
    }
  }

  /**
   * エージェントを起動
   */
  async start(): Promise<void> {
    if (this.process) {
      throw new Error('Agent already started')
    }

    return new Promise((resolve, reject) => {
      const args = [this.options.agentPath!]
      if (this.options.debug) {
        args.push('--debug')
      }

      this.process = spawn(this.options.pythonPath!, args, {
        stdio: ['pipe', 'pipe', 'pipe']
      })

      this.process.stdout?.on('data', (data) => {
        this.handleData(data.toString())
      })

      this.process.stderr?.on('data', (data) => {
        console.error('Agent stderr:', data.toString())
      })

      this.process.on('error', (error) => {
        this.emit('error', error)
        reject(error)
      })

      this.process.on('exit', (code, signal) => {
        this.emit('exit', { code, signal })
        this.cleanup()
      })

      // agent_ready 通知を待つ
      const readyHandler = () => {
        this.off('agent_ready', readyHandler)
        resolve()
      }
      this.once('agent_ready', readyHandler)

      // タイムアウト設定
      setTimeout(() => {
        this.off('agent_ready', readyHandler)
        reject(new Error('Agent startup timeout'))
      }, 5000)
    })
  }

  /**
   * エージェントを停止
   */
  async stop(): Promise<void> {
    if (!this.process) {
      return
    }

    return new Promise((resolve) => {
      const exitHandler = () => {
        resolve()
      }
      this.once('exit', exitHandler)

      this.process!.kill('SIGTERM')

      // 強制終了タイムアウト
      setTimeout(() => {
        this.off('exit', exitHandler)
        if (this.process) {
          this.process.kill('SIGKILL')
        }
        resolve()
      }, 3000)
    })
  }

  /**
   * RPCメソッドを呼び出す
   */
  async call(method: string, params?: any): Promise<any> {
    if (!this.process) {
      throw new Error('Agent not started')
    }

    const id = ++this.requestId
    const request: JsonRpcRequest = {
      jsonrpc: '2.0',
      method,
      params,
      id
    }

    return new Promise((resolve, reject) => {
      this.pendingRequests.set(id, { resolve, reject })

      const json = JSON.stringify(request)
      this.process!.stdin?.write(json + '\n')

      // タイムアウト設定
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id)
          reject(new Error(`Request timeout: ${method}`))
        }
      }, 30000)
    })
  }

  /**
   * 通知を送信（レスポンスを期待しない）
   */
  notify(method: string, params?: any): void {
    if (!this.process) {
      throw new Error('Agent not started')
    }

    const notification: JsonRpcNotification = {
      jsonrpc: '2.0',
      method,
      params
    }

    const json = JSON.stringify(notification)
    this.process!.stdin?.write(json + '\n')
  }

  /**
   * 標準出力からのデータを処理
   */
  private handleData(data: string): void {
    this.buffer += data
    const lines = this.buffer.split('\n')
    
    // 最後の不完全な行を保持
    this.buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.trim()) {
        try {
          const message = JSON.parse(line) as JsonRpcMessage
          this.handleMessage(message)
        } catch (error) {
          console.error('Failed to parse JSON-RPC message:', line, error)
        }
      }
    }
  }

  /**
   * JSON-RPCメッセージを処理
   */
  private handleMessage(message: JsonRpcMessage): void {
    // レスポンス
    if ('id' in message && ('result' in message || 'error' in message)) {
      const response = message as JsonRpcResponse
      const pending = this.pendingRequests.get(response.id)
      if (pending) {
        this.pendingRequests.delete(response.id)
        if (response.error) {
          pending.reject(new Error(response.error.message))
        } else {
          pending.resolve(response.result)
        }
      }
    }
    // 通知
    else if ('method' in message && !('id' in message)) {
      const notification = message as JsonRpcNotification
      this.emit(notification.method, notification.params)
    }
  }

  /**
   * クリーンアップ
   */
  private cleanup(): void {
    this.process = null
    this.buffer = ''
    
    // 未処理のリクエストをエラーで終了
    for (const [, pending] of this.pendingRequests) {
      pending.reject(new Error('Agent disconnected'))
    }
    this.pendingRequests.clear()
  }

  /**
   * 便利メソッド：ping
   */
  async ping(): Promise<any> {
    return this.call('ping')
  }

  /**
   * 便利メソッド：機能取得
   */
  async getCapabilities(): Promise<any> {
    return this.call('get_capabilities')
  }

  /**
   * 便利メソッド：タスク実行
   */
  async runTask(name: string, params?: any): Promise<string> {
    const result = await this.call('run_task', { name, params })
    return result.task_id
  }

  /**
   * 便利メソッド：タスクキャンセル
   */
  async cancelTask(taskId: string): Promise<any> {
    return this.call('cancel_task', { task_id: taskId })
  }
}
