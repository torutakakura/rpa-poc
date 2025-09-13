import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Calendar, Clock, Plus, Edit, Trash2, Repeat } from 'lucide-react'
import { Switch } from '@/components/ui/switch'
import { PageLayout } from '@/components/layout/PageLayout'

interface Schedule {
  id: string
  workflowName: string
  cronExpression: string
  nextRun: string
  lastRun: string
  enabled: boolean
  frequency: string
}

export default function Schedules() {
  const [schedules, setSchedules] = useState<Schedule[]>([
    {
      id: '1',
      workflowName: '日次レポート生成',
      cronExpression: '0 9 * * *',
      nextRun: '明日 9:00',
      lastRun: '今日 9:00',
      enabled: true,
      frequency: '毎日'
    },
    {
      id: '2',
      workflowName: '週次バックアップ',
      cronExpression: '0 0 * * 0',
      nextRun: '日曜日 0:00',
      lastRun: '先週日曜日',
      enabled: true,
      frequency: '毎週'
    },
    {
      id: '3',
      workflowName: '月次集計',
      cronExpression: '0 0 1 * *',
      nextRun: '来月1日',
      lastRun: '今月1日',
      enabled: false,
      frequency: '毎月'
    },
    {
      id: '4',
      workflowName: 'データ同期',
      cronExpression: '*/30 * * * *',
      nextRun: '30分後',
      lastRun: '5分前',
      enabled: true,
      frequency: '30分ごと'
    }
  ])

  const toggleSchedule = (id: string) => {
    setSchedules(schedules.map(schedule =>
      schedule.id === id ? { ...schedule, enabled: !schedule.enabled } : schedule
    ))
  }

  const getFrequencyIcon = (frequency: string) => {
    if (frequency.includes('分')) return Clock
    if (frequency === '毎日') return Calendar
    return Repeat
  }

  return (
    <PageLayout
      title="スケジュール"
      description="ワークフローの定期実行を管理"
      action={
        <Button className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          スケジュール追加
        </Button>
      }
    >

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="h-full">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg">実行予定カレンダー</CardTitle>
            <CardDescription className="text-sm">今後24時間の実行予定</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {['9:00', '12:00', '15:00', '18:00', '21:00'].map((time, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <div className="flex items-center gap-3">
                    <Clock className="h-4 w-4 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium">{time}</p>
                      <p className="text-xs text-gray-500">ワークフロー {index + 1}</p>
                    </div>
                  </div>
                  <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                    {index === 0 ? '次回実行' : `${index * 3}時間後`}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="h-full">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg">スケジュール統計</CardTitle>
            <CardDescription className="text-sm">実行頻度の概要</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50">
                <span className="text-sm text-gray-600">有効なスケジュール</span>
                <span className="text-xl font-bold text-green-600">
                  {schedules.filter(s => s.enabled).length}
                </span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50">
                <span className="text-sm text-gray-600">無効なスケジュール</span>
                <span className="text-xl font-bold text-gray-400">
                  {schedules.filter(s => !s.enabled).length}
                </span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50">
                <span className="text-sm text-gray-600">今日の実行予定</span>
                <span className="text-xl font-bold text-blue-600">12</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50">
                <span className="text-sm text-gray-600">平均実行間隔</span>
                <span className="text-lg font-bold">2時間</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="overflow-hidden">
        <CardHeader className="border-b bg-gray-50/50">
          <CardTitle>スケジュール一覧</CardTitle>
          <CardDescription>登録されているすべてのスケジュール</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <div className="divide-y">
            {schedules.map((schedule) => {
              const Icon = getFrequencyIcon(schedule.frequency)
              return (
                <div key={schedule.id} className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 hover:bg-gray-50 transition-colors gap-4">
                  <div className="flex items-center gap-4 flex-1">
                    <Switch
                      checked={schedule.enabled}
                      onCheckedChange={() => toggleSchedule(schedule.id)}
                    />
                    <div className="flex items-center gap-3 flex-1">
                      <Icon className={`h-5 w-5 ${schedule.enabled ? 'text-blue-500' : 'text-gray-400'}`} />
                      <div className="min-w-0 flex-1">
                        <p className={`font-medium truncate ${!schedule.enabled && 'text-gray-400'}`}>
                          {schedule.workflowName}
                        </p>
                        <div className="flex flex-wrap items-center gap-2 sm:gap-4 mt-1">
                          <span className="text-xs text-gray-500">
                            {schedule.frequency} • {schedule.cronExpression}
                          </span>
                          <span className="text-xs text-gray-500 whitespace-nowrap">
                            次回: {schedule.nextRun}
                          </span>
                          <span className="text-xs text-gray-500 whitespace-nowrap">
                            前回: {schedule.lastRun}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button size="sm" variant="ghost" className="h-8 w-8 p-0 hover:text-red-600">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </PageLayout>
  )
}
