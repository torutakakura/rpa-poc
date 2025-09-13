import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Search, Filter, Download, Eye, CheckCircle2, XCircle, Clock, AlertCircle } from 'lucide-react'
import { PageLayout } from '@/components/layout/PageLayout'

interface ExecutionHistory {
  id: string
  workflowName: string
  startTime: string
  endTime: string
  duration: string
  status: 'success' | 'failed' | 'running' | 'warning'
  trigger: string
  logs?: string
}

export default function Histories() {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  
  const histories: ExecutionHistory[] = [
    {
      id: '1',
      workflowName: '日次レポート生成',
      startTime: '2024-01-10 09:00:00',
      endTime: '2024-01-10 09:02:15',
      duration: '2分15秒',
      status: 'success',
      trigger: 'スケジュール'
    },
    {
      id: '2',
      workflowName: 'データ同期',
      startTime: '2024-01-10 08:30:00',
      endTime: '2024-01-10 08:31:45',
      duration: '1分45秒',
      status: 'success',
      trigger: 'スケジュール'
    },
    {
      id: '3',
      workflowName: 'メール自動送信',
      startTime: '2024-01-10 08:00:00',
      endTime: '2024-01-10 08:00:30',
      duration: '30秒',
      status: 'failed',
      trigger: '手動実行'
    },
    {
      id: '4',
      workflowName: 'Webスクレイピング',
      startTime: '2024-01-10 07:45:00',
      endTime: '-',
      duration: '実行中',
      status: 'running',
      trigger: 'API'
    },
    {
      id: '5',
      workflowName: 'データバックアップ',
      startTime: '2024-01-10 06:00:00',
      endTime: '2024-01-10 06:05:00',
      duration: '5分',
      status: 'warning',
      trigger: 'スケジュール'
    }
  ]

  const filteredHistories = histories.filter(history => {
    const matchesSearch = history.workflowName.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || history.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'running':
        return <Clock className="h-4 w-4 text-blue-500 animate-spin" />
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />
      default:
        return null
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'success':
        return '成功'
      case 'failed':
        return '失敗'
      case 'running':
        return '実行中'
      case 'warning':
        return '警告'
      default:
        return '不明'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'bg-green-100 text-green-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      case 'running':
        return 'bg-blue-100 text-blue-800'
      case 'warning':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <PageLayout
      title="実行履歴"
      description="ワークフローの実行ログと結果を確認"
      action={
        <Button variant="outline" className="flex items-center gap-2">
          <Download className="h-4 w-4" />
          エクスポート
        </Button>
      }
    >

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">総実行回数</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">1,234</p>
            <p className="text-xs text-gray-500 mt-1">過去30日間</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">成功率</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-green-600">98.5%</p>
            <p className="text-xs text-gray-500 mt-1">過去30日間</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">平均実行時間</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">2分30秒</p>
            <p className="text-xs text-gray-500 mt-1">全ワークフロー</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">エラー件数</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-red-600">18</p>
            <p className="text-xs text-gray-500 mt-1">過去7日間</p>
          </CardContent>
        </Card>
      </div>

      <Card className="overflow-hidden">
        <CardHeader className="border-b bg-gray-50/50">
          <CardTitle>実行履歴一覧</CardTitle>
          <CardDescription>ワークフローの実行結果を時系列で表示</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 p-4 border-b bg-white">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                type="text"
                placeholder="ワークフロー名で検索..."
                className="pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-[180px]">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="ステータス" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">すべて</SelectItem>
                <SelectItem value="success">成功</SelectItem>
                <SelectItem value="failed">失敗</SelectItem>
                <SelectItem value="running">実行中</SelectItem>
                <SelectItem value="warning">警告</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr className="text-left">
                  <th className="px-4 py-3 font-medium text-xs uppercase tracking-wider text-gray-700">ステータス</th>
                  <th className="px-4 py-3 font-medium text-xs uppercase tracking-wider text-gray-700">ワークフロー</th>
                  <th className="px-4 py-3 font-medium text-xs uppercase tracking-wider text-gray-700">開始時刻</th>
                  <th className="px-4 py-3 font-medium text-xs uppercase tracking-wider text-gray-700">終了時刻</th>
                  <th className="px-4 py-3 font-medium text-xs uppercase tracking-wider text-gray-700">実行時間</th>
                  <th className="px-4 py-3 font-medium text-xs uppercase tracking-wider text-gray-700">トリガー</th>
                  <th className="px-4 py-3 font-medium text-xs uppercase tracking-wider text-gray-700">操作</th>
                </tr>
              </thead>
              <tbody>
                {filteredHistories.map((history) => (
                  <tr key={history.id} className="border-b hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(history.status)}
                        <span className={`text-xs px-2 py-1 rounded ${getStatusColor(history.status)}`}>
                          {getStatusText(history.status)}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 font-medium">{history.workflowName}</td>
                    <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{history.startTime}</td>
                    <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{history.endTime}</td>
                    <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{history.duration}</td>
                    <td className="px-4 py-3">
                      <span className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">
                        {history.trigger}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <Button size="sm" variant="ghost">
                        <Eye className="h-4 w-4" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredHistories.length === 0 && (
            <div className="text-center py-12 px-4">
              <p className="text-gray-500">検索条件に一致する履歴が見つかりません</p>
            </div>
          )}
        </CardContent>
      </Card>
    </PageLayout>
  )
}
