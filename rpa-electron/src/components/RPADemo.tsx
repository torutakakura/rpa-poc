/**
 * RPA Demo Component
 * JSON-RPC over stdioでPythonと通信するデモ
 */

import { useState } from 'react'
import { useRPA } from '@/hooks/use-rpa'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  Play, 
  Square, 
  Wifi, 
  WifiOff, 
  FileSpreadsheet,
  Loader2,
  AlertCircle
} from 'lucide-react'

export function RPADemo() {
  const rpa = useRPA()
  const [excelPath, setExcelPath] = useState('/tmp/test.xlsx')
  const [taskName, setTaskName] = useState('sample_task')

  return (
    <div className="space-y-6">
      {/* 接続状態 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {rpa.status.connected ? (
              <Wifi className="h-5 w-5 text-green-500" />
            ) : (
              <WifiOff className="h-5 w-5 text-gray-400" />
            )}
            RPA Agent Connection
          </CardTitle>
          <CardDescription>
            Python RPAエージェントとの接続状態
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* 状態表示 */}
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">状態:</span>
              <span className={`text-sm font-medium ${
                rpa.status.connected ? 'text-green-600' : 
                rpa.status.connecting ? 'text-blue-600' : 
                'text-gray-600'
              }`}>
                {rpa.status.connected ? '接続済み' : 
                 rpa.status.connecting ? '接続中...' : 
                 '未接続'}
              </span>
            </div>

            {rpa.status.error && (
              <div className="flex items-start gap-2 p-3 bg-red-50 rounded-lg">
                <AlertCircle className="h-4 w-4 text-red-500 mt-0.5" />
                <p className="text-sm text-red-700">{rpa.status.error}</p>
              </div>
            )}

            {rpa.status.capabilities && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <p className="text-xs font-medium text-gray-700 mb-2">機能:</p>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-600">Excel:</span>
                    <span className={`text-xs font-medium ${
                      rpa.status.capabilities.excel ? 'text-green-600' : 'text-gray-400'
                    }`}>
                      {rpa.status.capabilities.excel ? '利用可能' : '利用不可'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-600">Version:</span>
                    <span className="text-xs font-medium">
                      {rpa.status.capabilities.version}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* 接続ボタン */}
            <div className="flex gap-2">
              {!rpa.status.connected ? (
                <Button
                  onClick={rpa.connect}
                  disabled={rpa.status.connecting}
                  className="flex-1"
                >
                  {rpa.status.connecting ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Wifi className="h-4 w-4 mr-2" />
                  )}
                  接続
                </Button>
              ) : (
                <>
                  <Button
                    variant="outline"
                    onClick={async () => {
                      try {
                        const result = await rpa.ping()
                        console.log('Ping result:', result)
                        alert('Ping successful!')
                      } catch (error) {
                        alert(`Ping failed: ${error}`)
                      }
                    }}
                    className="flex-1"
                  >
                    Ping
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={rpa.disconnect}
                    className="flex-1"
                  >
                    <WifiOff className="h-4 w-4 mr-2" />
                    切断
                  </Button>
                </>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* タスク実行 */}
      <Card>
        <CardHeader>
          <CardTitle>Task Execution</CardTitle>
          <CardDescription>
            非同期タスクの実行デモ
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex gap-2">
              <Input
                placeholder="Task name"
                value={taskName}
                onChange={(e) => setTaskName(e.target.value)}
                className="flex-1"
              />
              <Button
                onClick={async () => {
                  try {
                    const taskId = await rpa.runTask(taskName, {
                      test: 'data',
                      timestamp: Date.now()
                    })
                    console.log('Task started:', taskId)
                  } catch (error) {
                    alert(`Failed to start task: ${error}`)
                  }
                }}
                disabled={!rpa.status.connected}
              >
                <Play className="h-4 w-4 mr-2" />
                実行
              </Button>
            </div>

            {/* 実行中のタスク */}
            {rpa.tasks.length > 0 && (
              <div className="space-y-2">
                <p className="text-sm font-medium">実行中のタスク:</p>
                {rpa.tasks.map((task) => (
                  <div key={task.taskId} className="p-3 bg-blue-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-blue-900">
                        {task.taskId.substring(0, 8)}...
                      </span>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => rpa.cancelTask(task.taskId)}
                      >
                        <Square className="h-3 w-3" />
                      </Button>
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-blue-700">{task.message}</span>
                        <span className="text-xs font-medium text-blue-900">
                          {task.progress}%
                        </span>
                      </div>
                      <div className="w-full bg-blue-200 rounded-full h-1.5">
                        <div
                          className="bg-blue-600 h-1.5 rounded-full transition-all"
                          style={{ width: `${task.progress}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Excel操作 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileSpreadsheet className="h-5 w-5" />
            Excel Operations
          </CardTitle>
          <CardDescription>
            Excelファイルの読み書きデモ
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Input
              placeholder="Excel file path"
              value={excelPath}
              onChange={(e) => setExcelPath(e.target.value)}
            />
            
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={async () => {
                  try {
                    // サンプルデータを書き込み
                    const data = [
                      ['Name', 'Age', 'City'],
                      ['Alice', 30, 'Tokyo'],
                      ['Bob', 25, 'Osaka'],
                      ['Charlie', 35, 'Kyoto']
                    ]
                    const result = await rpa.excelWrite(excelPath, data)
                    console.log('Excel write result:', result)
                    alert('Excel file written successfully!')
                  } catch (error) {
                    alert(`Failed to write Excel: ${error}`)
                  }
                }}
                disabled={!rpa.status.connected}
                className="flex-1"
              >
                書き込み
              </Button>
              
              <Button
                variant="outline"
                onClick={async () => {
                  try {
                    const result = await rpa.excelRead(excelPath)
                    console.log('Excel read result:', result)
                    alert(`Read ${result.rows} rows x ${result.columns} columns`)
                  } catch (error) {
                    alert(`Failed to read Excel: ${error}`)
                  }
                }}
                disabled={!rpa.status.connected}
                className="flex-1"
              >
                読み込み
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ログ */}
      <Card>
        <CardHeader>
          <CardTitle>Logs</CardTitle>
          <CardDescription>
            エージェントからのログメッセージ
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-1 max-h-60 overflow-y-auto">
            {rpa.logs.length === 0 ? (
              <p className="text-sm text-gray-500">No logs yet</p>
            ) : (
              rpa.logs.map((log, index) => (
                <div
                  key={index}
                  className={`text-xs p-2 rounded font-mono ${
                    log.level === 'error' ? 'bg-red-50 text-red-700' :
                    log.level === 'warn' ? 'bg-yellow-50 text-yellow-700' :
                    log.level === 'debug' ? 'bg-gray-50 text-gray-600' :
                    'bg-blue-50 text-blue-700'
                  }`}
                >
                  <span className="font-semibold">[{log.level.toUpperCase()}]</span>{' '}
                  {new Date(log.timestamp * 1000).toLocaleTimeString()}: {log.message}
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
