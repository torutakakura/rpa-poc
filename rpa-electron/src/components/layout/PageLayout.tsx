import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface PageLayoutProps {
  children: ReactNode
  title: ReactNode
  description?: string
  action?: ReactNode
  className?: string
  maxWidth?: 'xl' | '2xl' | '3xl' | '4xl' | '5xl' | '6xl' | '7xl' | 'full'
}

export function PageLayout({
  children,
  title,
  description,
  action,
  className,
  maxWidth = 'full'
}: PageLayoutProps) {
  const maxWidthClasses = {
    'xl': 'max-w-xl mx-auto',
    '2xl': 'max-w-2xl mx-auto',
    '3xl': 'max-w-3xl mx-auto',
    '4xl': 'max-w-4xl mx-auto',
    '5xl': 'max-w-5xl mx-auto',
    '6xl': 'max-w-6xl mx-auto',
    '7xl': 'max-w-7xl mx-auto',
    'full': 'w-full'
  }
    
  return (
    <div className={cn(
      "min-h-full",
      maxWidth === 'full' ? 'w-full' : `${maxWidthClasses[maxWidth]} px-6`,
      className
    )}>
      <div className={cn(
        "mb-6 flex items-center justify-between",
        maxWidth === 'full' ? 'px-6 pt-6' : ''
      )}>
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">{title}</h1>
          {description && (
            <p className="mt-2 text-gray-600">{description}</p>
          )}
        </div>
        {action && (
          <div className="flex items-center gap-2">
            {action}
          </div>
        )}
      </div>
      <div className={cn(
        "space-y-6",
        maxWidth === 'full' ? 'px-6 pb-6 pr-12' : ''
      )}>
        {children}
      </div>
    </div>
  )
}
