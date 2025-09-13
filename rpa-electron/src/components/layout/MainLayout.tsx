import { useSidebar } from '@/components/ui/sidebar'
import { cn } from '@/lib/utils'

export function MainLayout({ children }: { children: React.ReactNode }) {
  const { open } = useSidebar()

  return (
    <main
      className={cn(
        "w-full min-h-screen overflow-auto bg-gray-50 transition-all duration-300",
        open 
          ? "ml-[var(--sidebar-width)]" 
          : "ml-[calc(var(--sidebar-width-icon)+var(--sidebar-gap))]" // アイコンモード時にギャップを追加
      )}
    >
      {children}
    </main>
  )
}
