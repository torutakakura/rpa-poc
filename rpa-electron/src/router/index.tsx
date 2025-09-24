import { Routes, Route } from 'react-router-dom'
import Dashboard from '@/pages/dashboard/Dashboard'
import Workflows from '@/pages/workflows/Workflows'
import Schedules from '@/pages/schedules/Schedules'
import Histories from '@/pages/histories/Histories'
import Analysis from '@/pages/analysis/Analysis'
import RPADemoPage from '@/pages/rpa-demo/RPADemoPage'
import Hearing from '@/pages/workflows/hearing/Hearing'
import HearingChat from '@/pages/workflows/hearing/[workflowId]/HearingChat'
import WorkflowEdit from '@/pages/workflows/edit/[workflowId]/WorkflowEdit'

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/workflows" element={<Workflows />} />
      <Route path="/workflows/hearing" element={<Hearing />} />
      <Route path="/workflows/hearing/:workflowId" element={<HearingChat />} />
      <Route path="/workflows/edit/:workflowId" element={<WorkflowEdit />} />
      <Route path="/schedules" element={<Schedules />} />
      <Route path="/histories" element={<Histories />} />
      <Route path="/analysis" element={<Analysis />} />
      <Route path="/rpa-demo" element={<RPADemoPage />} />
    </Routes>
  )
}
