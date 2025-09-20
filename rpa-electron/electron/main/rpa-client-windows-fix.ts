/**
 * RPA Agent Client - Windows対応修正版
 * Python RPAエージェントとJSON-RPC over stdioで通信
 */

import { spawn, ChildProcess } from 'child_process'
import { EventEmitter } from 'events'
import * as path from 'path'
import * as fs from 'fs'

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

/**
 * Windows環境でPythonを検出
 */
function detectWindowsPython(): string | null {
  const { execSync } = require('child_process')
  
  // Windows環境で試すべきPythonコマンドのリスト
  const pythonCommands = [
    'python',      // 一般的
    'python3',     // Python3明示
    'py',          // Python Launcher
    'py -3',       // Python Launcher with version
  ]
  
  for (const cmd of pythonCommands) {
    try {
      // Windowsではcmd.exe経由で実行
      const result = execSync(`${cmd} --version`, { 
        stdio: 'pipe',
        shell: true,
        windowsHide: true 
      })
      console.log(`Found Python via '${cmd}': ${result.toString().trim()}`)
      return cmd
    } catch (e) {
      // 次のコマンドを試す
    }
  }
  
  // 環境変数PATHを直接確認
  const pathDirs = process.env.PATH?.split(';') || []
  for (const dir of pathDirs) {
    const pythonExe = path.join(dir, 'python.exe')
    if (fs.existsSync(pythonExe)) {
      console.log(`Found Python at: ${pythonExe}`)
      return pythonExe
    }
  }
  
  return null
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
    
    // Windows環境の自動検出
    let defaultPython: string | null = null
    if (process.platform === 'win32') {
      defaultPython = detectWindowsPython()
      if (!defaultPython) {
        console.warn('Python not found in PATH. Please install Python or specify pythonPath.')
        defaultPython = 'python'  // フォールバック
      }
    } else {
      defaultPython = 'python3'
    }

    this.options = {
      pythonPath: options.pythonPath || defaultPython,
      agentPath: options.agentPath || path.join(__dirname, '../../rpa-agent/rpa_agent.py'),
      debug: options.debug || false
    }
    
    // Windowsパスの正規化
    if (process.platform === 'win32' && this.options.agentPath) {
      // バックスラッシュをフォワードスラッシュに統一
      this.options.agentPath = this.options.agentPath.replace(/\\/g, '/')
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
      // Windows環境での実行方法を決定
      let command: string
      let args: string[]
      let spawnOptions: any = {
        stdio: ['pipe', 'pipe', 'pipe'],
        windowsHide: true,
      }
      
      // agentPathが.pyファイルかexeファイルか判定
      const isScript = this.options.agentPath!.endsWith('.py')
      
      if (isScript && this.options.pythonPath) {
        // Pythonスクリプトとして実行
        if (process.platform === 'win32') {
          // Windowsの場合
          if (this.options.pythonPath.includes(' ')) {
            // "py -3"のようなコマンドの場合
            spawnOptions.shell = true
            command = this.options.pythonPath
            args = [`"${this.options.agentPath}"`]  // パスをクォート
          } else {
            // 通常のpythonコマンド
            command = this.options.pythonPath
            args = [this.options.agentPath!]
          }
        } else {
          // Unix系
          command = this.options.pythonPath
          args = [this.options.agentPath!]
        }
      } else {
        // 実行ファイルとして直接実行
        command = this.options.agentPath!
        args = []
        if (process.platform === 'win32') {
          spawnOptions.shell = false  // exeは直接実行
        }
      }
      
      if (this.options.debug) {
        args.push('--debug')
      }

      console.log('Starting RPA Agent:')
      console.log('  Platform:', process.platform)
      console.log('  Command:', command)
      console.log('  Args:', args)
      console.log('  Agent path:', this.options.agentPath)
      console.log('  Shell:', spawnOptions.shell)
      
      try {
        this.process = spawn(command, args, spawnOptions)

        this.process.stdout?.on('data', (data) => {
          const output = data.toString()
          console.log('Agent stdout:', output)
          this.handleData(output)
        })

        this.process.stderr?.on('data', (data) => {
          const error = data.toString()
          console.error('Agent stderr:', error)
          
          // Windows特有のエラーメッセージをチェック
          if (error.includes('python') && error.includes('not recognized')) {
            this.emit('error', new Error(
              'Pythonが見つかりません。\n' +
              'Pythonをインストールして、環境変数PATHに追加してください。\n' +
              'または、Python Launcherを使用してください: https://www.python.org/downloads/'
            ))
          }
        })

        this.process.on('error', (error: any) => {
          console.error('Process error:', error)
          
          // Windows特有のエラー処理
          if (error.code === 'ENOENT') {
            if (process.platform === 'win32') {
              reject(new Error(
                `実行ファイルが見つかりません: ${command}\n\n` +
                '解決方法:\n' +
                '1. Pythonがインストールされているか確認\n' +
                '2. コマンドプロンプトで "python --version" が動作するか確認\n' +
                '3. Python LauncherがインストールされていればI "py -3" を試す'
              ))
            } else {
              reject(new Error(`Python executable not found: ${command}`))
            }
          } else {
            reject(error)
          }
          
          this.emit('error', error)
        })

        this.process.on('exit', (code, signal) => {
          console.log('Process exited with code:', code, 'signal:', signal)
          this.emit('exit', { code, signal })
          this.cleanup()
        })

        // agent.ready 通知を待つ
        const readyHandler = () => {
          this.off('agent.ready', readyHandler)
          console.log('Agent is ready!')
          resolve()
        }
        this.once('agent.ready', readyHandler)

        // Windows環境では少し長めのタイムアウト
        const timeout = process.platform === 'win32' ? 10000 : 5000
        setTimeout(() => {
          this.off('agent.ready', readyHandler)
          reject(new Error(
            'Agent startup timeout.\n' +
            'デベロッパーツール（F12）のコンソールでエラーを確認してください。'
          ))
        }, timeout)
      } catch (error) {
        console.error('Failed to spawn process:', error)
        reject(error)
      }
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

      // Windowsでは異なる終了方法を使用
      if (process.platform === 'win32') {
        // Windowsではkillを使用
        this.process!.kill()
      } else {
        // Unix系ではSIGTERMを使用
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

  // 便利メソッドは元のまま...
  async ping(): Promise<any> {
    return this.call('ping')
  }

  async getCapabilities(): Promise<any> {
    return this.call('get_capabilities')
  }

  async executeWorkflow(steps: any[], mode: 'sequential' | 'parallel' = 'sequential'): Promise<any> {
    return this.call('executeOperations', { steps, mode })
  }
}
