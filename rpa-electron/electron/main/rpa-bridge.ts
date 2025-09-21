/**
 * RPA Bridge for Electron Main Process
 * RPAクライアントをIPC経由でRenderer側に公開
 */

import { ipcMain, IpcMainInvokeEvent } from 'electron'
import { RPAClient } from './rpa-client'
import * as path from 'path'

let rpaClient: RPAClient | null = null

/**
 * RPAブリッジを初期化
 */
export function initRPABridge(): void {
  // 接続状態を確認
  ipcMain.handle('rpa:status', async () => {
    // rpaClientの存在だけでなく、実際の動作状態も確認
    if (!rpaClient) {
      return {
        connected: false,
        ready: false
      }
    }
    
    // 実際にpingして動作確認
    try {
      await rpaClient.ping()
      return {
        connected: true,
        ready: true
      }
    } catch (e) {
      console.log('RPA client exists but not responding:', e)
      // クライアントは存在するが応答しない場合は、クリーンアップ
      rpaClient = null
      return {
        connected: false,
        ready: false,
        error: 'Client not responding'
      }
    }
  })

  // RPAクライアントの起動
  ipcMain.handle('rpa:start', async (event: IpcMainInvokeEvent) => {
    // 既存のクライアントがある場合、実際に動作しているか確認
    if (rpaClient) {
      console.log('Checking existing RPA client...')
      try {
        // pingして動作確認
        await rpaClient.ping()
        console.log('Existing RPA client is working')
        return { success: true, message: 'Already connected and working' }
      } catch (e) {
        console.log('Existing RPA client is not responding, cleaning up...', e)
        // 応答しない場合はクリーンアップして再起動
        try {
          await rpaClient.stop()
        } catch (stopError) {
          console.log('Error stopping old client:', stopError)
        }
        rpaClient = null
      }
    }

    try {
      // 開発環境と本番環境でパスを切り替え
      const isDev = process.env.NODE_ENV === 'development'
      const agentExecutableName = process.platform === 'win32' ? 'rpa_agent.exe' : 'rpa_agent'
      const agentPath = isDev
        ? path.join(__dirname, '../../../rpa-agent/rpa_agent.py')
        : path.join(process.resourcesPath, 'rpa-agent', agentExecutableName)  // PyInstallerでビルドした場合

      console.log('=== RPA Bridge Debug Info ===')
      console.log('Environment:', isDev ? 'development' : 'production')
      console.log('Platform:', process.platform)
      console.log('Agent path:', agentPath)
      console.log('Python path:', isDev ? (process.platform === 'win32' ? 'python' : 'python3') : 'none (using executable)')
      console.log('__dirname:', __dirname)
      console.log('process.resourcesPath:', process.resourcesPath)
      
      // ファイルの存在確認
      const fs = require('fs')
      if (fs.existsSync(agentPath)) {
        const stats = fs.statSync(agentPath)
        console.log('Agent file found:', {
          size: stats.size,
          isFile: stats.isFile(),
          mode: stats.mode.toString(8)
        })
      } else {
        console.error('Agent file NOT found at:', agentPath)
        
        // デバッグのために近くのディレクトリを探索
        if (!isDev && process.resourcesPath) {
          const resourcesPath = process.resourcesPath
          console.log('Checking resources directory:', resourcesPath)
          if (fs.existsSync(resourcesPath)) {
            const items = fs.readdirSync(resourcesPath)
            console.log('Resources directory contents:', items)
            
            const agentDir = path.join(resourcesPath, 'rpa-agent')
            if (fs.existsSync(agentDir)) {
              const agentItems = fs.readdirSync(agentDir)
              console.log('rpa-agent directory contents:', agentItems)
            }
          }
        }
      }
      console.log('=============================')

      rpaClient = new RPAClient({
        pythonPath: isDev ? (process.platform === 'win32' ? 'python' : 'python3') : undefined,  // 本番環境では実行ファイル直接
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
    
    // クライアントが実際に動作しているか確認
    try {
      await rpaClient.ping()
    } catch (e) {
      console.error('RPA client not responding in getCapabilities:', e)
      // 応答しない場合はクリーンアップ
      rpaClient = null
      throw new Error('RPA client not responding. Please restart the connection.')
    }
    
    // listOperationsを呼び出して操作一覧を取得
    const operations = await rpaClient.call('listOperations')
    return {
      excel: false,  // Excel操作はoperations内で定義
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

    // 送信するパラメータをログ出力
    console.log('=== RPA Operation Request ===')
    console.log('Category:', operation.category)
    console.log('Operation:', operation.operation)
    console.log('Params:', JSON.stringify(operation.params, null, 2))
    console.log('Full request:', JSON.stringify(operation, null, 2))
    console.log('=============================')

    // executeメソッドを呼び出す
    return await rpaClient.call('execute', operation)
  })

  // ワークフロー実行（複数操作の一括実行）
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
    console.log('Steps:', JSON.stringify(params.steps, null, 2))
    console.log('=============================')

    // ワークフロー実行
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
