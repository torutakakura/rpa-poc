import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Plus, Search, Play, Edit, Trash2, Copy } from 'lucide-react'
import { PageLayout } from '@/components/layout/PageLayout'

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
  
  const workflows: Workflow[] = [
    {
      id: '1',
      name: '日次レポート生成',
      description: '売上データを集計してレポートを自動生成',
      lastRun: '2時間前',
      status: 'active',
      runs: 245
    },
    {
      id: '2',
      name: 'メール自動送信',
      description: '定期的なお知らせメールを自動送信',
      lastRun: '5時間前',
      status: 'active',
      runs: 189
    },
    {
      id: '3',
      name: 'データバックアップ',
      description: '重要データの定期バックアップ',
      lastRun: '1日前',
      status: 'inactive',
      runs: 67
    },
    {
      id: '4',
      name: 'Webスクレイピング',
      description: '競合サイトの価格情報を収集',
      lastRun: '3日前',
      status: 'error',
      runs: 342
    }
  ]

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
    <PageLayout
      title="ワークフロー"
      description="自動化ワークフローの作成と管理"
      action={
        <Button className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          新規作成
        </Button>
      }
    >

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
                  <Button size="sm" variant="outline" className="flex-1">
                    <Edit className="h-3 w-3 mr-1" />
                    編集
                  </Button>
                  <Button size="sm" variant="outline">
                    <Copy className="h-3 w-3" />
                  </Button>
                  <Button size="sm" variant="outline">
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
  )
}
