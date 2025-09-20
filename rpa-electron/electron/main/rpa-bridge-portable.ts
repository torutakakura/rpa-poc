/**
 * RPA Bridge for Portable Distribution
 * ポータブル配布版用のRPAブリッジ設定
 */

import { ipcMain, IpcMainInvokeEvent, app } from 'electron'
import { RPAClient } from './rpa-client'
import * as path from 'path'
import * as fs from 'fs'

let rpaClient: RPAClient | null = null

/**
 * Python実行環境を検出
 */
function detectPythonCommand(): string | undefined {
  const commands = process.platform === 'win32' 
    ? ['python', 'python3', 'py']
    : ['python3', 'python'];
  
  const { execSync } = require('child_process');
  
  for (const cmd of commands) {
    try {
      execSync(`${cmd} --version`, { stdio: 'ignore' });
      console.log(`Found Python: ${cmd}`);
      return cmd;
    } catch (e) {
      // Continue to next command
    }
  }
  
  return undefined;
}

/**
 * RPAブリッジを初期化（ポータブル版）
 */
export function initRPABridge(): void {
  // 接続状態を確認
  ipcMain.handle('rpa:status', async () => {
    return {
      connected: !!rpaClient,
      ready: !!rpaClient
    }
  })

  // RPAクライアントの起動
  ipcMain.handle('rpa:start', async (event: IpcMainInvokeEvent) => {
    if (rpaClient) {
      console.log('RPA client already started')
      return { success: true, message: 'Already started' }
    }

    try {
      const isDev = process.env.NODE_ENV === 'development'
      let agentPath: string
      let pythonPath: string | undefined
      
      if (isDev) {
        // 開発環境: ソースコードを直接実行
        agentPath = path.join(__dirname, '../../../rpa-agent/rpa_agent.py')
        pythonPath = 'python3'
        console.log('Development mode: Using source code')
      } else {
        // 本番環境: 複数の戦略を試す
        
        // 戦略1: バンドルされた実行ファイルを探す（従来の方法）
        const execName = process.platform === 'win32' ? 'rpa_agent.exe' : 'rpa_agent'
        const bundledExecPath = path.join(process.resourcesPath, 'rpa-agent', execName)
        
        // 戦略2: バンドルされたPythonスクリプトを探す（新しい方法）
        const bundledScriptPath = path.join(process.resourcesPath, 'rpa-agent', 'rpa_agent.py')
        
        // 戦略3: アプリケーションディレクトリ内のスクリプト
        const appScriptPath = path.join(app.getAppPath(), '..', 'rpa-agent', 'rpa_agent.py')
        
        console.log('Production mode: Detecting agent...')
        console.log('  Checking bundled exec:', bundledExecPath)
        console.log('  Checking bundled script:', bundledScriptPath)
        console.log('  Checking app script:', appScriptPath)
        
        if (fs.existsSync(bundledExecPath)) {
          // 実行ファイルが見つかった
          console.log('Found bundled executable')
          agentPath = bundledExecPath
          pythonPath = undefined
        } else if (fs.existsSync(bundledScriptPath)) {
          // Pythonスクリプトが見つかった
          console.log('Found bundled Python script')
          agentPath = bundledScriptPath
          pythonPath = detectPythonCommand()
          
          if (!pythonPath) {
            throw new Error('Pythonがインストールされていません。Python 3.8以上をインストールしてください。')
          }
        } else if (fs.existsSync(appScriptPath)) {
          // アプリディレクトリのスクリプトが見つかった
          console.log('Found app Python script')
          agentPath = appScriptPath
          pythonPath = detectPythonCommand()
          
          if (!pythonPath) {
            throw new Error('Pythonがインストールされていません。Python 3.8以上をインストールしてください。')
          }
        } else {
          throw new Error(
            'Python Agentが見つかりません。以下のパスを確認してください：\n' +
            `- ${bundledExecPath}\n` +
            `- ${bundledScriptPath}\n` +
            `- ${appScriptPath}`
          )
        }
      }

      console.log('Starting RPA client:')
      console.log('  Environment:', isDev ? 'development' : 'production')
      console.log('  Platform:', process.platform)
      console.log('  Agent path:', agentPath)
      console.log('  Python command:', pythonPath || 'N/A (using executable)')
      
      rpaClient = new RPAClient({
        pythonPath,
        agentPath,
        debug: isDev
      })

      // イベントリスナーを設定
      rpaClient.on('log', (params) => {
        event.sender.send('rpa:log', params)
      })

      rpaClient.on('error', (error) => {
        event.sender.send('rpa:error', { error: error.message })
      })

      await rpaClient.start()
      return { success: true }
    } catch (error) {
      rpaClient = null
      console.error('Failed to start RPA client:', error)
      return { success: false, error: (error as Error).message }
    }
  })

  // RPAクライアントの停止
  ipcMain.handle('rpa:stop', async () => {
    if (!rpaClient) {
      return { success: false, error: 'Not started' }
    }

    try {
      await rpaClient.stop()
      rpaClient = null
      return { success: true }
    } catch (error) {
      return { success: false, error: (error as Error).message }
    }
  })

  // ping
  ipcMain.handle('rpa:ping', async () => {
    if (!rpaClient) {
      throw new Error('RPA client not started')
    }
    return await rpaClient.ping()
  })

  // 操作可能一覧の取得
  ipcMain.handle('rpa:getCapabilities', async () => {
    if (!rpaClient) {
      throw new Error('RPA client not started')
    }
    const operations = await rpaClient.call('listOperations')
    return {
      excel: false,
      version: '2.0.0',
      operations: operations?.operations || {}
    }
  })

  // RPA操作の実行
  ipcMain.handle('rpa:executeOperation', async (_event, operation: {
    category: string
    subcategory?: string
    operation: string
    params: any
  }) => {
    if (!rpaClient) {
      throw new Error('RPA client not started')
    }

    console.log('=== RPA Operation Request ===')
    console.log('Category:', operation.category)
    console.log('Operation:', operation.operation)
    console.log('Params:', JSON.stringify(operation.params, null, 2))
    console.log('=============================')

    return await rpaClient.call('execute', operation)
  })

  // ワークフロー実行
  ipcMain.handle('rpa:executeWorkflow', async (_event, params: {
    steps: Array<{
      id: string
      category: string
      subcategory?: string
      operation: string
      params: any
      description?: string
    }>
    mode?: 'sequential' | 'parallel'
  }) => {
    if (!rpaClient) {
      throw new Error('RPA client not started')
    }

    console.log('=== RPA Workflow Request ===')
    console.log('Mode:', params.mode || 'sequential')
    console.log('Steps count:', params.steps.length)
    console.log('=============================')

    return await rpaClient.executeWorkflow(params.steps, params.mode || 'sequential')
  })

  // 汎用メソッド呼び出し
  ipcMain.handle('rpa:call', async (_event, method: string, params?: any) => {
    if (!rpaClient) {
      throw new Error('RPA client not started')
    }
    return await rpaClient.call(method, params)
  })
}

/**
 * クリーンアップ（アプリケーション終了時）
 */
export async function cleanupRPABridge(): Promise<void> {
  if (rpaClient) {
    await rpaClient.stop()
    rpaClient = null
  }
}
