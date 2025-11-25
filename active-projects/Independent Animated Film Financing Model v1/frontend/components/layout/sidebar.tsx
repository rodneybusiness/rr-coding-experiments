'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  Calculator,
  TrendingUp,
  Lightbulb,
  FolderOpen,
  Settings,
  HelpCircle,
  Handshake,
  Shield,
} from 'lucide-react';

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    name: 'Tax Incentives',
    href: '/dashboard/incentives',
    icon: Calculator,
    description: 'Engine 1: Calculate tax credits',
  },
  {
    name: 'Waterfall Analysis',
    href: '/dashboard/waterfall',
    icon: TrendingUp,
    description: 'Engine 2: Revenue distributions',
  },
  {
    name: 'Scenario Optimizer',
    href: '/dashboard/scenarios',
    icon: Lightbulb,
    description: 'Engine 3: Optimize capital stack',
  },
  {
    name: 'Deal Blocks',
    href: '/dashboard/deals',
    icon: Handshake,
    description: 'Engine 4: Manage deal structures',
  },
  {
    name: 'Ownership Scoring',
    href: '/dashboard/ownership',
    icon: Shield,
    description: 'Engine 4: Strategic position analysis',
  },
  {
    name: 'Projects',
    href: '/dashboard/projects',
    icon: FolderOpen,
  },
];

const secondaryNavigation = [
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
  { name: 'Help', href: '/dashboard/help', icon: HelpCircle },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-full w-64 flex-col bg-gradient-to-b from-gray-900 to-gray-800 text-white">
      {/* Logo */}
      <div className="flex h-16 items-center px-6 border-b border-gray-700">
        <div className="flex items-center space-x-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
            <span className="text-white font-bold text-lg">F</span>
          </div>
          <div>
            <h1 className="text-lg font-bold">FilmFinance</h1>
            <p className="text-xs text-gray-400">Navigator</p>
          </div>
        </div>
      </div>

      {/* Primary Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        <div className="space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'group flex items-center rounded-md px-3 py-2 text-sm font-medium transition-all',
                  isActive
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                )}
              >
                <item.icon
                  className={cn(
                    'mr-3 h-5 w-5 flex-shrink-0',
                    isActive
                      ? 'text-white'
                      : 'text-gray-400 group-hover:text-white'
                  )}
                />
                <div className="flex-1">
                  <div>{item.name}</div>
                  {item.description && (
                    <div className="text-xs text-gray-400 group-hover:text-gray-300">
                      {item.description}
                    </div>
                  )}
                </div>
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Secondary Navigation */}
      <div className="border-t border-gray-700 px-3 py-4">
        <div className="space-y-1">
          {secondaryNavigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'group flex items-center rounded-md px-3 py-2 text-sm font-medium transition-all',
                  isActive
                    ? 'bg-gray-700 text-white'
                    : 'text-gray-400 hover:bg-gray-700 hover:text-white'
                )}
              >
                <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
                {item.name}
              </Link>
            );
          })}
        </div>
      </div>

      {/* User Info */}
      <div className="border-t border-gray-700 px-3 py-4">
        <div className="flex items-center">
          <div className="h-9 w-9 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center">
            <span className="text-sm font-medium">U</span>
          </div>
          <div className="ml-3">
            <p className="text-sm font-medium">User</p>
            <p className="text-xs text-gray-400">user@example.com</p>
          </div>
        </div>
      </div>
    </div>
  );
}
