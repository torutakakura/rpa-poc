/**
 * RPA Demo Page
 * JSON-RPC over stdioのデモページ
 */

import { useState } from 'react'
import { RPADemo } from '@/components/RPADemo'
import { RPADebugInfo } from '@/components/RPADebugInfo'
import { Button } from '@/components/ui/button'
import { Bug } from 'lucide-react'

export default function RPADemoPage() {
  // 配布版では最初からデバッグパネルを表示
  const [showDebug, setShowDebug] = useState(true)

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      {/* ヘッダー */}
      <div className="flex-shrink-0 px-6 pt-6 pb-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-gray-900">
              RPA Python連携デモ
            </h1>
            <p className="mt-2 text-gray-600">
              JSON-RPC over stdioでPythonエージェントと通信
            </p>
          </div>
          <Button
            variant={showDebug ? "default" : "outline"}
            size="sm"
            onClick={() => setShowDebug(!showDebug)}
          >
            <Bug className="mr-2 h-4 w-4" />
            デバッグ
          </Button>
        </div>
      </div>

      {/* デバッグパネル（オプション） */}
      {showDebug && (
        <div className="flex-shrink-0 px-6 pb-4">
          <RPADebugInfo />
        </div>
      )}

      {/* メインコンテンツ - 残りの高さを全て使用 */}
      <div className="flex-1 overflow-hidden">
        <RPADemo />
      </div>
    </div>
  )
}
