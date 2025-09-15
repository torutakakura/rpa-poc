/**
 * RPA Demo Component
 * JSON-RPC over stdioでPythonと通信するデモ
 */

import { useState } from 'react'
import { useRPA } from '@/hooks/use-rpa'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Play,
  Wifi,
  WifiOff,
  Folder,
  FolderEdit,
  Monitor,
  Settings,
  Loader2,
  AlertCircle,
  ChevronRight
} from 'lucide-react'

interface OperationStep {
  id: string
  category: string
  operation: string
  description: string
  params: any
  icon: React.ReactNode
}

export function RPADemo() {
  const rpa = useRPA()
  const [isExecuting, setIsExecuting] = useState(false)
  const [editingStep, setEditingStep] = useState<OperationStep | null>(null)

  // フォルダ移動シナリオのステップ定義
  const [steps, setSteps] = useState<OperationStep[]>([
    {
      id: 'step1',
      category: 'E_記憶',
      operation: '環境情報',
      description: 'コンピューター名を取得して記憶',
      params: {
        storage_key: 'computer_name',
        info_type: 'computer_name'
      },
      icon: <Monitor className="h-5 w-5" />
    },
    {
      id: 'step2',
      category: 'I_ファイル・フォルダ',
      operation: 'ファイル・フォルダ名の変更',
      description: 'フォルダを新しい場所に移動（名前変更）',
      params: {
        target_path: '/Users/test/Documents/source_folder',
        new_name: '/Users/test/Desktop/destination_folder',
        keep_extension: false
      },
      icon: <FolderEdit className="h-5 w-5" />
    }
  ])

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

      {/* フォルダ移動シナリオ */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Folder className="h-5 w-5" />
            フォルダ移動シナリオ
          </CardTitle>
          <CardDescription>
            環境情報の取得とファイル操作を組み合わせたフォルダ移動の実行
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* 操作ステップのカード表示 */}
            <div className="space-y-3">
              {steps.map((step, index) => (
                <div
                  key={step.id}
                  className="group relative flex items-center gap-3 p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => setEditingStep(step)}
                >
                  {/* ステップ番号 */}
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-medium">
                    {index + 1}
                  </div>

                  {/* アイコン */}
                  <div className="flex-shrink-0 text-gray-600">
                    {step.icon}
                  </div>

                  {/* ステップ情報 */}
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {step.category} → {step.operation}
                    </p>
                    <p className="text-sm text-gray-600">{step.description}</p>
                    {/* パラメータプレビュー */}
                    <div className="mt-1 text-xs text-gray-500">
                      {Object.entries(step.params).slice(0, 2).map(([key, value]) => (
                        <span key={key} className="mr-3">
                          {key}: <span className="font-mono">{String(value)}</span>
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* 設定ボタン */}
                  <div className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Settings className="h-4 w-4 text-gray-400" />
                  </div>

                  {/* ステップ間の矢印 */}
                  {index < steps.length - 1 && (
                    <div className="absolute -bottom-3 left-1/2 transform -translate-x-1/2 z-10">
                      <ChevronRight className="h-5 w-5 text-gray-400 rotate-90" />
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* 実行ボタン */}
            <div className="pt-4 border-t">
              <Button
                onClick={async () => {
                  setIsExecuting(true)
                  try {
                    // 各ステップを順番に実行
                    for (const step of steps) {
                      await rpa.executeOperation({
                        category: step.category,
                        operation: step.operation,
                        params: step.params
                      })
                    }
                    alert('フォルダ移動シナリオが正常に完了しました')
                  } catch (error) {
                    console.error('Scenario execution error:', error)
                    alert(`シナリオ実行に失敗しました: ${error}`)
                  } finally {
                    setIsExecuting(false)
                  }
                }}
                disabled={!rpa.status.connected || isExecuting}
                className="w-full"
              >
                {isExecuting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    実行中...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    シナリオを実行
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* パラメータ編集ダイアログ */}
      <Dialog open={!!editingStep} onOpenChange={() => setEditingStep(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>パラメータ編集</DialogTitle>
            <DialogDescription>
              {editingStep?.category} → {editingStep?.operation}
            </DialogDescription>
          </DialogHeader>

          {editingStep && (
            <div className="space-y-4">
              {/* 環境情報の場合 */}
              {editingStep.operation === '環境情報' && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="storage_key">記憶キー</Label>
                    <Input
                      id="storage_key"
                      value={editingStep.params.storage_key}
                      onChange={(e) => {
                        const updatedStep = {
                          ...editingStep,
                          params: { ...editingStep.params, storage_key: e.target.value }
                        }
                        setEditingStep(updatedStep)
                      }}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="info_type">情報タイプ</Label>
                    <Select
                      value={editingStep.params.info_type}
                      onValueChange={(value) => {
                        const updatedStep = {
                          ...editingStep,
                          params: { ...editingStep.params, info_type: value }
                        }
                        setEditingStep(updatedStep)
                      }}
                    >
                      <SelectTrigger id="info_type">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="computer_name">コンピューター名</SelectItem>
                        <SelectItem value="user_name">ユーザー名</SelectItem>
                        <SelectItem value="os_version">OSバージョン</SelectItem>
                        <SelectItem value="ip_address">IPアドレス</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </>
              )}

              {/* ファイル・フォルダ名の変更の場合 */}
              {editingStep.operation === 'ファイル・フォルダ名の変更' && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="target_path">対象パス</Label>
                    <Input
                      id="target_path"
                      value={editingStep.params.target_path}
                      onChange={(e) => {
                        const updatedStep = {
                          ...editingStep,
                          params: { ...editingStep.params, target_path: e.target.value }
                        }
                        setEditingStep(updatedStep)
                      }}
                      placeholder="/path/to/source"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="new_name">新しい名前（または移動先パス）</Label>
                    <Input
                      id="new_name"
                      value={editingStep.params.new_name}
                      onChange={(e) => {
                        const updatedStep = {
                          ...editingStep,
                          params: { ...editingStep.params, new_name: e.target.value }
                        }
                        setEditingStep(updatedStep)
                      }}
                      placeholder="/path/to/destination"
                    />
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="keep_extension"
                      checked={editingStep.params.keep_extension}
                      onCheckedChange={(checked: boolean | "indeterminate") => {
                        const updatedStep = {
                          ...editingStep,
                          params: { ...editingStep.params, keep_extension: checked === true }
                        }
                        setEditingStep(updatedStep)
                      }}
                    />
                    <Label htmlFor="keep_extension" className="text-sm">
                      拡張子を保持する
                    </Label>
                  </div>
                </>
              )}
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setEditingStep(null)}>
              キャンセル
            </Button>
            <Button onClick={() => {
              if (editingStep) {
                // ステップを更新
                setSteps(steps.map(s => s.id === editingStep.id ? editingStep : s))
                setEditingStep(null)
              }
            }}>
              保存
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

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
