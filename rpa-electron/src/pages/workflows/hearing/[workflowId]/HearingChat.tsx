import { useEffect, useRef, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Send } from 'lucide-react'
import axios from 'axios'
import { Textarea } from '@/components/ui/textarea'

type ChatMessage = {
  role: 'user' | 'assistant'
  content: string
}

function TypingDots() {
  const [dots, setDots] = useState(1)
  useEffect(() => {
    const id = setInterval(() => setDots((d) => (d % 3) + 1), 400)
    return () => clearInterval(id)
  }, [])
  return <span className="text-gray-800 font-bold" aria-label="生成中">{'・'.repeat(dots)}</span>
}

export default function HearingChat() {
  const { workflowId } = useParams()
  const navigate = useNavigate()
  const location = useLocation() as any
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement | null>(null)
  const apiBase = (import.meta as any).env?.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
  const hasInitialFromNav = useRef(false)

  // 初回遷移時: Hearingからの初期メッセージがあれば表示して即実行
  useEffect(() => {
    const init = location?.state?.initialMessages as ChatMessage[] | undefined
    if (init && init.length > 0) {
      hasInitialFromNav.current = true
      setChatMessages(init)
      // 画面遷移後に初回のAI応答を取得
      if (workflowId) {
        void fetchAssistant(init)
      }
    }
  }, [location, workflowId])

  // 履歴のロード
  useEffect(() => {
    const loadHistory = async () => {
      if (!workflowId) return
      // 直前の画面から初期メッセージで実行中の場合は履歴ロードをスキップ
      if (hasInitialFromNav.current) return
      try {
        const res = await axios.get(`${apiBase}/workflows/${workflowId}/messages`)
        const msgs = (res.data || []) as { role: 'user' | 'assistant'; content: string }[]
        if (msgs.length > 0) {
          setChatMessages(msgs.map(m => ({ role: m.role, content: m.content })))
        }
      } catch {
        // noop
      }
    }
    loadHistory()
  }, [apiBase, workflowId])

  const fetchAssistant = async (messages: ChatMessage[]) => {
    setLoading(true)
    try {
      const url = `${apiBase}/ai-chat/${workflowId}`
      const res = await axios.post(url, { messages })
      const reply: string = res.data?.reply ?? ''
      setChatMessages([...messages, { role: 'assistant', content: reply }])
    } catch {
      setChatMessages([...messages, { role: 'assistant', content: 'エラーが発生しました。時間をおいて再試行してください。' }])
    } finally {
      setLoading(false)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || !workflowId) return
    const userMsg: ChatMessage = { role: 'user', content: input.trim() }
    const nextMessages = [...chatMessages, userMsg]
    setChatMessages(nextMessages)
    setInput('')
    await fetchAssistant(nextMessages)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault()
      if (!loading) {
        void handleSend()
      }
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      const h = Math.min(textareaRef.current.scrollHeight, 240)
      textareaRef.current.style.height = `${h}px`
    }
  }

  return (
    <main className="h-[calc(100vh-1rem)] overflow-hidden">
      <div className="flex-1 flex flex-col max-w-4xl mx-auto h-full">
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="space-y-4 mb-6">
            {chatMessages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] p-4 rounded-lg ${
                    message.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="max-w-[70%] py-2 px-4 rounded-lg bg-muted text-muted-foreground">
                  <TypingDots />
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="border-t border-slate-200 p-4">
          <div className="relative">
            <Textarea
              ref={textareaRef}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="メッセージを入力... (Ctrl+Enterで送信)"
              className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 pr-12 text-sm placeholder:text-slate-400 focus:outline-none focus:border-slate-400 focus:ring-1 focus:ring-slate-400 disabled:cursor-not-allowed disabled:opacity-50 resize-none overflow-y-auto"
              rows={1}
              style={{ height: '40px', minHeight: '40px', maxHeight: '240px' }}
              disabled={loading}
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              size="icon"
              className="absolute right-1 bottom-1 h-8 w-8 rounded-md"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* 下部のグローバルな"生成中..."はバブルのドットに置換 */}
        <div className="p-4">
          <div className="flex justify-center">
            <Button
              size="lg"
              className="px-8"
              disabled={loading}
              onClick={async () => {
                if (!workflowId) return
                try {
                  await axios.post(`${apiBase}/workflow/${workflowId}/build`)
                } catch {}
                navigate(`/workflows/edit/${workflowId}`)
              }}
            >
              ワークフロー作成
            </Button>
          </div>
        </div>
      </div>
    </main>
  )
}
