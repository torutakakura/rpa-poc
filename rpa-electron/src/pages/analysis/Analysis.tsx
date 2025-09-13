import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { TrendingUp, TrendingDown, Activity, BarChart3, PieChart, Clock, Target, Zap } from 'lucide-react'
import { PageLayout } from '@/components/layout/PageLayout'

export default function Analysis() {
  const performanceMetrics = [
    {
      label: '成功率',
      value: '98.5%',
      change: '+2.3%',
      trend: 'up',
      icon: Target,
      color: 'text-green-500'
    },
    {
      label: '平均実行時間',
      value: '2分30秒',
      change: '-15秒',
      trend: 'up',
      icon: Clock,
      color: 'text-blue-500'
    },
    {
      label: '処理効率',
      value: '87%',
      change: '+5%',
      trend: 'up',
      icon: Zap,
      color: 'text-purple-500'
    },
    {
      label: 'エラー率',
      value: '1.5%',
      change: '-0.8%',
      trend: 'down',
      icon: Activity,
      color: 'text-orange-500'
    }
  ]

  const topWorkflows = [
    { name: '日次レポート生成', runs: 245, successRate: 99.2 },
    { name: 'データ同期', runs: 189, successRate: 98.9 },
    { name: 'メール自動送信', runs: 156, successRate: 97.4 },
    { name: 'Webスクレイピング', runs: 142, successRate: 95.8 },
    { name: 'データバックアップ', runs: 98, successRate: 100 }
  ]

  return (
    <PageLayout
      title="分析"
      description="ワークフローのパフォーマンスと効率性を分析"
      action={
        <Select defaultValue="week">
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="期間を選択" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="day">過去24時間</SelectItem>
            <SelectItem value="week">過去7日間</SelectItem>
            <SelectItem value="month">過去30日間</SelectItem>
            <SelectItem value="quarter">過去3ヶ月</SelectItem>
          </SelectContent>
        </Select>
      }
    >

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {performanceMetrics.map((metric, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {metric.label}
              </CardTitle>
              <metric.icon className={`h-4 w-4 ${metric.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metric.value}</div>
              <div className="flex items-center mt-1">
                {metric.trend === 'up' ? (
                  <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
                )}
                <span className={`text-xs ${metric.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                  {metric.change}
                </span>
                <span className="text-xs text-gray-500 ml-1">前期比</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>実行頻度グラフ</CardTitle>
            <CardDescription>時間帯別の実行回数</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {['00-06時', '06-12時', '12-18時', '18-24時'].map((timeRange, index) => {
                const percentage = [25, 40, 30, 5][index]
                return (
                  <div key={index}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-gray-600">{timeRange}</span>
                      <span className="text-sm font-medium">{percentage * 10}回</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>カテゴリ別実行割合</CardTitle>
            <CardDescription>ワークフローの種類別統計</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center h-[200px]">
              <div className="relative">
                <PieChart className="h-32 w-32 text-gray-200" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <p className="text-2xl font-bold">1,234</p>
                    <p className="text-xs text-gray-500">総実行回数</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4 mt-4">
              {[
                { label: 'データ処理', value: '35%', color: 'bg-blue-500' },
                { label: 'レポート生成', value: '25%', color: 'bg-green-500' },
                { label: '通知・連携', value: '20%', color: 'bg-yellow-500' },
                { label: 'その他', value: '20%', color: 'bg-gray-500' }
              ].map((item, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${item.color}`} />
                  <div>
                    <p className="text-xs text-gray-600">{item.label}</p>
                    <p className="text-sm font-medium">{item.value}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>実行回数ランキング</CardTitle>
          <CardDescription>最も頻繁に実行されているワークフロー</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {topWorkflows.map((workflow, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-100 text-sm font-medium">
                    {index + 1}
                  </div>
                  <div>
                    <p className="font-medium">{workflow.name}</p>
                    <p className="text-xs text-gray-500">成功率: {workflow.successRate}%</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-medium">{workflow.runs}回</p>
                  <div className="flex items-center gap-1 mt-1">
                    <BarChart3 className="h-3 w-3 text-gray-400" />
                    <div className="w-20 bg-gray-200 rounded-full h-1.5">
                      <div
                        className="bg-blue-500 h-1.5 rounded-full"
                        style={{ width: `${(workflow.runs / 245) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <Card>
          <CardHeader>
            <CardTitle>パフォーマンストレンド</CardTitle>
            <CardDescription>過去7日間の推移</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="text-sm text-gray-600">改善したワークフロー</span>
                <div className="flex items-center gap-2">
                  <span className="font-medium">12個</span>
                  <TrendingUp className="h-4 w-4 text-green-500" />
                </div>
              </div>
              <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                <span className="text-sm text-gray-600">悪化したワークフロー</span>
                <div className="flex items-center gap-2">
                  <span className="font-medium">3個</span>
                  <TrendingDown className="h-4 w-4 text-red-500" />
                </div>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-600">変化なし</span>
                <span className="font-medium">8個</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>推奨アクション</CardTitle>
            <CardDescription>パフォーマンス改善の提案</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="p-3 bg-yellow-50 rounded-lg">
                <p className="text-sm font-medium text-yellow-900">最適化の機会</p>
                <p className="text-xs text-yellow-700 mt-1">
                  「Webスクレイピング」の実行時間が平均より30%長くなっています
                </p>
              </div>
              <div className="p-3 bg-blue-50 rounded-lg">
                <p className="text-sm font-medium text-blue-900">スケジュール調整</p>
                <p className="text-xs text-blue-700 mt-1">
                  9:00-10:00の時間帯に実行が集中しています。分散を検討してください
                </p>
              </div>
              <div className="p-3 bg-green-50 rounded-lg">
                <p className="text-sm font-medium text-green-900">成功事例</p>
                <p className="text-xs text-green-700 mt-1">
                  「データバックアップ」は100%の成功率を維持しています
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </PageLayout>
  )
}
