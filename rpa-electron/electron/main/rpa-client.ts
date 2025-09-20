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
    const defaultPython = process.platform === 'win32' ? 'python' : 'python3'

    this.options = {
      pythonPath: options.pythonPath || defaultPython,
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

      console.log('Spawning process:', this.options.pythonPath!, args)
      this.process = spawn(this.options.pythonPath!, args, {
        stdio: ['pipe', 'pipe', 'pipe'],
        shell: process.platform === 'win32',  // Windows環境ではshell経由で実行
        windowsHide: true  // Windowsでコンソールウィンドウを非表示
      } as any)

      this.process.stdout?.on('data', (data) => {
        console.log('Agent stdout:', data.toString())
        this.handleData(data.toString())
      })

      this.process.stderr?.on('data', (data) => {
        console.error('Agent stderr:', data.toString())
      })

      this.process.on('error', (error: any) => {
        console.error('Process error:', error)
        
        // Windows特有のエラー処理
        if (error.code === 'ENOENT') {
          const errorMsg = process.platform === 'win32'
            ? `Pythonが見つかりません: ${this.options.pythonPath}\n` +
              'Pythonがインストールされ、PATHに追加されているか確認してください。\n' +
              'コマンドプロンプトで "python --version" を実行して確認できます。'
            : `Python executable not found: ${this.options.pythonPath}`
          reject(new Error(errorMsg))
        } else {
          reject(error)
        }
        
        this.emit('error', error)
      })

      this.process.on('exit', (code, signal) => {
        this.emit('exit', { code, signal })
        this.cleanup()
      })

      // agent.ready 通知を待つ
      const readyHandler = () => {
        this.off('agent.ready', readyHandler)
        resolve()
      }
      this.once('agent.ready', readyHandler)

      // タイムアウト設定
      setTimeout(() => {
        this.off('agent.ready', readyHandler)
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

      // Windows環境では異なるシグナルを使用
      if (process.platform === 'win32') {
        this.process!.kill()
      } else {
        this.process!.kill('SIGTERM')
      }

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
      console.log('Sending JSON-RPC request:', json)
      // Windows環境での改行コード処理
      const lineEnding = process.platform === 'win32' ? '\r\n' : '\n'
      this.process!.stdin?.write(json + lineEnding)

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
    // Windows環境では\r\nも考慮
    const lines = this.buffer.split(/\r?\n/)
    
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

  /**
   * 便利メソッド：ワークフロー実行（複数操作の一括実行）
   */
  async executeWorkflow(steps: any[], mode: 'sequential' | 'parallel' = 'sequential'): Promise<any> {
    return this.call('executeOperations', { steps, mode })
  }

  /**
   * 便利メソッド：Excel読み込み
   */
  async excelRead(filePath: string, sheetName?: string): Promise<any> {
    return this.call('excel_read', { file_path: filePath, sheet_name: sheetName })
  }

  /**
   * 便利メソッド：Excel書き込み
   */
  async excelWrite(filePath: string, data: any[][], sheetName?: string): Promise<any> {
    return this.call('excel_write', {
      file_path: filePath,
      data,
      sheet_name: sheetName || 'Sheet1'
    })
  }
}
