import type { ReactNode } from 'react'
import { Sidebar } from '@/components/sidebar'

interface DashboardShellProps {
  children: ReactNode
}

export function DashboardShell({ children }: DashboardShellProps) {
  return (
    <div className="flex h-screen w-full bg-background">
      <Sidebar />
      {children}
    </div>
  )
}