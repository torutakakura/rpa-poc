import { useEffect, useRef, useState } from 'react'
import { useParams, useLocation } from 'react-router-dom'
import { PageLayout } from '@/components/layout/PageLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { ScrollArea } from '@/components/ui/scroll-area'
import { ArrowDown, ArrowLeft, ArrowRight, Bot, CheckCircle, Layers, Loader2, Pencil, RefreshCw, Save, Send, Settings, TestTube, Upload, Workflow, X } from 'lucide-react'
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
  const location = useLocation() as any
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
  const [isEditingTitle, setIsEditingTitle] = useState(false)
  const [draftTitle, setDraftTitle] = useState<string>('')

  const [generatedGroups, setGeneratedGroups] = useState<GeneratedGroup[]>([])

  const [workflowSteps, setWorkflowSteps] = useState<WorkflowStep[]>([])
  const hasBuildDataProcessed = useRef(false)
  const [isRebuilding, setIsRebuilding] = useState(false)

  // アシスタントパネルの幅管理
  const [assistantWidth, setAssistantWidth] = useState(320) // デフォルト幅 320px
  const [isResizing, setIsResizing] = useState(false)
  const assistantRef = useRef<HTMLDivElement | null>(null)
  const MIN_WIDTH = 280
  const MAX_WIDTH = 780

  // チャット機能の状態管理
  const [assistantInput, setAssistantInput] = useState('')
  const [assistantLoading, setAssistantLoading] = useState(false)
  const assistantTextareaRef = useRef<HTMLTextAreaElement | null>(null)
  const chatScrollRef = useRef<HTMLDivElement | null>(null)

  // HearingChatからbuildDataが渡された場合の処理
  useEffect(() => {
    const buildData = location?.state?.buildData
    console.log('+++++++++++++++++')
    console.log('buildData', buildData)
    if (buildData && !hasBuildDataProcessed.current) {
      hasBuildDataProcessed.current = true

      // generatedフィールドからデータを取得
      const generated = buildData.generated || buildData

      // ワークフロー名と説明を設定
      if (generated.name) {
        setWfTitle(generated.name)
        setDraftTitle(generated.name)
      }
      if (generated.description) {
        setWfDescription(generated.description)
      }

      // ステップデータをWorkflowStep[]へマッピング
      if (Array.isArray(generated.steps)) {
        const mappedSteps = generated.steps.map((item: any, index: number): WorkflowStep => {
          const type: WorkflowStep['type'] = item['cmd-type'] === 'branching'
            ? 'condition'
            : (index === 0 ? 'trigger' : 'action')
          // UUIDが重複している場合はインデックスを付与してユニークにする
          const baseId = item.uuid || `step-${index + 1}`
          const uniqueId = `${baseId}-${index}`
          return {
            id: String(uniqueId),
            title: String(item['cmd-nickname'] || item.cmd || `ステップ ${index + 1}`),
            description: String(item.description || ''),
            type,
            status: 'configured'
          }
        })

        console.log('mappedSteps', mappedSteps)
        if (mappedSteps.length > 0) {
          setWorkflowSteps(mappedSteps)
          setNewWorkflowViewMode('detailed')
        }
      }

      // buildDataがある場合は即座に完了状態にする
      setWorkflowCreationStep(4)
    }
  }, [location])

  useEffect(() => {
    const loadAll = async () => {
      if (!workflowId) return

      // buildDataがある場合は他のデータロードは不要
      if (hasBuildDataProcessed.current) {
        // 履歴だけは読み込む
        try {
          const res = await axios.get(`${apiBase}/workflows/${workflowId}/messages`)
          const msgs = (res.data || []) as { role: 'user' | 'assistant'; content: string }[]
          if (msgs.length > 0) setChatMessages(msgs)
        } catch {
          // noop
        }
        return
      }

      // buildDataがない場合は各種データをロード
      try {
        // ワークフロー基本情報を取得
        const wfRes = await axios.get(`${apiBase}/workflow/${workflowId}`)
        const name = wfRes.data?.name ?? ''
        setWfTitle(name)
        setDraftTitle(name)
        setWfDescription(wfRes.data?.description ?? '')

        // 会話履歴を取得
        const msgRes = await axios.get(`${apiBase}/workflows/${workflowId}/messages`)
        const msgs = (msgRes.data || []) as { role: 'user' | 'assistant'; content: string }[]
        if (msgs.length > 0) setChatMessages(msgs)

        // 生成済みステップを取得
        const latestRes = await axios.get(`${apiBase}/workflow/${workflowId}/latest`)
        const generated = latestRes.data?.generated
        const steps = generated?.steps || []

        // ワークフロー情報を更新（生成されたものがあれば上書き）
        if (generated?.name) {
          setWfTitle(generated.name)
          setDraftTitle(generated.name)
        }
        if (generated?.description) {
          setWfDescription(generated.description)
        }

        // ステップデータをWorkflowStep[]へマッピング
        const mappedSteps = (steps as any[]).map((item, index): WorkflowStep => {
          const type: WorkflowStep['type'] = item['cmd-type'] === 'branching'
            ? 'condition'
            : (index === 0 ? 'trigger' : 'action')
          // UUIDが重複している場合はインデックスを付与してユニークにする
          const baseId = item.uuid || `sv-${index + 1}`
          const uniqueId = `${baseId}-${index}`
          return {
            id: String(uniqueId),
            title: String(item['cmd-nickname'] || item.cmd || `ステップ ${index + 1}`),
            description: String(item.description || ''),
            type,
            status: 'configured'
          }
        })

        if (mappedSteps.length > 0) {
          setWorkflowSteps(mappedSteps)
          setNewWorkflowViewMode('detailed')
        }

        // データロード完了後に完了状態にする
        setWorkflowCreationStep(4)
      } catch {
        // エラー時も完了状態にして画面を表示
        setWorkflowCreationStep(4)
      }
    }

    // 少し遅延させてからロードを開始（ローディング画面を表示するため）
    const timer = setTimeout(() => {
      loadAll()
    }, 500)

    return () => clearTimeout(timer)
  }, [apiBase, workflowId])

  // リサイズのハンドリング
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return

      const newWidth = window.innerWidth - e.clientX
      if (newWidth >= MIN_WIDTH && newWidth <= MAX_WIDTH) {
        setAssistantWidth(newWidth)
      }
    }

    const handleMouseUp = () => {
      setIsResizing(false)
      document.body.style.userSelect = ''
      document.body.style.cursor = ''
    }

    if (isResizing) {
      document.body.style.userSelect = 'none'
      document.body.style.cursor = 'col-resize'
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isResizing])

  // チャットメッセージのスクロール
  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight
    }
  }, [chatMessages])

  // アシスタントへのメッセージ送信
  const handleAssistantSend = async () => {
    if (!assistantInput.trim() || !workflowId || assistantLoading) return

    const userMsg = { role: 'user' as const, content: assistantInput.trim() }
    const nextMessages = [...chatMessages, userMsg]
    setChatMessages(nextMessages)
    setAssistantInput('')

    // テキストエリアの高さをリセット
    if (assistantTextareaRef.current) {
      assistantTextareaRef.current.style.height = '40px'
    }

    setAssistantLoading(true)
    try {
      const url = `${apiBase}/ai-chat/${workflowId}`
      const res = await axios.post(url, { messages: nextMessages })
      const reply: string = res.data?.reply ?? ''
      setChatMessages([...nextMessages, { role: 'assistant', content: reply }])
    } catch {
      setChatMessages([...nextMessages, {
        role: 'assistant',
        content: 'エラーが発生しました。時間をおいて再試行してください。'
      }])
    } finally {
      setAssistantLoading(false)
    }
  }

  // キーボードショートカットのハンドリング
  const handleAssistantKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault()
      if (!assistantLoading) {
        void handleAssistantSend()
      }
    }
  }

  // テキストエリアの高さ自動調整
  const handleAssistantInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setAssistantInput(e.target.value)
    if (assistantTextareaRef.current) {
      assistantTextareaRef.current.style.height = 'auto'
      const h = Math.min(assistantTextareaRef.current.scrollHeight, 120)
      assistantTextareaRef.current.style.height = `${h}px`
    }
  }

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

  // ワークフローを再ビルドする関数（2段階API呼び出し）
  const handleRebuild = async () => {
    if (!workflowId) return
    setIsRebuilding(true)
    try {
      // ステップ1: ベクトル検索で候補を取得
      const searchRes = await axios.get(`${apiBase}/workflow/${workflowId}/search`)
      console.log('検索結果:', searchRes.data)
      
      // 検索結果の検証
      if (!searchRes.data || !Array.isArray(searchRes.data.allowed_tool_names)) {
        throw new Error(`検索結果が不正です: allowed_tool_names=${searchRes.data?.allowed_tool_names}`)
      }
      
      // ステップ2: MCP エージェントでワークフロー生成（検索結果を渡す）
      const buildPayload = {
        allowed_tool_names: searchRes.data.allowed_tool_names || [],
        hearing_text: searchRes.data.hearing_text || ''
      }
      console.log('=== ビルドリクエスト詳細 ===')
      console.log('buildPayload:', buildPayload)
      console.log('allowed_tool_names type:', typeof buildPayload.allowed_tool_names)
      console.log('allowed_tool_names isArray:', Array.isArray(buildPayload.allowed_tool_names))
      console.log('allowed_tool_names length:', buildPayload.allowed_tool_names?.length)
      console.log('hearing_text type:', typeof buildPayload.hearing_text)
      console.log('hearing_text length:', buildPayload.hearing_text?.length)
      console.log('JSON stringify:', JSON.stringify(buildPayload, null, 2))
      
      // payloadが正しいか最終確認
      if (!buildPayload.allowed_tool_names || !Array.isArray(buildPayload.allowed_tool_names)) {
        throw new Error('allowed_tool_names が配列ではありません')
      }
      
      const buildRes = await axios.post(`${apiBase}/workflow/${workflowId}/build`, buildPayload)
      const buildData = buildRes.data
      const generated = buildData.generated || buildData

      // ワークフロー名と説明を更新
      if (generated.name) {
        setWfTitle(generated.name)
        setDraftTitle(generated.name)
      }
      if (generated.description) {
        setWfDescription(generated.description)
      }

      // ステップデータを更新
      if (Array.isArray(generated.steps)) {
        const mappedSteps = generated.steps.map((item: any, index: number): WorkflowStep => {
          const type: WorkflowStep['type'] = item['cmd-type'] === 'branching'
            ? 'condition'
            : (index === 0 ? 'trigger' : 'action')
          const baseId = item.uuid || `rebuild-${index + 1}`
          const uniqueId = `${baseId}-${index}`
          return {
            id: String(uniqueId),
            title: String(item['cmd-nickname'] || item.cmd || `ステップ ${index + 1}`),
            description: String(item.description || ''),
            type,
            status: 'configured'
          }
        })

        if (mappedSteps.length > 0) {
          setWorkflowSteps(mappedSteps)
          setNewWorkflowViewMode('detailed')
        }
      }
    } catch (error: any) {
      console.error('ワークフロー再ビルドエラー:', error)
      console.error('エラーレスポンス:', error.response?.data)
      const errorMsg = error.response?.data?.detail || error.message || 'ワークフローの再生成に失敗しました。'
      alert(`エラー: ${errorMsg}`)
    } finally {
      setIsRebuilding(false)
    }
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
    {/* メインコンテンツエリア - アシスタント幅に応じてマージンを調整 */}
    <div style={{ marginRight: `${assistantWidth}px` }}>
      <PageLayout
      title={
        <div className="flex items-center gap-2">
          {!isEditingTitle ? (
            <>
              <span>{wfTitle || 'ワークフロー編集'}</span>
              <button
                className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground"
                onClick={() => setIsEditingTitle(true)}
                aria-label="タイトルを編集"
              >
                <Pencil className="h-4 w-4" />
              </button>
            </>
          ) : (
            <div className="flex items-center gap-2">
              <Input
                value={draftTitle}
                onChange={(e) => setDraftTitle(e.target.value)}
                className="h-8 w-80"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    const next = draftTitle.trim()
                    setWfTitle(next)
                    setIsEditingTitle(false)
                  } else if (e.key === 'Escape') {
                    setDraftTitle(wfTitle)
                    setIsEditingTitle(false)
                  }
                }}
              />
              <Button
                size="sm"
                onClick={() => {
                  void (async () => {
                    const next = draftTitle.trim()
                    setWfTitle(next)
                    setIsEditingTitle(false)
                    if (workflowId) {
                      try {
                        await axios.patch(`${apiBase}/workflow/${workflowId}`, { name: next })
                      } catch {}
                    }
                  })()
                }}
              >
                保存
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => {
                  setDraftTitle(wfTitle)
                  setIsEditingTitle(false)
                }}
              >
                キャンセル
              </Button>
            </div>
          )}
        </div>
      }
      description={wfDescription || ''}
      maxWidth="full"
      className="pr-80"
    >
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
                    <Button
                      variant="outline"
                      onClick={handleRebuild}
                      disabled={isRebuilding}
                    >
                      {isRebuilding ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          再生成中...
                        </>
                      ) : (
                        <>
                          <RefreshCw className="h-4 w-4 mr-2" />
                          ワークフローを再生成
                        </>
                      )}
                    </Button>
                    <Button variant="outline">
                      <TestTube className="h-4 w-4 mr-2" />
                      テスト実行
                    </Button>
                    <Button
                      onClick={async () => {
                        if (!workflowId) return
                        try {
                          // タイトルも保存
                          const name = (wfTitle || draftTitle).trim()
                          if (name) {
                            await axios.patch(`${apiBase}/workflow/${workflowId}`, { name })
                          }
                          // icon は送信しない（表示用）
                          const groups = generatedGroups.map(({ icon, ...rest }) => rest)
                          const steps = workflowSteps.map(({ icon, ...rest }) => rest)
                          await axios.post(`${apiBase}/workflow/${workflowId}/save`, { groups, steps })
                          window.alert('ワークフローを保存しました。')
                        } catch (e) {
                          window.alert('ワークフローの保存に失敗しました。')
                        }
                      }}
                    >
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
    </div>

    {/* リサイズ可能なハンドル */}
    <div
      className="fixed top-0 bottom-0 w-1 cursor-col-resize hover:bg-primary/20 active:bg-primary/30 z-50 transition-colors"
      style={{ right: `${assistantWidth - 2}px` }}
      onMouseDown={(e) => {
        e.preventDefault()
        setIsResizing(true)
      }}
    >
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-0.5 h-8 bg-border rounded-full" />
      </div>
    </div>

    {/* リサイズ可能な右側AIアシスタント（画面最上部〜最下部） */}
    <div
      ref={assistantRef}
      className="fixed right-0 top-0 bottom-0 border-l bg-muted/10 flex flex-col transition-none"
      style={{ width: `${assistantWidth}px` }}>
      <div className="p-4 border-b">
        <h3 className="font-semibold flex items-center">
          <Bot className="h-4 w-4 mr-2" />
          ワークフローアシスタント
        </h3>
      </div>
      <div ref={chatScrollRef} className="flex-1 overflow-y-auto p-4 space-y-3">
        {chatMessages.length === 0 && (
          <div className="text-center text-sm text-muted-foreground mt-8">
            <p>ワークフローについて何かお手伝いできることはありますか？</p>
            <p className="mt-2">例: ステップの追加、修正、最適化など</p>
          </div>
        )}
        {chatMessages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-lg px-3 py-2 ${
                message.role === 'user'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted'
              }`}
            >
              <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
            </div>
          </div>
        ))}
        {assistantLoading && (
          <div className="flex justify-start">
            <div className="max-w-[85%] rounded-lg px-3 py-2 bg-muted">
              <div className="flex items-center space-x-2">
                <Loader2 className="h-3 w-3 animate-spin" />
                <span className="text-sm text-muted-foreground">考え中...</span>
              </div>
            </div>
          </div>
        )}
      </div>
      <div className="p-3 border-t bg-card">
        <div className="relative">
          <Textarea
            ref={assistantTextareaRef}
            value={assistantInput}
            onChange={handleAssistantInputChange}
            onKeyDown={handleAssistantKeyDown}
            placeholder="メッセージを入力... (Ctrl+Enterで送信)"
            className="w-full rounded-md border border-input bg-background px-3 py-2 pr-12 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50 resize-none overflow-y-auto"
            rows={1}
            style={{ height: '40px', minHeight: '40px', maxHeight: '120px' }}
            disabled={assistantLoading}
          />
          <Button
            onClick={handleAssistantSend}
            disabled={!assistantInput.trim() || assistantLoading}
            size="icon"
            className="absolute right-1 bottom-1 h-8 w-8"
          >
            {assistantLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
    </>
  )
}


