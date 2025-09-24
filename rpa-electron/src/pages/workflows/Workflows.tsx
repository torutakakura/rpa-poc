import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useNavigate } from 'react-router-dom'
import { Input } from '@/components/ui/input'
import { Plus, Search, Play, Edit, Trash2 } from 'lucide-react'
import { PageLayout } from '@/components/layout/PageLayout'
import axios from 'axios'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'

interface Workflow {
  id: string
  name: string
  description: string
  lastRun: string
  status: 'active' | 'inactive' | 'error'
  runs: number
}

export default function Workflows() {
  const [searchTerm, setSearchTerm] = useState('')
  const [workflows, setWorkflows] = useState<Workflow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [targetWorkflow, setTargetWorkflow] = useState<Workflow | null>(null)

  type ApiWorkflow = {
    id: string
    name: string
    description?: string | null
    last_run_at?: string | null
    is_hearing?: boolean | null
  }

  const formatRelative = (iso?: string | null) => {
    if (!iso) return '未実行'
    const dt = new Date(iso)
    const now = new Date()
    const diffMs = now.getTime() - dt.getTime()
    const sec = Math.max(0, Math.floor(diffMs / 1000))
    const min = Math.floor(sec / 60)
    const hour = Math.floor(min / 60)
    const day = Math.floor(hour / 24)
    if (day > 0) return `${day}日前`
    if (hour > 0) return `${hour}時間前`
    if (min > 0) return `${min}分前`
    return 'たった今'
  }

  useEffect(() => {
    const fetchWorkflows = async () => {
      try {
        const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
        const res = await axios.get<ApiWorkflow[]>(`${baseURL}/workflows`)
        const mapped: Workflow[] = res.data.map(w => ({
          id: w.id,
          name: w.name,
          description: w.description ?? '',
          lastRun: formatRelative(w.last_run_at ?? null),
          status: 'active',
          runs: 0,
        }))
        setWorkflows(mapped)
      } catch (e) {
        setError('ワークフローの取得に失敗しました')
      } finally {
        setLoading(false)
      }
    }
    fetchWorkflows()
  }, [])

  const handleEdit = async (id: string) => {
    try {
      const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
      const res = await axios.get<ApiWorkflow>(`${baseURL}/workflow/${id}`)
      const isHearing = !!res.data?.is_hearing
      if (isHearing) navigate(`/workflows/hearing/${id}`)
      else navigate(`/workflows/edit/${id}`)
    } catch {
      // フォールバックとしてヒアリングへ
      navigate(`/workflows/hearing/${id}`)
    }
  }

  const handleDelete = async (id: string) => {
    try {
      setDeletingId(id)
      const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
      await axios.delete(`${baseURL}/workflows/${id}`)
      setWorkflows((prev) => prev.filter((w) => w.id !== id))
    } catch (e) {
      alert('削除に失敗しました')
    } finally {
      setDeletingId(null)
      setDeleteOpen(false)
      setTargetWorkflow(null)
    }
  }

  const filteredWorkflows = workflows.filter(workflow =>
    workflow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    workflow.description.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'inactive':
        return 'bg-gray-100 text-gray-800'
      case 'error':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return '実行中'
      case 'inactive':
        return '停止中'
      case 'error':
        return 'エラー'
      default:
        return '不明'
    }
  }

  return (
    <>
    <PageLayout
      title="ワークフロー"
      description="自動化ワークフローの作成と管理"
      action={
        <Button className="flex items-center gap-2" onClick={() => navigate('/workflows/hearing')}>
          <Plus className="h-4 w-4" />
          新規作成
        </Button>
      }
    >
      {loading && (
        <div className="text-sm text-gray-500">読み込み中...</div>
      )}
      {error && (
        <div className="text-sm text-red-600">{error}</div>
      )}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
        <Input
          type="text"
          placeholder="ワークフローを検索..."
          className="pl-10"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filteredWorkflows.map((workflow) => (
          <Card key={workflow.id} className="hover:shadow-lg transition-all hover:-translate-y-1 duration-200">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg">{workflow.name}</CardTitle>
                  <CardDescription className="mt-1">
                    {workflow.description}
                  </CardDescription>
                </div>
                <span className={`text-xs px-2 py-1 rounded ${getStatusColor(workflow.status)}`}>
                  {getStatusText(workflow.status)}
                </span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">最終実行</span>
                  <span className="font-medium">{workflow.lastRun}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">実行回数</span>
                  <span className="font-medium">{workflow.runs}回</span>
                </div>
                <div className="flex items-center gap-2 pt-3 border-t">
                  <Button size="sm" variant="outline" className="flex-1">
                    <Play className="h-3 w-3 mr-1" />
                    実行
                  </Button>
                  <Button size="sm" variant="outline" className="flex-1" onClick={() => handleEdit(workflow.id)}>
                    <Edit className="h-3 w-3 mr-1" />
                    編集
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setTargetWorkflow(workflow)
                      setDeleteOpen(true)
                    }}
                    disabled={deletingId === workflow.id}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredWorkflows.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">検索条件に一致するワークフローが見つかりません</p>
        </div>
      )}
    </PageLayout>
    <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>ワークフローを削除</DialogTitle>
          <DialogDescription>
            {targetWorkflow ? `「${targetWorkflow.name}」を削除します。よろしいですか？` : '選択されたワークフローを削除します。'}
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={() => setDeleteOpen(false)}>キャンセル</Button>
          <Button variant="destructive" onClick={() => targetWorkflow && handleDelete(targetWorkflow.id)} disabled={!!(targetWorkflow && deletingId === targetWorkflow.id)}>
            削除する
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
    </>
  )
}
