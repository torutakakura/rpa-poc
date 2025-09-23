import { useState } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { ArrowRight, Send, Workflow as WorkflowIcon } from 'lucide-react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

type ChatMessage = {
  role: 'user' | 'assistant'
  content: string
}

export default function Hearing() {
  const [workflowCreationStep, setWorkflowCreationStep] = useState<1 | 2>(1)
  const [workflowPrompt, setWorkflowPrompt] = useState('')
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [chatInput, setChatInput] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [chatLoading, setChatLoading] = useState(false)

  const apiBase = (import.meta as any).env?.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
  const navigate = useNavigate()

  const fetchAssistant = async (messages: ChatMessage[]) => {
    setChatLoading(true)
    try {
      const res = await axios.post(`${apiBase}/ai-chat`, { messages })
      const reply: string = res.data?.reply ?? ''
      const workflowId: string | undefined = res.data?.workflow_id
      const initialMessages: ChatMessage[] = [...messages, { role: 'assistant', content: reply }]
      if (workflowId) {
        navigate(`/workflows/hearing/${workflowId}`, { state: { initialMessages } })
      } else {
        setChatMessages(initialMessages)
      }
    } finally {
      setChatLoading(false)
    }
  }

  const handlePromptSubmit = async () => {
    if (!workflowPrompt.trim()) return
    // 初回: /ai-chat を呼び、返信とworkflow_idを受け取ってチャット画面へ遷移
    const initialUser: ChatMessage = { role: 'user', content: workflowPrompt.trim() }
    await fetchAssistant([initialUser])
  }

  return (
    <main className="h-[calc(100vh-1rem)] overflow-hidden">
      <div className="flex h-full">
        <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-background to-muted/20">
          <div className="text-center space-y-8 max-w-2xl mx-auto px-6">
            <div className="space-y-4">
              <h1 className="text-4xl font-bold tracking-tight">RPA Manager</h1>
              <p className="text-xl text-muted-foreground">作成したいワークフローを説明してください</p>
            </div>

            <div className="space-y-4">
              <div className="relative">
                <Input
                  placeholder="例：電子帳簿保存のワークフローを作成して"
                  value={workflowPrompt}
                  onChange={(e) => setWorkflowPrompt(e.target.value)}
                  className="text-lg py-6 px-4 bg-card border-2"
                  onKeyPress={(e) => e.key === 'Enter' && handlePromptSubmit()}
                />
                <Button
                  className="absolute right-2 top-1/2 -translate-y-1/2"
                  onClick={handlePromptSubmit}
                  disabled={!workflowPrompt.trim()}
                >
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </div>

              <div className="flex flex-wrap gap-2 justify-center">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setWorkflowPrompt('電子帳簿保存のワークフローを作成して')}
                >
                  電子帳簿保存
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setWorkflowPrompt('請求書処理の自動化ワークフローを作成して')}
                >
                  請求書処理
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setWorkflowPrompt('顧客データ管理のワークフローを作成して')}
                >
                  顧客データ管理
                </Button>
              </div>
            </div>
          </div>
        </div>
        </div>
    </main>
  )
}


