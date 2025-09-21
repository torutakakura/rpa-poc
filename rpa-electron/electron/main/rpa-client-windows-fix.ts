/**
 * RPA Agent Client - Windows Fix Version
 * Windows環境での問題を解決するための改良版
 */

import { spawn, ChildProcess } from 'child_process'
import { EventEmitter } from 'events'
import * as path from 'path'
import * as fs from 'fs'
import { StringDecoder } from 'string_decoder'
import { execSync } from 'child_process'

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

export class RPAClientWindowsFix extends EventEmitter {
  private process: ChildProcess | null = null
  private requestId = 0
  private pendingRequests = new Map<string | number, {
    resolve: (value: any) => void
    reject: (error: any) => void
  }>()
  private buffer = ''
  private options: RPAClientOptions
  private stdoutDecoder = new StringDecoder('utf8')
  private stderrDecoder = new StringDecoder('utf8')
  private startRetries = 0
  private maxRetries = 3

  constructor(options: RPAClientOptions = {}) {
    super()
    const defaultPython = process.platform === 'win32' ? 'python' : 'python3'

    this.options = {
      pythonPath: options.pythonPath !== undefined ? options.pythonPath : defaultPython,
      agentPath: options.agentPath || path.join(__dirname, '../../rpa-agent/rpa_agent.py'),
      debug: options.debug || false
    }
  }

  /**
   * Windows環境での実行ファイルパスの正規化
   */
  private normalizeWindowsPath(filePath: string): string {
    if (process.platform !== 'win32') return filePath

    // バックスラッシュを統一
    let normalized = filePath.replace(/\//g, '\\')
    
    // 短縮パス（8.3形式）の取得を試みる
    if (normalized.includes(' ')) {
      try {
        // cmd.exe /c "for %I in ("path") do @echo %~sI" を使用
        const shortPath = execSync(
          `cmd.exe /c "for %I in ("${normalized}") do @echo %~sI"`, 
          { encoding: 'utf8' }
        ).trim()
        
        if (shortPath && fs.existsSync(shortPath)) {
          console.log(`[Windows] 短縮パスを使用: ${shortPath}`)
          return shortPath
        }
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e)
        console.log(`[Windows] 短縮パスの取得に失敗、元のパスを使用: ${msg}`)
      }
    }

    return normalized
  }

  /**
   * プロセスの起動を試みる（リトライ機能付き）
   */
  private async startWithRetry(): Promise<void> {
    while (this.startRetries < this.maxRetries) {
      try {
        await this.startInternal()
        this.startRetries = 0 // 成功したらリセット
        return
      } catch (error) {
        this.startRetries++
        console.error(`[Windows] 起動試行 ${this.startRetries}/${this.maxRetries} 失敗:`, error)
        
        if (this.startRetries >= this.maxRetries) {
          throw error
        }

        // リトライ前に待機（指数バックオフ）
        const waitTime = Math.min(1000 * Math.pow(2, this.startRetries - 1), 5000)
        console.log(`[Windows] ${waitTime}ms 待機してからリトライ...`)
        await new Promise(resolve => setTimeout(resolve, waitTime))
      }
    }
  }

  /**
   * エージェントを起動（内部実装）
   */
  private async startInternal(): Promise<void> {
    if (this.process) {
      throw new Error('Agent already started')
    }

    return new Promise((resolve, reject) => {
      const isDirectExecutable = !this.options.pythonPath
      let command: string
      let args: string[] = []
      
      console.log('[Windows] ======= RPA Client Start Debug =======')
      console.log('[Windows] Platform:', process.platform)
      console.log('[Windows] pythonPath:', this.options.pythonPath)
      console.log('[Windows] agentPath:', this.options.agentPath)
      console.log('[Windows] isDirectExecutable:', isDirectExecutable)
      
      if (isDirectExecutable && this.options.agentPath) {
        // PyInstallerでビルドされた実行ファイルを直接実行
        command = this.normalizeWindowsPath(this.options.agentPath)
        
        // ファイルの存在確認
        if (!fs.existsSync(command)) {
          // 代替パスを試す
          const altPaths = [
            command,
            command.replace(/\.exe$/i, '') + '.exe',
            path.join(process.resourcesPath, 'rpa-agent', 'rpa_agent.exe'),
            path.join(process.resourcesPath, 'rpa-agent', 'rpa_agent'),
            path.join(__dirname, '../../temp-resources/rpa-agent/rpa_agent.exe')
          ]
          
          console.log('[Windows] ファイルを検索中...')
          for (const altPath of altPaths) {
            console.log(`[Windows] 検索: ${altPath}`)
            if (fs.existsSync(altPath)) {
              command = this.normalizeWindowsPath(altPath)
              console.log(`[Windows] 見つかりました: ${command}`)
              break
            }
          }
          
          if (!fs.existsSync(command)) {
            reject(new Error(`実行ファイルが見つかりません。試したパス:\n${altPaths.join('\n')}`))
            return
          }
        }
        
        // ファイル情報を表示
        const stats = fs.statSync(command)
        console.log('[Windows] ファイル情報:', {
          path: command,
          size: `${(stats.size / 1024 / 1024).toFixed(2)} MB`,
          isFile: stats.isFile(),
          mode: stats.mode.toString(8)
        })
        
      } else {
        // Pythonスクリプトとして実行
        command = this.options.pythonPath!
        args = [this.options.agentPath!]
        console.log('[Windows] Python実行:', command, args)
      }
      
      if (this.options.debug) {
        args.push('--debug')
      }

      // spawn オプションの設定（Windows最適化）
      const spawnOptions: any = {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: {
          ...process.env,
          PYTHONIOENCODING: 'utf-8',
          PYTHONUTF8: '1',
          PYTHONUNBUFFERED: '1'
        }
      }
      
      if (process.platform === 'win32') {
        // Windows特有の設定
        spawnOptions.windowsHide = false // デバッグのため表示
        spawnOptions.shell = false
        spawnOptions.detached = false
        spawnOptions.windowsVerbatimArguments = true // 引数をそのまま渡す
        
        // 重要な環境変数を確実に含める
        spawnOptions.env = {
          ...spawnOptions.env,
          SYSTEMROOT: process.env.SYSTEMROOT || 'C:\\Windows',
          COMSPEC: process.env.COMSPEC || 'C:\\Windows\\System32\\cmd.exe',
          PATH: process.env.PATH,
          TEMP: process.env.TEMP,
          TMP: process.env.TMP
        }
      }
      
      console.log('[Windows] spawn設定:', {
        command: command,
        args: args,
        options: {
          ...spawnOptions,
          env: '(省略)'
        }
      })
      console.log('[Windows] =======================================')
      
      try {
        this.process = spawn(command, args, spawnOptions)
        
        if (!this.process || !this.process.stdout || !this.process.stderr || !this.process.stdin) {
          reject(new Error('プロセスのストリーム作成に失敗しました'))
          return
        }
        
        console.log('[Windows] プロセス起動成功, PID:', this.process.pid)
        
        // stdout処理
        this.process.stdout.on('data', (data) => {
          const output = this.stdoutDecoder.write(data)
          console.log('[Windows Agent stdout]:', output.trim())
          this.handleData(output)
        })

        this.process.stdout.on('end', () => {
          const remaining = this.stdoutDecoder.end()
          if (remaining) {
            this.handleData(remaining)
          }
        })

        // stderr処理
        this.process.stderr.on('data', (data) => {
          const errorOutput = this.stderrDecoder.write(data)
          console.error('[Windows Agent stderr]:', errorOutput.trim())
        })

        this.process.stderr.on('end', () => {
          const remaining = this.stderrDecoder.end()
          if (remaining) {
            console.error('[Windows Agent stderr]:', remaining)
          }
        })

        // エラーハンドリング
        this.process.on('error', (error: any) => {
          console.error('[Windows] プロセスエラー:', error)
          
          if (error.code === 'ENOENT') {
            const errorMsg = isDirectExecutable
              ? `実行ファイルが見つかりません: ${command}\n` +
                'ビルド時にrpa_agent.exeが正しく生成・配置されているか確認してください。'
              : `Pythonが見つかりません: ${command}\n` +
                'Pythonがインストールされ、PATHに追加されているか確認してください。'
            reject(new Error(errorMsg))
          } else if (error.code === 'EACCES' || error.code === 5) {
            reject(new Error(`実行権限がありません: ${command}\n` +
              'Windows Defenderまたはアンチウイルスソフトがブロックしている可能性があります。'))
          } else {
            reject(error)
          }
          
          this.emit('error', error)
        })

        // プロセス終了処理
        this.process.on('exit', (code, signal) => {
          console.log(`[Windows] プロセス終了: code=${code}, signal=${signal}`)
          this.emit('exit', { code, signal })
          this.cleanup()
        })

        // agent.ready 通知を待つ
        const readyHandler = () => {
          console.log('[Windows] Agent ready受信!')
          this.off('agent.ready', readyHandler)
          resolve()
        }
        this.once('agent.ready', readyHandler)

        // Windows環境では長めのタイムアウトを設定（初回起動時の展開を考慮）
        const timeoutMs = isDirectExecutable ? 30000 : 15000
        setTimeout(() => {
          this.off('agent.ready', readyHandler)
          
          // タイムアウトしてもプロセスが生きていれば成功とみなす
          if (this.process && !this.process.killed) {
            console.log('[Windows] タイムアウトしたがプロセスは生きているため成功とみなす')
            resolve()
          } else {
            reject(new Error(`エージェント起動タイムアウト (${timeoutMs/1000}秒)`))
          }
        }, timeoutMs)
        
      } catch (spawnError) {
        console.error('[Windows] spawn失敗:', spawnError)
        reject(spawnError)
      }
    })
  }

  /**
   * エージェントを起動（公開メソッド）
   */
  async start(): Promise<void> {
    return this.startWithRetry()
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

      // Windows環境での終了処理
      if (process.platform === 'win32') {
        // 最初は通常のkillを試す
        this.process!.kill()
        
        // 3秒待っても終了しない場合はtaskkillを使用
        setTimeout(() => {
          if (this.process && !this.process.killed) {
            console.log('[Windows] taskkillを使用して強制終了を試みます...')
            try {
              execSync(`taskkill /PID ${this.process.pid} /F`, { stdio: 'ignore' })
            } catch (e) {
              console.error('[Windows] taskkill失敗:', e)
            }
          }
        }, 3000)
      } else {
        this.process!.kill('SIGTERM')
      }

      // 最終的な強制終了タイムアウト
      setTimeout(() => {
        this.off('exit', exitHandler)
        if (this.process) {
          this.process.kill('SIGKILL')
        }
        resolve()
      }, 5000)
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
      console.log('[Windows] Sending JSON-RPC:', json)
      
      // Windows環境では\r\nを使用
      const lineEnding = '\r\n'
      
      try {
        this.process!.stdin?.write(json + lineEnding, (error) => {
          if (error) {
            console.error('[Windows] stdin書き込みエラー:', error)
            this.pendingRequests.delete(id)
            reject(error)
          }
        })
      } catch (e) {
        console.error('[Windows] stdin書き込み例外:', e)
        this.pendingRequests.delete(id)
        reject(e)
      }

      // タイムアウト設定
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id)
          reject(new Error(`リクエストタイムアウト: ${method}`))
        }
      }, 30000)
    })
  }

  /**
   * 通知を送信
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
    const lineEnding = process.platform === 'win32' ? '\r\n' : '\n'
    this.process!.stdin?.write(json + lineEnding)
  }

  /**
   * データ処理
   */
  private handleData(data: string): void {
    this.buffer += data
    const lines = this.buffer.split(/\r?\n/)
    
    this.buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.trim()) {
        try {
          const message = JSON.parse(line) as JsonRpcMessage
          this.handleMessage(message)
        } catch (error) {
          console.error('[Windows] JSON解析エラー:', line, error)
        }
      }
    }
  }

  /**
   * メッセージ処理
   */
  private handleMessage(message: JsonRpcMessage): void {
    // レスポンス処理
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
    // 通知処理
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
    
    for (const [, pending] of this.pendingRequests) {
      pending.reject(new Error('Agent disconnected'))
    }
    this.pendingRequests.clear()
  }

  /**
   * プロセス存在確認
   */
  hasProcess(): boolean {
    return this.process !== null && !this.process.killed
  }

  /**
   * ping（ヘルスチェック）
   */
  async ping(): Promise<any> {
    if (!this.process) {
      throw new Error('Agent process not started')
    }
    
    if (this.process.killed) {
      throw new Error('Agent process has been killed')
    }
    
    return this.callWithTimeout('ping', undefined, 3000)
  }

  /**
   * タイムアウト付きコール
   */
  async callWithTimeout(method: string, params?: any, timeout: number = 30000): Promise<any> {
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
      const lineEnding = process.platform === 'win32' ? '\r\n' : '\n'
      this.process!.stdin?.write(json + lineEnding)

      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id)
          reject(new Error(`リクエストタイムアウト (${timeout}ms): ${method}`))
        }
      }, timeout)
    })
  }

  // 便利メソッド群
  async getCapabilities(): Promise<any> {
    return this.call('get_capabilities')
  }

  async runTask(name: string, params?: any): Promise<string> {
    const result = await this.call('run_task', { name, params })
    return result.task_id
  }

  async cancelTask(taskId: string): Promise<any> {
    return this.call('cancel_task', { task_id: taskId })
  }

  async executeWorkflow(steps: any[], mode: 'sequential' | 'parallel' = 'sequential'): Promise<any> {
    return this.call('executeOperations', { steps, mode })
  }

  async excelRead(filePath: string, sheetName?: string): Promise<any> {
    return this.call('excel_read', { file_path: filePath, sheet_name: sheetName })
  }

  async excelWrite(filePath: string, data: any[][], sheetName?: string): Promise<any> {
    return this.call('excel_write', {
      file_path: filePath,
      data,
      sheet_name: sheetName || 'Sheet1'
    })
  }
}