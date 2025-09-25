import { useEffect, useMemo, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import { PageLayout } from '@/components/layout/PageLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { ScrollArea } from '@/components/ui/scroll-area'
import { ArrowDown, ArrowLeft, ArrowRight, Bot, CheckCircle, Layers, Loader2, Save, Send, Settings, TestTube, Upload, Workflow, X } from 'lucide-react'
import axios from 'axios'

type ViewMode = 'groups' | 'detailed'

type GeneratedGroup = {
  id: string
  title: string
  description: string
  steps: number
  icon: React.ComponentType<any>
}

type WorkflowStep = {
  id: string
  title: string
  description: string
  type: 'trigger' | 'action' | 'condition'
  status?: 'configured' | 'pending'
  icon?: React.ComponentType<any>
}

export default function WorkflowEdit() {
  const { workflowId } = useParams()
  const [wfTitle, setWfTitle] = useState<string>('')
  const [wfDescription, setWfDescription] = useState<string>('')
  const apiBase = (import.meta as any).env?.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
  const [chatMessages, setChatMessages] = useState<{ role: 'user' | 'assistant'; content: string }[]>([])

  const [workflowCreationStep, setWorkflowCreationStep] = useState<3 | 4>(3)
  const [newWorkflowViewMode, setNewWorkflowViewMode] = useState<ViewMode>('groups')
  const [selectedNewWorkflowGroup, setSelectedNewWorkflowGroup] = useState<string | null>(null)
  const [selectedStep, setSelectedStep] = useState<string | null>(null)
  const [selectedStepsForTest, setSelectedStepsForTest] = useState<Set<string>>(new Set())
  const fileInputRef = useRef<HTMLInputElement | null>(null)

  // Mock data
  const generatedGroups: GeneratedGroup[] = useMemo(
    () => [
      { id: 'grp-1', title: '入力の取得', description: 'メールやファイルから入力データを収集します', steps: 2, icon: Layers },
      { id: 'grp-2', title: 'データの検証', description: '抽出データを検証し整形します', steps: 3, icon: Layers },
      { id: 'grp-3', title: '出力/通知', description: '結果の保存や通知を行います', steps: 2, icon: Layers },
    ],
    []
  )

  const [workflowSteps, setWorkflowSteps] = useState<WorkflowStep[]>([
    { id: 'st-1', title: 'トリガー: メール受信', description: '指定ラベルの新着メールで開始', type: 'trigger', status: 'configured' },
    { id: 'st-2', title: 'テキスト抽出', description: '本文から必要情報を抽出', type: 'action' },
    { id: 'st-3', title: '条件: 金額が閾値以上', description: '条件に応じて分岐', type: 'condition' },
    { id: 'st-4', title: '通知送信', description: 'Slackへ結果を通知', type: 'action' },
  ])

  useEffect(() => {
    // 簡易的にロード中UI→完了UIへ遷移
    const t = setTimeout(() => setWorkflowCreationStep(4), 1200)
    return () => clearTimeout(t)
  }, [])

  useEffect(() => {
    const load = async () => {
      if (!workflowId) return
      try {
        const res = await axios.get(`${apiBase}/workflow/${workflowId}`)
        setWfTitle(res.data?.name ?? '')
        setWfDescription(res.data?.description ?? '')
      } catch {
        // noop
      }
    }
    load()
  }, [apiBase, workflowId])

  useEffect(() => {
    const loadHistory = async () => {
      if (!workflowId) return
      try {
        const res = await axios.get(`${apiBase}/workflows/${workflowId}/messages`)
        const msgs = (res.data || []) as { role: 'user' | 'assistant'; content: string }[]
        if (msgs.length > 0) setChatMessages(msgs)
      } catch {
        // noop
      }
    }
    loadHistory()
  }, [apiBase, workflowId])

  const toggleStepForTest = (id: string) => {
    setSelectedStepsForTest(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const addWorkflowStep = () => {
    const n = workflowSteps.length + 1
    setWorkflowSteps(prev => [...prev, { id: `st-${n}`, title: `アクション ${n}`, description: '詳細設定', type: 'action' }])
  }

  const getStepIcon = (type: WorkflowStep['type']) => {
    switch (type) {
      case 'trigger':
        return { color: 'text-green-600 border-green-300', bg: 'bg-green-50', icon: Layers }
      case 'condition':
        return { color: 'text-orange-600 border-orange-300', bg: 'bg-orange-50', icon: Layers }
      default:
        return { color: 'text-blue-600 border-blue-300', bg: 'bg-blue-50', icon: Layers }
    }
  }

  // ===== JSONインポート（generated_step_list.json 形式） =====
  type ImportedSequenceItem = {
    uuid?: string
    cmd?: string
    ['cmd-nickname']?: string
    ['cmd-type']?: string
    description?: string
  }

  type ImportedGeneratedList = {
    name?: string
    description?: string
    sequence?: ImportedSequenceItem[]
  }

  const mapImportedItemToWorkflowStep = (item: ImportedSequenceItem, index: number): WorkflowStep => {
    const isCondition = item['cmd-type'] === 'branching'
    const stepType: WorkflowStep['type'] = isCondition ? 'condition' : (index === 0 ? 'trigger' : 'action')
    const title = item['cmd-nickname'] || item.cmd || `ステップ ${index + 1}`
    const description = item.description || ''
    const id = item.uuid || `imp-${index + 1}`
    return { id, title, description, type: stepType }
  }

  const handleImportClick = () => fileInputRef.current?.click()

  const handleJsonImport: React.ChangeEventHandler<HTMLInputElement> = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      try {
        const text = (reader.result as string) || ''
        const data = JSON.parse(text) as ImportedGeneratedList
        const seq = Array.isArray(data.sequence) ? data.sequence : []
        const steps = seq.map(mapImportedItemToWorkflowStep)

        if (steps.length === 0) {
          window.alert('JSON内に有効なステップが見つかりません。')
        }

        setWorkflowSteps(steps)
        if (data.name) setWfTitle(data.name)
        if (typeof data.description === 'string') setWfDescription(data.description)

        // 表示を詳細ビューに切り替え、生成中のUIを完了状態へ
        setNewWorkflowViewMode('detailed')
        setSelectedNewWorkflowGroup(null)
        setWorkflowCreationStep(4)
      } catch (err) {
        console.error(err)
        window.alert('JSONの解析に失敗しました。ファイル形式を確認してください。')
      } finally {
        // 同じファイルを再選択できるように値をクリア
        e.target.value = ''
      }
    }
    reader.readAsText(file)
  }

  return (
    <>
    <PageLayout title={wfTitle || 'ワークフロー編集'} description={wfDescription || ''} maxWidth="full" className="pr-80">
      <div className="flex h-[calc(100vh-8rem)]">
        {/* 左側 */}
        <div className="flex-1 flex flex-col">
          {workflowCreationStep === 3 ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center space-y-4">
                <div className="w-16 h-16 mx-auto rounded-full bg-primary/10 flex items-center justify-center">
                  <Loader2 className="h-8 w-8 text-primary animate-spin" />
                </div>
                <h3 className="text-xl font-semibold">詳細ステップを作成中...</h3>
                <p className="text-muted-foreground">AIがワークフローの詳細を生成しています</p>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex">
              {/* ワークフロー図 */}
              <div className="flex-1 p-6 bg-gray-50/50">
                <div className="mb-6 flex items-center justify-center">
                  <div className="flex space-x-2">
                    <div className="flex border rounded-lg">
                      <Button
                        variant={newWorkflowViewMode === 'groups' ? 'default' : 'ghost'}
                        size="sm"
                        onClick={() => setNewWorkflowViewMode('groups')}
                        className="rounded-r-none"
                      >
                        <Layers className="h-4 w-4 mr-2" />
                        グループ表示
                      </Button>
                      <Button
                        variant={newWorkflowViewMode === 'detailed' ? 'default' : 'ghost'}
                        size="sm"
                        onClick={() => setNewWorkflowViewMode('detailed')}
                        className="rounded-l-none"
                      >
                        <Workflow className="h-4 w-4 mr-2" />
                        詳細表示
                      </Button>
                    </div>
                    <Button variant="outline" onClick={handleImportClick}>
                      <Upload className="h-4 w-4 mr-2" />
                      JSONをインポート
                    </Button>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="application/json,.json"
                      onChange={handleJsonImport}
                      className="hidden"
                    />
                    <Button variant="outline">
                      <TestTube className="h-4 w-4 mr-2" />
                      テスト実行
                    </Button>
                    <Button>
                      <Save className="h-4 w-4 mr-2" />
                      ワークフローを保存
                    </Button>
                  </div>
                </div>

                {newWorkflowViewMode === 'groups' ? (
                  <div className="max-w-2xl mx-auto">
                    <div className="space-y-4">
                      {generatedGroups.map((group, index) => {
                        const GroupIcon = group.icon
                        return (
                          <div key={group.id}>
                            <Card
                              className="cursor-pointer transition-all hover:shadow-md border-2 hover:border-primary/50"
                              onClick={() => {
                                setSelectedNewWorkflowGroup(group.id)
                                setNewWorkflowViewMode('detailed')
                              }}
                            >
                              <CardContent className="p-6">
                                <div className="flex items-start space-x-4">
                                  <div className="p-3 rounded-full bg-primary/10 border border-primary/20">
                                    <GroupIcon className="h-6 w-6 text-primary" />
                                  </div>
                                  <div className="flex-1">
                                    <div className="flex items-center justify-between">
                                      <h3 className="font-semibold text-lg">{group.title}</h3>
                                      <div className="flex items-center space-x-2">
                                        <Badge variant="outline" className="text-xs">{group.steps}ステップ</Badge>
                                        <ArrowRight className="h-4 w-4 text-muted-foreground" />
                                      </div>
                                    </div>
                                    <p className="text-muted-foreground mt-2 leading-relaxed">{group.description}</p>
                                    <div className="flex items-center mt-3 space-x-2">
                                      <span className="text-xs text-muted-foreground">クリックして詳細を表示</span>
                                    </div>
                                  </div>
                                </div>
                              </CardContent>
                            </Card>
                            {index < generatedGroups.length - 1 && (
                              <div className="flex justify-center py-3">
                                <ArrowDown className="h-5 w-5 text-muted-foreground" />
                              </div>
                            )}
                          </div>
                        )
                      })}
                    </div>
                  </div>
                ) : (
                  <div className="max-w-md mx-auto">
                    {selectedNewWorkflowGroup && (
                      <div className="mb-6">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setNewWorkflowViewMode('groups')
                            setSelectedNewWorkflowGroup(null)
                          }}
                          className="mb-4"
                        >
                          <ArrowLeft className="h-4 w-4 mr-2" />
                          グループ表示に戻る
                        </Button>
                        <div className="bg-card p-4 rounded-lg border">
                          <h3 className="font-semibold text-lg">
                            {generatedGroups.find(g => g.id === selectedNewWorkflowGroup)?.title}
                          </h3>
                          <p className="text-sm text-muted-foreground mt-1">
                            {generatedGroups.find(g => g.id === selectedNewWorkflowGroup)?.description}
                          </p>
                        </div>
                      </div>
                    )}

                    <div className="space-y-4">
                      {workflowSteps.map((step, index, steps) => {
                        const stepStyle = getStepIcon(step.type)
                        const StepIcon = step.icon || stepStyle.icon
                        return (
                          <div key={step.id}>
                            <Card
                              className={`cursor-pointer transition-all hover:shadow-md ${selectedStep === step.id ? 'ring-2 ring-primary shadow-md' : ''} ${stepStyle.bg} border-2`}
                              onClick={() => setSelectedStep(step.id)}
                            >
                              <CardContent className="p-4">
                                <div className="flex items-start space-x-3">
                                  <div className="flex items-start space-x-2">
                                    <input
                                      type="checkbox"
                                      checked={selectedStepsForTest.has(step.id)}
                                      onChange={() => toggleStepForTest(step.id)}
                                      onClick={(e) => e.stopPropagation()}
                                      className="mt-1 h-4 w-4 text-primary border-gray-300 rounded focus:ring-primary"
                                    />
                                    <div className={`p-2 rounded-full bg-white border ${stepStyle.color}`}>
                                      <StepIcon className="h-5 w-5" />
                                    </div>
                                  </div>
                                  <div className="flex-1">
                                    <div className="flex items-center justify-between">
                                      <h3 className="font-semibold text-sm">{step.title}</h3>
                                      <div className="flex items-center space-x-1">
                                        {step.status === 'configured' && <CheckCircle className="h-4 w-4 text-green-500" />}
                                        <Button
                                          size="sm"
                                          variant="ghost"
                                          onClick={(e) => {
                                            e.stopPropagation()
                                            setWorkflowSteps(prev => prev.filter(s => s.id !== step.id))
                                          }}
                                          className="h-6 w-6 p-0 hover:bg-red-100 hover:text-red-600"
                                        >
                                          <X className="h-3 w-3" />
                                        </Button>
                                      </div>
                                    </div>
                                    <p className="text-xs text-muted-foreground mt-1">{step.description}</p>
                                    {step.type === 'trigger' && <Badge variant="outline" className="mt-2 text-xs">トリガー</Badge>}
                                    {step.type === 'condition' && (
                                      <Badge variant="outline" className="mt-2 text-xs bg-orange-50 text-orange-700">条件分岐</Badge>
                                    )}
                                  </div>
                                </div>
                              </CardContent>
                            </Card>
                            {index < steps.length - 1 && (
                              <div className="flex justify-center py-2">
                                <ArrowDown className="h-5 w-5 text-muted-foreground" />
                              </div>
                            )}
                          </div>
                        )
                      })}

                      <div className="flex justify-center py-4">
                        <Button variant="outline" onClick={addWorkflowStep} className="border-dashed border-2 hover:border-primary bg-transparent">
                          <Layers className="h-4 w-4 mr-2" />
                          ステップを追加
                        </Button>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* 右側：ステップ詳細設定パネル */}
              {selectedStep && (
                <div className="w-80 border-l bg-card">
                  <div className="p-4 border-b">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold">ステップ設定</h3>
                      <Button size="sm" variant="ghost" onClick={() => setSelectedStep(null)}>
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  <ScrollArea className="h-[calc(100vh-12rem)]">
                    <div className="p-4 space-y-4">
                      <div className="flex items-center space-x-3 p-3 bg-muted/50 rounded-lg">
                        <div className={`p-2 rounded-full bg-white border ${getStepIcon((workflowSteps.find(s => s.id === selectedStep)?.type) || 'action').color}`}>
                          <Layers className="h-5 w-5" />
                        </div>
                        <div>
                          <h4 className="font-medium">{workflowSteps.find(s => s.id === selectedStep)?.title}</h4>
                          <p className="text-sm text-muted-foreground">{workflowSteps.find(s => s.id === selectedStep)?.description}</p>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <div>
                          <Label>ステップ名</Label>
                          <Input defaultValue={workflowSteps.find(s => s.id === selectedStep)?.title} />
                        </div>
                        <div>
                          <Label>説明</Label>
                          <Textarea defaultValue={workflowSteps.find(s => s.id === selectedStep)?.description} rows={2} />
                        </div>
                        <div className="pt-4 border-t">
                          <Button className="w-full">
                            <Settings className="h-4 w-4 mr-2" />
                            設定を保存
                          </Button>
                        </div>
                      </div>
                    </div>
                  </ScrollArea>
                </div>
              )}
            </div>
          )}
        </div>

      </div>
    </PageLayout>
    {/* 固定表示の右側AIアシスタント（画面最上部〜最下部） */}
    <div className="fixed right-0 top-0 bottom-0 w-80 border-l bg-muted/10 flex flex-col">
      <div className="p-4 border-b">
        <h3 className="font-semibold flex items-center">
          <Bot className="h-4 w-4 mr-2" />
          ワークフローアシスタント
        </h3>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-sm">
        {chatMessages.length === 0 && (
          <p className="text-muted-foreground">履歴はまだありません。</p>
        )}
        {chatMessages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-3 py-2 ${
                message.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'
              }`}
            >
              <p className="whitespace-pre-wrap text-sm">{message.content}</p>
            </div>
          </div>
        ))}
      </div>
      <div className="p-4 border-t bg-card">
        <div className="flex space-x-2">
          <Input placeholder="メッセージを入力..." />
          <Button size="sm">
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
    </>
  )
}


