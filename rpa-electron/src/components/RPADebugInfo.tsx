/**
 * RPA Debug Info Component
 * 配布版でのデバッグ情報を表示
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ScrollArea } from '@/components/ui/scroll-area'
import { AlertCircle, CheckCircle, XCircle, Loader2 } from 'lucide-react'

interface DebugInfo {
  status: 'checking' | 'success' | 'error'
  message: string
  details?: any
}

export function RPADebugInfo() {
  const [debugInfo, setDebugInfo] = useState<DebugInfo[]>([])
  const [isChecking, setIsChecking] = useState(false)

  const runDebugChecks = async () => {
    setIsChecking(true)
    const checks: DebugInfo[] = []

    // 1. IPC通信の確認
    try {
      if (window.electron?.ipcRenderer) {
        checks.push({
          status: 'success',
          message: 'IPC通信: 利用可能'
        })
      } else {
        checks.push({
          status: 'error',
          message: 'IPC通信: 利用不可（Electronコンテキストではありません）'
        })
      }
    } catch (e) {
      checks.push({
        status: 'error',
        message: 'IPC通信: エラー',
        details: String(e)
      })
    }

    // 2. 接続状態の確認
    if (window.electron?.ipcRenderer) {
      try {
        const status = await window.electron.ipcRenderer.invoke('rpa:status')
        checks.push({
          status: status.connected ? 'success' : 'error',
          message: `RPA接続: ${status.connected ? '接続済み' : '未接続'}`,
          details: status
        })
      } catch (e) {
        checks.push({
          status: 'error',
          message: 'RPA接続状態の取得に失敗',
          details: String(e)
        })
      }

      // 3. 接続試行
      try {
        const startResult = await window.electron.ipcRenderer.invoke('rpa:start')
        checks.push({
          status: startResult.success ? 'success' : 'error',
          message: `RPA起動: ${startResult.success ? '成功' : '失敗'}`,
          details: startResult
        })

        // 4. Ping確認（接続成功時のみ）
        if (startResult.success) {
          try {
            const pingResult = await window.electron.ipcRenderer.invoke('rpa:ping')
            checks.push({
              status: 'success',
              message: 'Ping: 成功',
              details: pingResult
            })
          } catch (e) {
            checks.push({
              status: 'error',
              message: 'Ping: 失敗',
              details: String(e)
            })
          }
        }
      } catch (e) {
        checks.push({
          status: 'error',
          message: 'RPA起動に失敗',
          details: String(e)
        })
      }
    }

    setDebugInfo(checks)
    setIsChecking(false)
  }

  // コンポーネントマウント時に自動実行
  useEffect(() => {
    runDebugChecks()
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />
      default:
        return <AlertCircle className="h-4 w-4 text-yellow-500" />
    }
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>デバッグ情報</span>
          <Button
            size="sm"
            onClick={runDebugChecks}
            disabled={isChecking}
          >
            {isChecking ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                チェック中...
              </>
            ) : (
              '再チェック'
            )}
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {debugInfo.map((info, index) => (
            <Alert key={index} className={
              info.status === 'error' ? 'border-red-200' :
              info.status === 'success' ? 'border-green-200' :
              'border-yellow-200'
            }>
              <AlertDescription>
                <div className="flex items-start gap-2">
                  {getStatusIcon(info.status)}
                  <div className="flex-1">
                    <p className="font-medium">{info.message}</p>
                    {info.details && (
                      <ScrollArea className="mt-2 h-24 w-full rounded border p-2">
                        <pre className="text-xs">
                          {typeof info.details === 'string' 
                            ? info.details 
                            : JSON.stringify(info.details, null, 2)}
                        </pre>
                      </ScrollArea>
                    )}
                  </div>
                </div>
              </AlertDescription>
            </Alert>
          ))}
        </div>

        {debugInfo.length === 0 && !isChecking && (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              デバッグチェックを開始してください
            </AlertDescription>
          </Alert>
        )}

        <div className="mt-4 text-xs text-gray-500">
          <p>トラブルシューティング:</p>
          <ul className="ml-4 mt-1 list-disc">
            <li>配布版の場合、アプリケーションを再起動してみてください</li>
            <li>macOSの場合、システム環境設定でアプリケーションの実行を許可してください</li>
            <li>開発者ツール（F12）のコンソールで詳細なエラーを確認してください</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  )
}
