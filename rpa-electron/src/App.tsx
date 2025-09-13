import { BrowserRouter } from 'react-router-dom'
import { AppSidebar } from '@/components/layout/AppSidebar'
import { MainLayout } from '@/components/layout/MainLayout'
import { SidebarProvider } from '@/components/ui/sidebar'
import { ResponsiveSidebarController } from '@/components/layout/ResponsiveSidebar'
import AppRouter from '@/router'

function App() {
  // 初期状態を画面幅に応じて設定
  const initialOpen = typeof window !== 'undefined' ? window.innerWidth > 1024 : true

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <SidebarProvider defaultOpen={initialOpen}>
          <ResponsiveSidebarController />
          <AppSidebar />
          <MainLayout>
            <AppRouter />
          </MainLayout>
        </SidebarProvider>
      </div>
    </BrowserRouter>
  )
}

export default App