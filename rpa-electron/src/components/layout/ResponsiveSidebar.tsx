import { useEffect, useRef } from 'react'
import { useSidebar } from '@/components/ui/sidebar'

export function ResponsiveSidebarController() {
  const { setOpen, open } = useSidebar()
  const lastWidthRef = useRef(window.innerWidth)
  const lastOpenRef = useRef(open)
  const isManualToggleRef = useRef(false)

  // 初期設定のみ行う
  useEffect(() => {
    // マウント時の初期設定
    const timer = setTimeout(() => {
      if (window.innerWidth <= 1024) {
        setOpen(false)
      } else if (window.innerWidth > 1024) {
        setOpen(true)
      }
    }, 100)

    return () => clearTimeout(timer)
  }, []) // 依存配列を空にして初回のみ実行

  // リサイズハンドリング
  useEffect(() => {
    const handleResize = () => {
      // ユーザーが手動で操作した直後は自動リサイズを無効化
      if (isManualToggleRef.current) {
        // 一定時間後に自動リサイズを再開
        setTimeout(() => {
          isManualToggleRef.current = false
        }, 1000)
        return
      }

      const currentWidth = window.innerWidth
      const lastWidth = lastWidthRef.current

      // 画面幅が1024pxのしきい値を越えた時のみ状態を変更
      if (lastWidth > 1024 && currentWidth <= 1024) {
        setOpen(false)
      } else if (lastWidth <= 1024 && currentWidth > 1024) {
        setOpen(true)
      }

      lastWidthRef.current = currentWidth
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [setOpen])

  // openの変化を検知して手動操作を判定
  useEffect(() => {
    if (lastOpenRef.current !== open) {
      // Keyboard shortcut (Cmd+B) でも動作するように改善
      const handleKeyDown = (e: KeyboardEvent) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'b') {
          isManualToggleRef.current = true
        }
      }
      
      window.addEventListener('keydown', handleKeyDown)
      
      // クリックイベントも検知
      const handleClick = (e: MouseEvent) => {
        const target = e.target as HTMLElement
        if (target.closest('[data-sidebar-trigger]') || target.closest('button[aria-label*="Toggle"]')) {
          isManualToggleRef.current = true
        }
      }
      
      document.addEventListener('click', handleClick, true)
      
      lastOpenRef.current = open
      
      return () => {
        window.removeEventListener('keydown', handleKeyDown)
        document.removeEventListener('click', handleClick, true)
      }
    }
  }, [open])

  return null
}
