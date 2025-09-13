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
  // RPAクライアントの起動
  ipcMain.handle('rpa:start', async (event: IpcMainInvokeEvent) => {
    if (rpaClient) {
      return { success: false, error: 'Already started' }
    }

    try {
      // 開発環境と本番環境でパスを切り替え
      const isDev = process.env.NODE_ENV === 'development'
      const agentPath = isDev 
        ? path.join(__dirname, '../../../rpa-agent/rpa_agent.py')
        : path.join(process.resourcesPath, 'rpa-agent', 'rpa_agent')  // PyInstallerでビルドした場合

      rpaClient = new RPAClient({
        pythonPath: isDev ? 'python3' : undefined,  // 本番環境では実行ファイル直接
        agentPath,
        debug: isDev
      })

      // イベントリスナーを設定
      rpaClient.on('log', (params) => {
        event.sender.send('rpa:log', params)
      })

      rpaClient.on('task_started', (params) => {
        event.sender.send('rpa:task_started', params)
      })

      rpaClient.on('task_progress', (params) => {
        event.sender.send('rpa:task_progress', params)
      })

      rpaClient.on('task_completed', (params) => {
        event.sender.send('rpa:task_completed', params)
      })

      rpaClient.on('task_failed', (params) => {
        event.sender.send('rpa:task_failed', params)
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

  // 機能取得
  ipcMain.handle('rpa:getCapabilities', async () => {
    if (!rpaClient) {
      throw new Error('RPA client not started')
    }
    return await rpaClient.getCapabilities()
  })

  // タスク実行
  ipcMain.handle('rpa:runTask', async (_event, name: string, params?: any) => {
    if (!rpaClient) {
      throw new Error('RPA client not started')
    }
    return await rpaClient.runTask(name, params)
  })

  // タスクキャンセル
  ipcMain.handle('rpa:cancelTask', async (_event, taskId: string) => {
    if (!rpaClient) {
      throw new Error('RPA client not started')
    }
    return await rpaClient.cancelTask(taskId)
  })

  // Excel読み込み
  ipcMain.handle('rpa:excelRead', async (_event, filePath: string, sheetName?: string) => {
    if (!rpaClient) {
      throw new Error('RPA client not started')
    }
    return await rpaClient.excelRead(filePath, sheetName)
  })

  // Excel書き込み
  ipcMain.handle('rpa:excelWrite', async (_event, filePath: string, data: any[][], sheetName?: string) => {
    if (!rpaClient) {
      throw new Error('RPA client not started')
    }
    return await rpaClient.excelWrite(filePath, data, sheetName)
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
