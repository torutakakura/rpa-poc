import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Activity, Clock, CheckCircle2, AlertCircle } from 'lucide-react'
import { PageLayout } from '@/components/layout/PageLayout'

export default function Dashboard() {
  const stats = [
    {
      title: '実行中のワークフロー',
      value: '3',
      description: '現在実行中',
      icon: Activity,
      color: 'text-blue-500'
    },
    {
      title: '今日の実行回数',
      value: '24',
      description: '過去24時間',
      icon: Clock,
      color: 'text-orange-500'
    },
    {
      title: '成功率',
      value: '98.5%',
      description: '過去7日間',
      icon: CheckCircle2,
      color: 'text-green-500'
    },
    {
      title: 'エラー件数',
      value: '2',
      description: '要確認',
      icon: AlertCircle,
      color: 'text-red-500'
    }
  ]

  return (
    <PageLayout
      title="ダッシュボード"
      description="RPAワークフローの実行状況を一覧で確認できます"
    >

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-gray-500 mt-1">{stat.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="h-full">
          <CardHeader className="border-b">
            <CardTitle className="text-lg">最近の実行履歴</CardTitle>
            <CardDescription className="text-sm">直近10件の実行結果</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map(i => (
                <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <div className="flex items-center space-x-3">
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                    <div>
                      <p className="text-sm font-medium">ワークフロー {i}</p>
                      <p className="text-xs text-gray-500">10分前</p>
                    </div>
                  </div>
                  <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded">成功</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="h-full">
          <CardHeader className="border-b">
            <CardTitle className="text-lg">スケジュール実行予定</CardTitle>
            <CardDescription className="text-sm">次回実行予定のワークフロー</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <div>
                    <p className="text-sm font-medium">定期実行タスク {i}</p>
                    <p className="text-xs text-gray-500">毎日 {9 + i}:00</p>
                  </div>
                  <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                    {i === 1 ? '1時間後' : `${i}時間後`}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </PageLayout>
  )
}
