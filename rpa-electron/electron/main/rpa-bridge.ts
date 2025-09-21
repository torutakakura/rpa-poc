/**
 * RPA Bridge for Electron Main Process
 * RPAクライアントをIPC経由でRenderer側に公開
 */

import { ipcMain, IpcMainInvokeEvent } from 'electron'
import { RPAClient } from './rpa-client'
import { RPAClientWindowsFix } from './rpa-client-windows-fix'
import * as path from 'path'
import * as fs from 'fs'

let rpaClient: RPAClient | null = null

/**
 * 実行可能ファイル（または開発用スクリプト）を探す
 */
function findExecutable(): { path: string; type: 'exe' | 'script' } | null {
  const isDev = process.env.NODE_ENV === 'development'
  const isWin = process.platform === 'win32'
  const execName = isWin ? 'rpa_agent.exe' : 'rpa_agent'

  const searchPaths = [
    ...(isDev ? [
      path.join(__dirname, '../../../rpa-agent/rpa_agent.py')
    ] : []),

    path.join(process.resourcesPath, 'rpa-agent', execName),
    path.join(process.resourcesPath, '..', 'rpa-agent', execName),
    path.join(__dirname, '../../rpa-agent/dist', execName),
    path.join(__dirname, '../../temp-resources/rpa-agent', execName),

    path.join(process.cwd(), 'rpa-agent', execName),
    path.join(process.cwd(), 'resources', 'rpa-agent', execName),

    ...(isWin ? [
      path.join(process.env.APPDATA || '', 'rpa-electron', 'rpa-agent', execName),
      path.join(process.env.LOCALAPPDATA || '', 'Programs', 'rpa-electron', 'resources', 'rpa-agent', execName)
    ] : [])
  ]

  for (const p of searchPaths) {
    if (fs.existsSync(p)) {
      const isScript = p.endsWith('.py')
      return { path: p, type: isScript ? 'script' : 'exe' }
    }
  }

  return null
}

/**
 * RPAブリッジを初期化
 */
export function initRPABridge(): void {
  // 接続状態を確認
  ipcMain.handle('rpa:status', async () => {
    if (!rpaClient) {
      return { connected: false, ready: false, version: 'unified' }
    }

    if (rpaClient.hasProcess()) {
      try {
        await rpaClient.callWithTimeout('ping', undefined, 1000)
        return { connected: true, ready: true, version: 'unified' }
      } catch {
        return { connected: true, ready: false, version: 'unified' }
      }
    } else {
      rpaClient = null
      return { connected: false, ready: false, version: 'unified' }
    }
  })

  // RPAクライアントの起動
  ipcMain.handle('rpa:start', async (event: IpcMainInvokeEvent) => {
    // 既存のクライアントがある場合、プロセスの存在だけチェック（pingは避ける）
    if (rpaClient) {
      // プロセスが存在しているかだけ確認（非同期処理なし）
      if (rpaClient.hasProcess()) {
        console.log('RPA client process already exists')
        // すでに起動済みの場合は高速でpingして確認
        try {
          await rpaClient.callWithTimeout('ping', undefined, 1000)  // 1秒の短いタイムアウト
          console.log('Existing RPA client is working')
          return { success: true, message: 'Already connected and working' }
        } catch (e) {
          console.log('Existing process not responding yet, continuing...')
          // プロセスはあるが応答しない場合は、そのまま続行（再起動はしない）
          return { success: true, message: 'Process starting, please wait...' }
        }
      } else {
        console.log('No RPA client process found, cleaning up...')
        rpaClient = null
      }
    }

    try {
      const executable = findExecutable()
      if (!executable) {
        throw new Error(
          'RPA実行ファイルが見つかりません。ビルドが成功しているか、アンチウイルスでブロックされていないかを確認してください。'
        )
      }

      const isWindows = process.platform === 'win32'
      const useExecutable = executable.type === 'exe'

      console.log('=== RPA Bridge Debug Info ===')
      console.log('Environment:', process.env.NODE_ENV || 'production')
      console.log('Platform:', process.platform)
      console.log('Agent path:', executable.path)
      console.log('Agent type:', executable.type)
      console.log('__dirname:', __dirname)
      console.log('process.resourcesPath:', process.resourcesPath)
      console.log('=============================')

      if (isWindows && useExecutable) {
        // Windows + 実行ファイルは改良版クライアント
        rpaClient = new (RPAClientWindowsFix as any)({
          pythonPath: null,
          agentPath: executable.path,
          debug: process.env.NODE_ENV === 'development'
        })
      } else {
        // それ以外は標準クライアント（scriptの場合はpython経由）
        const pythonPath = executable.type === 'script'
          ? (isWindows ? 'python' : 'python3')
          : null
        rpaClient = new RPAClient({
          pythonPath: pythonPath as any,
          agentPath: executable.path,
          debug: process.env.NODE_ENV === 'development'
        })
      }

      // イベントリスナーを設定
      rpaClient!.on('log', (params) => {
        event.sender.send('rpa:log', params)
      })

      rpaClient!.on('error', (error) => {
        event.sender.send('rpa:error', { error: error.message })
      })

      await rpaClient!.start()
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
