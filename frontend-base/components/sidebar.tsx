'use client'

import type { ReactNode } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Home,
  TrendingUp,
  Package,
  Settings,
  Bot,
  BarChart3,
  Users,
  Database,
  UserCheck,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface SidebarChildItem {
  id: string
  label: string
  href: string
  icon: ReactNode
}

interface SidebarItem {
  id: string
  label: string
  href: string
  icon: ReactNode
  children?: SidebarChildItem[]
}

export function Sidebar() {
  const pathname = usePathname()

  const menuItems: SidebarItem[] = [
    {
      id: 'overview',
      label: 'Tổng quan',
      href: '/overview',
      icon: <Home className="w-4 h-4" />,
    },
    {
      // id: 'creators',
      // label: 'Nhà sáng tạo',
      // href: '/creators',
      // icon: <Users className="w-4 h-4" />,
      // children: [
      //   {
          id: 'creator-data',
          label: 'Booking',
          href: '/creators/data',
          icon: <Database className="w-4 h-4" />,
      //   },
      // ],
    },
    {
      id: 'products',
      label: 'Sản phẩm',
      href: '/products',
      icon: <Package className="w-4 h-4" />,
    },
    {
      id: 'kol-management',
      label: 'Quản lý KOL',
      href: '/kol-management',
      icon: <UserCheck className="w-4 h-4" />,
    },
    {
      id: 'agent-config',
      label: 'Agent sale',
      href: '/agent-config',
      icon: <Bot className="w-4 h-4" />,
    },
    {
      id: 'analytics',
      label: 'Phân tích',
      href: '/analytics',
      icon: <BarChart3 className="w-4 h-4" />,
    },
  ]

  const isItemActive = (href: string) => {
    if (href === '/creators') {
      return pathname.startsWith('/creators')
    }

    return pathname === href
  }

  return (
    <aside className="w-56 bg-sidebar border-r border-sidebar-border h-screen flex flex-col">
      {/* Header */}
      <div className="p-5 border-b border-sidebar-border">
        <h1 className="text-lg font-bold text-sidebar-foreground">Creator Dashboard</h1>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 px-3 py-6 overflow-y-auto space-y-2">
        {menuItems.map((item) => (
          <div key={item.id} className="space-y-1">
            <Link
              href={item.href}
              className={cn(
                'w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all',
                isItemActive(item.href)
                  ? 'bg-sidebar-primary text-sidebar-primary-foreground shadow-sm'
                  : 'text-sidebar-foreground hover:bg-sidebar-accent/50'
              )}
            >
              {item.icon}
              <span>{item.label}</span>
            </Link>

            {item.children && (
              <div className="ml-8 space-y-1 border-l border-sidebar-border pl-3">
                {item.children.map((child) => {
                  const isChildActive = pathname === child.href

                  return (
                    <Link
                      key={child.id}
                      href={child.href}
                      className={cn(
                        'flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-all',
                        isChildActive
                          ? 'bg-sidebar-accent text-sidebar-foreground font-medium'
                          : 'text-muted-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-foreground'
                      )}
                    >
                      {child.icon}
                      <span>{child.label}</span>
                    </Link>
                  )
                })}
              </div>
            )}
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 ">
        <Link
          href="/settings"
          className={cn(
            'w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all',
            pathname === '/settings'
              ? 'bg-sidebar-primary text-sidebar-primary-foreground shadow-sm'
              : 'text-sidebar-foreground hover:bg-sidebar-accent/50'
          )}
        >
          <Settings className="w-4 h-4" />
          <span>Cài đặt</span>
        </Link>
      </div>
    </aside>
  )
}
