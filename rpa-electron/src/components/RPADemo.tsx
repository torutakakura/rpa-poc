/**
 * RPA Demo Component
 * JSON-RPC over stdioでPythonと通信するデモ
 */

import { useState, useCallback, useRef, useEffect } from 'react'
import { useRPA } from '@/hooks/use-rpa'
import { WorkflowStep } from '@/components/WorkflowBuilder'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Separator } from '@/components/ui/separator'
import {
  Wifi,
  WifiOff,
  Loader2,
  AlertCircle,
  CheckCircle,
  Play,
  StopCircle,
  Plus,
  ChevronUp,
  ChevronDown,
  Copy,
  Trash2,
  Edit2,
  Save,
  Search,
  AppWindow,
  Clock,
  Mouse,
  Keyboard,
  HardDrive,
  Type,
  GitBranch,
  Mail,
  Folder,
  FileSpreadsheet,
  FileText,
  Globe,
  Upload,
  Download,
} from 'lucide-react'

// カテゴリアイコンのマッピング
const categoryIcons: Record<string, React.ReactNode> = {
  'A_アプリ・画面': <AppWindow className="h-4 w-4" />,
  'B_待機・終了・エラー': <Clock className="h-4 w-4" />,
  'C_マウス': <Mouse className="h-4 w-4" />,
  'D_キーボード': <Keyboard className="h-4 w-4" />,
  'E_記憶': <HardDrive className="h-4 w-4" />,
  'F_文字抽出': <Type className="h-4 w-4" />,
  'G_分岐': <GitBranch className="h-4 w-4" />,
  'H_メール': <Mail className="h-4 w-4" />,
  'I_ファイル・フォルダ': <Folder className="h-4 w-4" />,
  'J_Excel': <FileSpreadsheet className="h-4 w-4" />,
  'K_CSV': <FileText className="h-4 w-4" />,
  'L_ウェブブラウザ': <Globe className="h-4 w-4" />,
}


export function RPADemo() {
  // 自動接続を有効にしてRPAフックを使用
  const rpa = useRPA(true)

  // 操作テンプレートの状態
  const [operationTemplates, setOperationTemplates] = useState<any>(null)

  // ワークフロー関連の状態
  const [workflowSteps, setWorkflowSteps] = useState<WorkflowStep[]>([])
  const [isExecutingWorkflow, setIsExecutingWorkflow] = useState(false)
  const [currentStepIndex, setCurrentStepIndex] = useState(-1)
  const [workflowProgress, setWorkflowProgress] = useState(0)
  const abortControllerRef = useRef<boolean>(false)
  const [executionMode, setExecutionMode] = useState<'sequential' | 'batch'>('batch')

  // 操作検索とフィルタ
  const [searchTerm, setSearchTerm] = useState('')

  // ステップ編集
  const [editingStep, setEditingStep] = useState<WorkflowStep | null>(null)
  const [isAddingStep, setIsAddingStep] = useState(false)
  const [stepParams, setStepParams] = useState<Record<string, any>>({})
  const [stepDescription, setStepDescription] = useState('')

  // 操作一覧を取得
  const operations = rpa.status.capabilities?.operations || {}

  // 操作テンプレートを取得
  useEffect(() => {
    const fetchTemplates = async () => {
      if (rpa.status.connected && rpa.call) {
        try {
          const templates = await rpa.call('getOperationTemplates')
          setOperationTemplates(templates)
        } catch (error) {
          console.error('Failed to fetch operation templates:', error)
        }
      }
    }
    fetchTemplates()
  }, [rpa.status.connected, rpa.call])

  // 操作を検索フィルタリング（ネスト構造対応）
  const filteredOperations = Object.entries(operations).reduce((acc, [category, ops]) => {
    if (!ops || !Array.isArray(ops) || ops.length === 0) return acc

    const filtered = ops.filter((op: string) => {
      const opName = op.includes('/') ? op : op
      return opName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        category.toLowerCase().includes(searchTerm.toLowerCase())
    })

    if (filtered.length > 0) {
      acc[category] = filtered
    }

    return acc
  }, {} as Record<string, string[]>)

  // パラメータテンプレートを取得するヘルパー関数
  const getOperationTemplate = (category: string, operation: string) => {
    if (!operationTemplates?.operation_templates) return {}

    const categoryTemplates = operationTemplates.operation_templates[category]
    if (!categoryTemplates) return {}

    // ネストされた操作の場合
    if (operation.includes('/')) {
      const [parent, child] = operation.split('/')
      if (categoryTemplates[parent] && categoryTemplates[parent][child]) {
        return categoryTemplates[parent][child].specific_params || {}
      }
    }

    // 直接の操作の場合
    if (categoryTemplates[operation]) {
      return categoryTemplates[operation].specific_params || {}
    }

    return {}
  }

  // ステップを追加（操作から）
  const handleAddOperation = (category: string, operation: string) => {
    const template = getOperationTemplate(category, operation)
    const newStep: WorkflowStep = {
      id: `step-${Date.now()}`,
      category,
      operation,
      params: template,
      description: `${category.substring(2)} → ${operation}`,
      status: 'pending',
    }
    setWorkflowSteps([...workflowSteps, newStep])
  }

  // ステップを編集
  const handleEditStep = (step: WorkflowStep) => {
    setEditingStep(step)
    setStepParams(step.params)
    setStepDescription(step.description || '')
    setIsAddingStep(true)
  }

  // ステップを更新
  const handleUpdateStep = () => {
    if (!editingStep) return

    const updatedSteps = workflowSteps.map((step) =>
      step.id === editingStep.id
        ? {
            ...editingStep,
            params: { ...stepParams },
            description: stepDescription,
          }
        : step
    )

    setWorkflowSteps(updatedSteps)
    setEditingStep(null)
    resetForm()
  }

  // ステップを削除
  const handleDeleteStep = (id: string) => {
    setWorkflowSteps(workflowSteps.filter((step) => step.id !== id))
  }

  // ステップを複製
  const handleDuplicateStep = (step: WorkflowStep) => {
    const newStep: WorkflowStep = {
      ...step,
      id: `step-${Date.now()}`,
      status: 'pending',
    }
    const index = workflowSteps.findIndex((s) => s.id === step.id)
    const newSteps = [...workflowSteps]
    newSteps.splice(index + 1, 0, newStep)
    setWorkflowSteps(newSteps)
  }

  // ステップを上に移動
  const handleMoveUp = (index: number) => {
    if (index === 0) return
    const newSteps = [...workflowSteps]
    ;[newSteps[index - 1], newSteps[index]] = [newSteps[index], newSteps[index - 1]]
    setWorkflowSteps(newSteps)
  }

  // ステップを下に移動
  const handleMoveDown = (index: number) => {
    if (index === workflowSteps.length - 1) return
    const newSteps = [...workflowSteps]
    ;[newSteps[index], newSteps[index + 1]] = [newSteps[index + 1], newSteps[index]]
    setWorkflowSteps(newSteps)
  }

  // フォームをリセット
  const resetForm = () => {
    setIsAddingStep(false)
    setStepParams({})
    setStepDescription('')
  }

  // ワークフローを実行
  const handleExecuteWorkflow = useCallback(async () => {
    if (!rpa.status.connected || workflowSteps.length === 0) return

    setIsExecutingWorkflow(true)
    setCurrentStepIndex(0)
    setWorkflowProgress(0)
    abortControllerRef.current = false

    // ステップの状態をリセット
    setWorkflowSteps(prev => prev.map(s => ({ ...s, status: 'pending' })))

    console.log('=== Starting Workflow Execution ===')
    console.log('Execution mode:', executionMode)
    console.log('Total steps:', workflowSteps.length)

    try {
      if (executionMode === 'batch') {
        // 一括実行モード
        console.log('Executing workflow in batch mode')

        // ステップを準備（subcategoryの処理を含む）
        const preparedSteps = workflowSteps.map(step => {
          let subcategory: string | undefined
          let actualOperation: string = step.operation

          if (step.operation.includes('/')) {
            const parts = step.operation.split('/')
            subcategory = parts[0]
            actualOperation = parts[1]
          }

          return {
            id: step.id,
            category: step.category,
            subcategory,
            operation: actualOperation,
            params: step.params,
            description: step.description
          }
        })

        // すべてのステップを実行中に更新
        setWorkflowSteps(prev => prev.map(s => ({ ...s, status: 'running' })))

        // 一括実行
        const result = await rpa.executeWorkflow(preparedSteps, 'sequential')

        console.log('Batch execution result:', result)

        // 結果に基づいてステップの状態を更新
        if (result.results) {
          setWorkflowSteps(prev => prev.map((step, idx) => {
            const stepResult = result.results[idx]
            if (stepResult) {
              return {
                ...step,
                status: stepResult.status === 'completed' ? 'completed' :
                        stepResult.status === 'error' ? 'error' :
                        stepResult.status === 'skipped' ? 'pending' : 'pending',
                error: stepResult.error
              }
            }
            return step
          }))
        }

        setWorkflowProgress(100)
      } else {
        // 順次実行モード（既存の実装）
        console.log('Executing workflow in sequential mode')

        for (let i = 0; i < workflowSteps.length; i++) {
          // 中断チェック
          if (abortControllerRef.current) {
            console.log('Workflow execution aborted')
            break
          }

          const step = workflowSteps[i]
          setCurrentStepIndex(i)
          setWorkflowProgress((i / workflowSteps.length) * 100)

          // ステップの状態を更新
          setWorkflowSteps(prev => prev.map((s, idx) =>
            idx === i ? { ...s, status: 'running' } : s
          ))

          console.log(`=== Executing Step ${i + 1}/${workflowSteps.length} ===`)
          console.log('Category:', step.category)
          console.log('Operation:', step.operation)
          console.log('Params:', step.params)

          try {
            // ネストされた操作の場合、subcategoryとoperationを分割
            let subcategory: string | undefined
            let actualOperation: string = step.operation

            if (step.operation.includes('/')) {
              const parts = step.operation.split('/')
              subcategory = parts[0]
              actualOperation = parts[1]
            }

            const operationRequest = {
              category: step.category,
              subcategory,
              operation: actualOperation,
              params: step.params,
            }

            const result = await rpa.executeOperation(operationRequest)
            console.log(`Step ${i + 1} completed:`, result)

            // ステップの状態を完了に更新
            setWorkflowSteps(prev => prev.map((s, idx) =>
              idx === i ? { ...s, status: 'completed' } : s
            ))

            // 次のステップまで少し待機（デモ用）
            if (i < workflowSteps.length - 1) {
              await new Promise(resolve => setTimeout(resolve, 500))
            }
          } catch (error) {
            console.error(`Step ${i + 1} failed:`, error)

            // ステップの状態をエラーに更新
            setWorkflowSteps(prev => prev.map((s, idx) =>
              idx === i ? { ...s, status: 'error', error: String(error) } : s
            ))

            // エラー時は実行を中断
            alert(`ステップ ${i + 1} でエラーが発生しました: ${error}`)
            break
          }
        }

        setWorkflowProgress(100)
      }
    } catch (error) {
      console.error('Workflow execution failed:', error)
      alert(`ワークフロー実行エラー: ${error}`)
    } finally {
      setIsExecutingWorkflow(false)
      setCurrentStepIndex(-1)
      console.log('=== Workflow Execution Completed ===')
    }
  }, [rpa, workflowSteps, executionMode])

  // ワークフローを中断
  const handleStopWorkflow = () => {
    abortControllerRef.current = true
    setIsExecutingWorkflow(false)
    setCurrentStepIndex(-1)
  }

  // ステップの状態アイコンを取得
  const getStatusIcon = (step: WorkflowStep, index: number) => {
    if (index === currentStepIndex && isExecutingWorkflow) {
      return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
    }

    switch (step.status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      case 'running':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
      default:
        return <div className="h-4 w-4 rounded-full border-2 border-gray-300" />
    }
  }

  // JSONファイルからワークフローをインポート
  const handleImportJSON = (workflowData: any) => {
    try {
      // JSONの妥当性をチェック
      if (!workflowData.steps || !Array.isArray(workflowData.steps)) {
        throw new Error('Invalid workflow format: steps array is required')
      }

      // ステップを変換してインポート
      const importedSteps: WorkflowStep[] = workflowData.steps.map((step: any) => ({
        id: step.id || `step-${Date.now()}-${Math.random()}`,
        category: step.category,
        operation: step.operation,
        params: step.params || {},
        description: step.description || '',
        status: 'pending'
      }))

      // 既存のステップに追加
      setWorkflowSteps(prev => [...prev, ...importedSteps])

      alert(`${importedSteps.length}個のステップをインポートしました`)
    } catch (error) {
      console.error('Failed to import workflow:', error)
      alert(`インポートエラー: ${error}`)
    }
  }

  // ファイル選択からJSONをインポート
  const handleFileImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string
        const workflowData = JSON.parse(content)
        handleImportJSON(workflowData)
      } catch (error) {
        console.error('Failed to parse JSON file:', error)
        alert('JSONファイルの解析に失敗しました')
      }
    }
    reader.readAsText(file)

    // inputをリセット（同じファイルを再選択可能にする）
    event.target.value = ''
  }

  // ワークフローをJSONとしてエクスポート
  const handleExportJSON = () => {
    const exportData = {
      name: 'Exported Workflow',
      description: 'Exported from RPA Demo',
      version: '1.0.0',
      timestamp: new Date().toISOString(),
      steps: workflowSteps.map(step => ({
        id: step.id,
        category: step.category,
        operation: step.operation,
        params: step.params,
        description: step.description
      }))
    }

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `workflow_${Date.now()}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="h-full flex flex-col">
      {/* 接続状態ヘッダー */}
      <div className="flex-shrink-0 p-4">
        <Card>
          <CardContent className="py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {rpa.status.connected ? (
                  <Wifi className="h-5 w-5 text-green-500" />
                ) : rpa.status.connecting ? (
                  <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />
                ) : (
                  <WifiOff className="h-5 w-5 text-gray-400" />
                )}
                <div>
                  <div className="font-medium text-sm">
                    {rpa.status.connected ? 'エージェント接続済み' :
                     rpa.status.connecting ? 'エージェント接続中...' :
                     'エージェント未接続'}
                  </div>
                  {rpa.status.capabilities && (
                    <div className="text-xs text-muted-foreground">
                      バージョン: {rpa.status.capabilities.version} |
                      操作数: {Object.values(operations).reduce((sum: number, ops) => sum + (Array.isArray(ops) ? ops.length : 0), 0)}
                    </div>
                  )}
                </div>
              </div>
              <div className="flex gap-2">
                {!rpa.status.connected ? (
                  <Button
                    onClick={rpa.connect}
                    disabled={rpa.status.connecting}
                    size="sm"
                  >
                    {rpa.status.connecting ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Wifi className="h-4 w-4 mr-2" />
                    )}
                    接続
                  </Button>
                ) : (
                  <Button
                    variant="outline"
                    onClick={rpa.disconnect}
                    size="sm"
                  >
                    <WifiOff className="h-4 w-4 mr-2" />
                    切断
                  </Button>
                )}
              </div>
            </div>
            {rpa.status.error && (
              <Alert className="mt-3">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{rpa.status.error}</AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      </div>

      {/* メインコンテンツ */}
      {rpa.status.connected && operations && (
        <div className="flex-1 grid grid-cols-[350px_1fr] gap-4 p-4 pt-0 overflow-hidden min-h-0">
          {/* 左側: 操作一覧 */}
          <Card className="flex flex-col overflow-hidden h-full">
            <CardHeader className="pb-3 flex-shrink-0">
              <CardTitle className="text-lg">操作一覧</CardTitle>
              <div className="mt-2 relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="操作を検索..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto p-4">
              <Accordion type="multiple" className="w-full">
                {Object.entries(filteredOperations).map(([category, ops]) => (
                  <AccordionItem key={category} value={category}>
                    <AccordionTrigger className="hover:no-underline py-2">
                      <div className="flex items-center gap-2">
                        {categoryIcons[category]}
                        <span className="text-sm font-medium">{category.substring(2)}</span>
                        <Badge variant="secondary" className="ml-auto mr-2 text-xs">
                          {ops.length}
                        </Badge>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="pb-2">
                      <div className="space-y-1 pl-6">
                        {ops.map((operation: string) => {
                          // ネスト構造の操作を処理
                          const parts = operation.split('/')
                          const isNested = parts.length > 1
                          const displayName = parts[parts.length - 1]
                          const parentName = isNested ? parts[0] : null

                          return (
                            <div
                              key={operation}
                              className={`flex items-center justify-between py-1.5 px-2 rounded hover:bg-accent cursor-pointer group ${
                                isNested ? 'ml-4' : ''
                              }`}
                              onClick={() => handleAddOperation(category, operation)}
                            >
                              <div className="flex items-center gap-2 text-sm">
                                {isNested && (
                                  <span className="text-muted-foreground text-xs">
                                    {parentName} ›
                                  </span>
                                )}
                                <span>{displayName}</span>
                              </div>
                              <Plus className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                            </div>
                          )
                        })}
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </CardContent>
          </Card>

          {/* 右側: ワークフロービルダー */}
          <Card className="flex flex-col overflow-hidden h-full">
            <CardHeader className="pb-3 flex-shrink-0">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">ワークフロー</CardTitle>
                  <CardDescription className="text-xs mt-1">
                    {workflowSteps.length === 0
                      ? "左側から操作を選択して追加してください"
                      : `${workflowSteps.length} ステップ`}
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  {/* インポート/エクスポートボタン */}
                  <div className="flex items-center gap-1">
                    <input
                      type="file"
                      accept=".json"
                      onChange={handleFileImport}
                      className="hidden"
                      id="json-file-input"
                    />
                    <label htmlFor="json-file-input">
                      <Button
                        size="sm"
                        variant="outline"
                        className="h-8"
                        disabled={isExecutingWorkflow}
                        asChild
                      >
                        <span>
                          <Upload className="h-3 w-3 mr-1" />
                          インポート
                        </span>
                      </Button>
                    </label>
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-8"
                      onClick={handleExportJSON}
                      disabled={isExecutingWorkflow || workflowSteps.length === 0}
                    >
                      <Download className="h-3 w-3 mr-1" />
                      エクスポート
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-8"
                      onClick={() => {
                        if (confirm('ワークフローをクリアしますか？')) {
                          setWorkflowSteps([])
                        }
                      }}
                      disabled={isExecutingWorkflow || workflowSteps.length === 0}
                    >
                      <Trash2 className="h-3 w-3 mr-1" />
                      クリア
                    </Button>
                  </div>

                  <Separator orientation="vertical" className="h-6" />

                  {/* 実行モード切り替え */}
                  <div className="flex items-center gap-2">
                    <Label htmlFor="execution-mode" className="text-xs">
                      一括実行
                    </Label>
                    <Switch
                      id="execution-mode"
                      checked={executionMode === 'batch'}
                      onCheckedChange={(checked) =>
                        setExecutionMode(checked ? 'batch' : 'sequential')
                      }
                      disabled={isExecutingWorkflow}
                    />
                  </div>
                  <Button
                    onClick={handleExecuteWorkflow}
                    disabled={isExecutingWorkflow || workflowSteps.length === 0}
                    size="sm"
                  >
                    {isExecutingWorkflow ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                        実行中...
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4 mr-1" />
                        実行
                      </>
                    )}
                  </Button>
                </div>
              </div>
              {isExecutingWorkflow && (
                <div className="mt-3">
                  <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                    <span>
                      {executionMode === 'batch'
                        ? '一括実行中...'
                        : `ステップ ${currentStepIndex + 1}/${workflowSteps.length}`}
                    </span>
                    <span>{Math.round(workflowProgress)}%</span>
                  </div>
                  <Progress value={workflowProgress} className="h-2" />
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={handleStopWorkflow}
                    className="mt-2 w-full"
                  >
                    <StopCircle className="h-4 w-4 mr-1" />
                    中断
                  </Button>
                </div>
              )}
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto p-4">
              {workflowSteps.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
                  <Folder className="h-12 w-12 mb-3 opacity-20" />
                  <p className="text-sm">ワークフローが空です</p>
                  <p className="text-xs mt-1">左側から操作を選択して追加してください</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {workflowSteps.map((step, index) => (
                    <div
                      key={step.id}
                      className={`flex items-center gap-2 p-3 rounded-lg border transition-colors ${
                        index === currentStepIndex && isExecutingWorkflow
                          ? 'border-blue-500 bg-blue-50'
                          : step.status === 'completed'
                          ? 'border-green-200 bg-green-50'
                          : step.status === 'error'
                          ? 'border-red-200 bg-red-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      {/* ステータスアイコン */}
                      <div className="flex-shrink-0">
                        {getStatusIcon(step, index)}
                      </div>

                      {/* ステップ番号 */}
                      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-medium">
                        {index + 1}
                      </div>

                      {/* ステップ情報 */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">
                            {step.category.substring(2)}
                          </Badge>
                          <span className="font-medium text-sm truncate">{step.operation}</span>
                        </div>
                        {step.description && (
                          <p className="text-xs text-muted-foreground mt-0.5 truncate">
                            {step.description}
                          </p>
                        )}
                        {step.error && (
                          <p className="text-xs text-red-600 mt-0.5">{step.error}</p>
                        )}
                      </div>

                      {/* アクションボタン */}
                      {!isExecutingWorkflow && (
                        <div className="flex-shrink-0 flex items-center gap-1">
                          <Button
                            size="icon"
                            variant="ghost"
                            className="h-7 w-7"
                            onClick={() => handleMoveUp(index)}
                            disabled={index === 0}
                          >
                            <ChevronUp className="h-3 w-3" />
                          </Button>
                          <Button
                            size="icon"
                            variant="ghost"
                            className="h-7 w-7"
                            onClick={() => handleMoveDown(index)}
                            disabled={index === workflowSteps.length - 1}
                          >
                            <ChevronDown className="h-3 w-3" />
                          </Button>
                          <Button
                            size="icon"
                            variant="ghost"
                            className="h-7 w-7"
                            onClick={() => handleDuplicateStep(step)}
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                          <Button
                            size="icon"
                            variant="ghost"
                            className="h-7 w-7"
                            onClick={() => handleEditStep(step)}
                          >
                            <Edit2 className="h-3 w-3" />
                          </Button>
                          <Button
                            size="icon"
                            variant="ghost"
                            className="h-7 w-7 text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteStep(step.id)}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* 接続待機中の表示 */}
      {!rpa.status.connected && !rpa.status.error && (
        <div className="flex-1 flex items-center justify-center p-4">
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12 px-8">
              <Loader2 className="h-8 w-8 text-muted-foreground animate-spin mb-4" />
              <p className="text-muted-foreground">
                RPAエージェントへの接続を待っています...
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ステップ編集ダイアログ */}
      <Dialog open={isAddingStep} onOpenChange={setIsAddingStep}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editingStep ? 'ステップを編集' : 'ステップを追加'}
            </DialogTitle>
            <DialogDescription>
              パラメータを設定してください
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* パラメータ入力 */}
            {editingStep && (
              <>
                <div className="space-y-2">
                  <Label>操作</Label>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{editingStep.category.substring(2)}</Badge>
                    <span className="font-medium">{editingStep.operation}</span>
                  </div>
                </div>

                <Separator />

                <div className="space-y-2">
                  <Label>パラメータ</Label>
                  <div className="space-y-3">
                    {Object.entries(stepParams).map(([key, value]) => (
                      <div key={key} className="space-y-1">
                        <Label className="text-sm">{key}</Label>
                        <Input
                          value={value}
                          onChange={(e) =>
                            setStepParams({ ...stepParams, [key]: e.target.value })
                          }
                          placeholder={`${key}を入力`}
                        />
                      </div>
                    ))}
                    {Object.keys(stepParams).length === 0 && (
                      <p className="text-sm text-muted-foreground">
                        この操作にはパラメータがありません
                      </p>
                    )}
                  </div>
                </div>

                {/* 説明 */}
                <div className="space-y-2">
                  <Label>説明（オプション）</Label>
                  <Input
                    value={stepDescription}
                    onChange={(e) => setStepDescription(e.target.value)}
                    placeholder="このステップの説明を入力"
                  />
                </div>
              </>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={resetForm}>
              キャンセル
            </Button>
            {editingStep && (
              <Button onClick={handleUpdateStep}>
                <Save className="h-4 w-4 mr-2" />
                更新
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}