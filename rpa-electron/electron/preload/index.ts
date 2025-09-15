/**
 * Preload Script
 * Renderer側にElectron APIを安全に公開
 */

import { contextBridge, ipcRenderer } from 'electron'

// Renderer側に公開するAPI
const electronAPI = {
  ipcRenderer: {
    // 双方向通信
    invoke: (channel: string, ...args: any[]) => {
      // 許可されたチャンネルのみ
      const validChannels = [
        'rpa:start',
        'rpa:stop',
        'rpa:ping',
        'rpa:getCapabilities',
        'rpa:runTask',
        'rpa:cancelTask',
        'rpa:executeOperation',
        'rpa:call'
      ]
      if (validChannels.includes(channel)) {
        return ipcRenderer.invoke(channel, ...args)
      }
      throw new Error(`Invalid channel: ${channel}`)
    },

    // イベントリスナー
    on: (channel: string, listener: (event: any, ...args: any[]) => void) => {
      const validChannels = [
        'rpa:log',
        'rpa:task_started',
        'rpa:task_progress',
        'rpa:task_completed',
        'rpa:task_failed',
        'rpa:error'
      ]
      if (validChannels.includes(channel)) {
        ipcRenderer.on(channel, listener)
        return ipcRenderer
      }
      throw new Error(`Invalid channel: ${channel}`)
    },

    // リスナー削除
    removeListener: (channel: string, listener: (...args: any[]) => void) => {
      ipcRenderer.removeListener(channel, listener)
      return ipcRenderer
    }
  }
}

// Renderer側のwindowオブジェクトに公開
contextBridge.exposeInMainWorld('electron', electronAPI)