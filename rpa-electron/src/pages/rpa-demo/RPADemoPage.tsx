/**
 * RPA Demo Page
 * JSON-RPC over stdioのデモページ
 */

import { RPADemo } from '@/components/RPADemo'

export default function RPADemoPage() {
  return (
    <div className="h-screen flex flex-col overflow-hidden">
      {/* ヘッダー */}
      <div className="flex-shrink-0 px-6 pt-6 pb-4">
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">
          RPA Python連携デモ
        </h1>
        <p className="mt-2 text-gray-600">
          JSON-RPC over stdioでPythonエージェントと通信
        </p>
      </div>

      {/* メインコンテンツ - 残りの高さを全て使用 */}
      <div className="flex-1 overflow-hidden">
        <RPADemo />
      </div>
    </div>
  )
}
