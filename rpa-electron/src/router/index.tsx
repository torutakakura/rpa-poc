import { Routes, Route } from 'react-router-dom'
import Dashboard from '@/pages/dashboard/Dashboard'
import Workflows from '@/pages/workflows/Workflows'
import Schedules from '@/pages/schedules/Schedules'
import Histories from '@/pages/histories/Histories'
import Analysis from '@/pages/analysis/Analysis'
import RPADemoPage from '@/pages/rpa-demo/RPADemoPage'

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/workflows" element={<Workflows />} />
      <Route path="/schedules" element={<Schedules />} />
      <Route path="/histories" element={<Histories />} />
      <Route path="/analysis" element={<Analysis />} />
      <Route path="/rpa-demo" element={<RPADemoPage />} />
    </Routes>
  )
}
