/**
 * RPA Demo Page
 * JSON-RPC over stdioのデモページ
 */

import { PageLayout } from '@/components/layout/PageLayout'
import { RPADemo } from '@/components/RPADemo'

export default function RPADemoPage() {
  return (
    <PageLayout
      title="RPA Python連携デモ"
      description="JSON-RPC over stdioでPythonエージェントと通信"
    >
      <RPADemo />
    </PageLayout>
  )
}
