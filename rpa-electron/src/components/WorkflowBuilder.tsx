/**
 * Workflow Builder Component
 * ワークフローの作成と編集を行うコンポーネント
 */

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Plus,
  Play,
  Trash2,
  Edit2,
  Save,
  MoveUp,
  MoveDown,
  Copy,
  AlertCircle,
  CheckCircle,
  Loader2,
} from 'lucide-react'

export interface WorkflowStep {
  id: string
  category: string
  operation: string
  params: Record<string, any>
  description?: string
  status?: 'pending' | 'running' | 'completed' | 'error'
  error?: string
}

interface WorkflowBuilderProps {
  operations: Record<string, string[]>
  operationTemplates?: any
  onExecute?: (steps: WorkflowStep[]) => void
  isExecuting?: boolean
  currentStepIndex?: number
}

export function WorkflowBuilder({
  operations,
  operationTemplates,
  onExecute,
  isExecuting = false,
  currentStepIndex = -1,
}: WorkflowBuilderProps) {
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
  const [steps, setSteps] = useState<WorkflowStep[]>([])
  const [editingStep, setEditingStep] = useState<WorkflowStep | null>(null)
  const [isAddingStep, setIsAddingStep] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [selectedOperation, setSelectedOperation] = useState<string>('')
  const [stepParams, setStepParams] = useState<Record<string, any>>({})
  const [stepDescription, setStepDescription] = useState('')

  // ステップを追加
  const handleAddStep = () => {
    if (!selectedCategory || !selectedOperation) return

    const newStep: WorkflowStep = {
      id: `step-${Date.now()}`,
      category: selectedCategory,
      operation: selectedOperation,
      params: { ...stepParams },
      description: stepDescription || `${selectedCategory.substring(2)} → ${selectedOperation}`,
      status: 'pending',
    }

    setSteps([...steps, newStep])
    resetForm()
  }

  // ステップを更新
  const handleUpdateStep = () => {
    if (!editingStep) return

    const updatedSteps = steps.map((step) =>
      step.id === editingStep.id
        ? {
            ...editingStep,
            params: { ...stepParams },
            description: stepDescription,
          }
        : step
    )

    setSteps(updatedSteps)
    setEditingStep(null)
    resetForm()
  }

  // ステップを削除
  const handleDeleteStep = (id: string) => {
    setSteps(steps.filter((step) => step.id !== id))
  }

  // ステップを複製
  const handleDuplicateStep = (step: WorkflowStep) => {
    const newStep: WorkflowStep = {
      ...step,
      id: `step-${Date.now()}`,
      status: 'pending',
    }
    const index = steps.findIndex((s) => s.id === step.id)
    const newSteps = [...steps]
    newSteps.splice(index + 1, 0, newStep)
    setSteps(newSteps)
  }

  // ステップを上に移動
  const handleMoveUp = (index: number) => {
    if (index === 0) return
    const newSteps = [...steps]
    ;[newSteps[index - 1], newSteps[index]] = [newSteps[index], newSteps[index - 1]]
    setSteps(newSteps)
  }

  // ステップを下に移動
  const handleMoveDown = (index: number) => {
    if (index === steps.length - 1) return
    const newSteps = [...steps]
    ;[newSteps[index], newSteps[index + 1]] = [newSteps[index + 1], newSteps[index]]
    setSteps(newSteps)
  }

  // フォームをリセット
  const resetForm = () => {
    setIsAddingStep(false)
    setSelectedCategory('')
    setSelectedOperation('')
    setStepParams({})
    setStepDescription('')
  }

  // 編集を開始
  const handleEditStep = (step: WorkflowStep) => {
    setEditingStep(step)
    setSelectedCategory(step.category)
    setSelectedOperation(step.operation)
    setStepParams(step.params)
    setStepDescription(step.description || '')
    setIsAddingStep(true)
  }

  // カテゴリが選択された時
  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category)
    setSelectedOperation('')
    setStepParams({})
  }

  // 操作が選択された時
  const handleOperationChange = (operation: string) => {
    setSelectedOperation(operation)
    // デフォルトパラメータを設定
    const template = getOperationTemplate(selectedCategory, operation)
    setStepParams(template)
  }

  // ワークフローを実行
  const handleExecute = () => {
    if (steps.length === 0) return
    onExecute?.(steps)
  }

  // ステップの状態アイコンを取得
  const getStatusIcon = (step: WorkflowStep, index: number) => {
    if (index === currentStepIndex && isExecuting) {
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

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>ワークフロービルダー</CardTitle>
          <CardDescription>
            操作を組み合わせてワークフローを作成します
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* ワークフローステップ一覧 */}
            <ScrollArea className="h-[400px] w-full rounded-md border p-4">
              {steps.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-32 text-muted-foreground">
                  <p className="text-sm">ワークフローステップがありません</p>
                  <p className="text-xs mt-1">下の「ステップを追加」ボタンから追加してください</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {steps.map((step, index) => (
                    <div
                      key={step.id}
                      className={`flex items-center gap-2 p-3 rounded-lg border ${
                        index === currentStepIndex && isExecuting
                          ? 'border-blue-500 bg-blue-50'
                          : step.status === 'completed'
                          ? 'border-green-200 bg-green-50'
                          : step.status === 'error'
                          ? 'border-red-200 bg-red-50'
                          : 'border-gray-200'
                      }`}
                    >
                      {/* ステータスアイコン */}
                      <div className="flex-shrink-0">
                        {getStatusIcon(step, index)}
                      </div>

                      {/* ステップ番号 */}
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-medium">
                        {index + 1}
                      </div>

                      {/* ステップ情報 */}
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">
                            {step.category.substring(2)}
                          </Badge>
                          <span className="font-medium text-sm">{step.operation}</span>
                        </div>
                        {step.description && (
                          <p className="text-xs text-muted-foreground mt-1">{step.description}</p>
                        )}
                        {step.error && (
                          <p className="text-xs text-red-600 mt-1">{step.error}</p>
                        )}
                      </div>

                      {/* アクションボタン */}
                      {!isExecuting && (
                        <div className="flex-shrink-0 flex items-center gap-1">
                          <Button
                            size="icon"
                            variant="ghost"
                            className="h-8 w-8"
                            onClick={() => handleMoveUp(index)}
                            disabled={index === 0}
                          >
                            <MoveUp className="h-4 w-4" />
                          </Button>
                          <Button
                            size="icon"
                            variant="ghost"
                            className="h-8 w-8"
                            onClick={() => handleMoveDown(index)}
                            disabled={index === steps.length - 1}
                          >
                            <MoveDown className="h-4 w-4" />
                          </Button>
                          <Button
                            size="icon"
                            variant="ghost"
                            className="h-8 w-8"
                            onClick={() => handleDuplicateStep(step)}
                          >
                            <Copy className="h-4 w-4" />
                          </Button>
                          <Button
                            size="icon"
                            variant="ghost"
                            className="h-8 w-8"
                            onClick={() => handleEditStep(step)}
                          >
                            <Edit2 className="h-4 w-4" />
                          </Button>
                          <Button
                            size="icon"
                            variant="ghost"
                            className="h-8 w-8"
                            onClick={() => handleDeleteStep(step.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>

            {/* アクションボタン */}
            <div className="flex gap-2">
              <Button
                onClick={() => setIsAddingStep(true)}
                disabled={isExecuting}
                className="flex-1"
              >
                <Plus className="h-4 w-4 mr-2" />
                ステップを追加
              </Button>
              <Button
                onClick={handleExecute}
                disabled={steps.length === 0 || isExecuting}
                className="flex-1"
              >
                {isExecuting ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Play className="h-4 w-4 mr-2" />
                )}
                ワークフローを実行
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ステップ追加/編集ダイアログ */}
      <Dialog open={isAddingStep} onOpenChange={setIsAddingStep}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editingStep ? 'ステップを編集' : 'ステップを追加'}
            </DialogTitle>
            <DialogDescription>
              実行する操作とパラメータを設定してください
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* カテゴリ選択 */}
            <div className="space-y-2">
              <Label>カテゴリ</Label>
              <Select value={selectedCategory} onValueChange={handleCategoryChange}>
                <SelectTrigger>
                  <SelectValue placeholder="カテゴリを選択" />
                </SelectTrigger>
                <SelectContent>
                  {Object.keys(operations).map((category) => (
                    <SelectItem key={category} value={category}>
                      {category.substring(2)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* 操作選択 */}
            {selectedCategory && (
              <div className="space-y-2">
                <Label>操作</Label>
                <Select value={selectedOperation} onValueChange={handleOperationChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="操作を選択" />
                  </SelectTrigger>
                  <SelectContent>
                    {operations[selectedCategory]?.map((operation) => (
                      <SelectItem key={operation} value={operation}>
                        {operation}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            {/* パラメータ入力 */}
            {selectedOperation && (
              <>
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
            {editingStep ? (
              <Button onClick={handleUpdateStep} disabled={!selectedOperation}>
                <Save className="h-4 w-4 mr-2" />
                更新
              </Button>
            ) : (
              <Button onClick={handleAddStep} disabled={!selectedOperation}>
                <Plus className="h-4 w-4 mr-2" />
                追加
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}