import { app, BrowserWindow } from 'electron'
import path from 'path'
import { initRPABridge, cleanupRPABridge } from './rpa-bridge'

let mainWindow: BrowserWindow | null = null

// 単一の統合ブリッジを使用

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, '../preload/index.js')
    }
  })

  // 開発環境と本番環境の切り替え
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../../dist/index.html'))
    // 配布版でもF12キーで開発者ツールを開けるようにする（デバッグ用）
    mainWindow.webContents.on('before-input-event', (event, input) => {
      if (input.key === 'F12') {
        mainWindow!.webContents.toggleDevTools()
        event.preventDefault()
      }
    })
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

app.whenReady().then(() => {
  // 統合ブリッジを初期化
  initRPABridge()
  createWindow()
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

app.on('before-quit', async (event) => {
  event.preventDefault()
  // 統合ブリッジをクリーンアップ
  await cleanupRPABridge()
  app.exit()
})