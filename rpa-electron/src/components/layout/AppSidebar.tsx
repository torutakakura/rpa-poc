import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Workflow,
  Calendar,
  History,
  BarChart3,
  User,
  Menu,
  Code2
} from 'lucide-react'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
  useSidebar
} from '@/components/ui/sidebar'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'

const navItems = [
  {
    title: 'ダッシュボード',
    href: '/',
    icon: LayoutDashboard
  },
  {
    title: 'ワークフロー',
    href: '/workflows',
    icon: Workflow
  },
  {
    title: 'スケジュール',
    href: '/schedules',
    icon: Calendar
  },
  {
    title: '実行履歴',
    href: '/histories',
    icon: History
  },
  {
    title: '分析',
    href: '/analysis',
    icon: BarChart3
  },
  {
    title: 'Python連携デモ',
    href: '/rpa-demo',
    icon: Code2
  }
]

export function AppSidebar() {
  const location = useLocation()
  const { open } = useSidebar()

  return (
    <TooltipProvider delayDuration={0}>
      <Sidebar 
        className="border-r border-gray-200 fixed left-0 top-0 h-screen z-50 bg-white/95 backdrop-blur-sm" 
        collapsible="icon"
        data-sidebar="sidebar"
      >
        <SidebarHeader className="border-b">
          <div className={open ? "flex items-center justify-between px-2 py-4 gap-2" : "flex items-center justify-center px-2 py-4"}>
            {open && (
              <div className="flex-1 min-w-0">
                <h1 className="text-xl font-bold truncate">RPA Manager</h1>
                <p className="text-sm text-muted-foreground truncate">Electron Edition</p>
              </div>
            )}
            <SidebarTrigger 
              className="h-8 w-8 shrink-0 hover:bg-accent hover:text-accent-foreground rounded-md transition-colors" 
              data-sidebar-trigger
              aria-label="Toggle sidebar"
            >
              <Menu className="h-4 w-4" />
            </SidebarTrigger>
          </div>
        </SidebarHeader>
      
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {navItems.map((item) => {
                const isActive = location.pathname === item.href
                return (
                  <SidebarMenuItem key={item.href}>
                    {open ? (
                      <SidebarMenuButton 
                        asChild
                        isActive={isActive}
                      >
                        <Link to={item.href}>
                          <item.icon className="h-4 w-4" />
                          <span>{item.title}</span>
                        </Link>
                      </SidebarMenuButton>
                    ) : (
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <SidebarMenuButton 
                            asChild
                            isActive={isActive}
                          >
                            <Link to={item.href}>
                              <item.icon className="h-4 w-4" />
                            </Link>
                          </SidebarMenuButton>
                        </TooltipTrigger>
                        <TooltipContent side="right">
                          {item.title}
                        </TooltipContent>
                      </Tooltip>
                    )}
                  </SidebarMenuItem>
                )
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      
        <SidebarFooter className="border-t">
          <SidebarMenu>
            <SidebarMenuItem>
              {open ? (
                <SidebarMenuButton>
                  <User className="h-4 w-4" />
                  <div className="flex flex-col items-start">
                    <span className="text-sm font-medium">ユーザー</span>
                    <span className="text-xs text-muted-foreground">user@example.com</span>
                  </div>
                </SidebarMenuButton>
              ) : (
                <Tooltip>
                  <TooltipTrigger asChild>
                    <SidebarMenuButton>
                      <User className="h-4 w-4" />
                    </SidebarMenuButton>
                  </TooltipTrigger>
                  <TooltipContent side="right">
                    <div>
                      <p className="font-medium">ユーザー</p>
                      <p className="text-xs">user@example.com</p>
                    </div>
                  </TooltipContent>
                </Tooltip>
              )}
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarFooter>
      </Sidebar>
    </TooltipProvider>
  )
}
