'use client';

import { useEffect, useState } from 'react';
import { Header } from '@/components/layout/header';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Calculator,
  TrendingUp,
  Lightbulb,
  ArrowRight,
  DollarSign,
  FileText,
  BarChart3,
  Briefcase,
  FolderOpen,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import Link from 'next/link';
import { getDashboardMetrics } from '@/lib/api/services';
import type { DashboardResponse, DashboardMetrics, RecentActivity } from '@/lib/api/types';

// Fallback mock data for when API is unavailable
const fallbackMetrics: DashboardMetrics = {
  total_projects: 12,
  total_budget: 360000000,
  total_tax_incentives: 72000000,
  average_capture_rate: 20,
  scenarios_generated: 48,
  active_capital_programs: 3,
  total_committed_capital: 250000000,
  total_deployed_capital: 180000000,
  projects_in_development: 4,
  projects_in_production: 8,
};

const fallbackActivity: RecentActivity[] = [
  {
    project: 'Animated Feature - Sky Warriors',
    action: 'Optimized capital stack',
    time: '2 hours ago',
    activity_type: 'scenario',
  },
  {
    project: 'CGI Feature - Deep Space',
    action: 'Calculated tax incentives',
    time: '5 hours ago',
    activity_type: 'incentive',
  },
  {
    project: 'Adventure Film - Lost Kingdom',
    action: 'Ran waterfall analysis',
    time: '1 day ago',
    activity_type: 'waterfall',
  },
];

function formatCurrency(amount: number): string {
  if (amount >= 1000000000) {
    return `$${(amount / 1000000000).toFixed(1)}B`;
  } else if (amount >= 1000000) {
    return `$${(amount / 1000000).toFixed(0)}M`;
  } else if (amount >= 1000) {
    return `$${(amount / 1000).toFixed(0)}K`;
  }
  return `$${amount.toFixed(0)}`;
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics>(fallbackMetrics);
  const [activity, setActivity] = useState<RecentActivity[]>(fallbackActivity);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        setLoading(true);
        const data: DashboardResponse = await getDashboardMetrics();
        setMetrics(data.metrics);
        setActivity(data.recent_activity);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch dashboard metrics:', err);
        // Use fallback data but show warning
        setError('Using demo data - API not available');
      } finally {
        setLoading(false);
      }
    }

    fetchDashboardData();
  }, []);

  return (
    <div className="flex flex-col">
      <Header
        title="Dashboard"
        description="Welcome to Film Financing Navigator"
      />

      <div className="p-6 space-y-6">
        {/* Error Banner */}
        {error && (
          <div className="bg-amber-50 border border-amber-200 text-amber-700 px-4 py-3 rounded-lg flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm">{error}</span>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card className="animate-slide-in">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Total Projects
              </CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {loading ? (
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              ) : (
                <>
                  <div className="text-2xl font-bold">{metrics.total_projects}</div>
                  <p className="text-xs text-muted-foreground">
                    {metrics.projects_in_development} in development, {metrics.projects_in_production} in production
                  </p>
                </>
              )}
            </CardContent>
          </Card>

          <Card className="animate-slide-in" style={{ animationDelay: '0.1s' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Total Budget
              </CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {loading ? (
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              ) : (
                <>
                  <div className="text-2xl font-bold">{formatCurrency(metrics.total_budget)}</div>
                  <p className="text-xs text-muted-foreground">
                    Across all projects
                  </p>
                </>
              )}
            </CardContent>
          </Card>

          <Card className="animate-slide-in" style={{ animationDelay: '0.2s' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Tax Incentives
              </CardTitle>
              <Calculator className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {loading ? (
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              ) : (
                <>
                  <div className="text-2xl font-bold">{formatCurrency(metrics.total_tax_incentives)}</div>
                  <p className="text-xs text-muted-foreground">
                    {metrics.average_capture_rate.toFixed(0)}% average capture rate
                  </p>
                </>
              )}
            </CardContent>
          </Card>

          <Card className="animate-slide-in" style={{ animationDelay: '0.3s' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Capital Programs
              </CardTitle>
              <Briefcase className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {loading ? (
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              ) : (
                <>
                  <div className="text-2xl font-bold">{metrics.active_capital_programs}</div>
                  <p className="text-xs text-muted-foreground">
                    {formatCurrency(metrics.total_deployed_capital)} deployed
                  </p>
                </>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Engine 1: Tax Incentives */}
          <Card className="group hover:shadow-lg transition-all duration-200 border-blue-200">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                  <Calculator className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Tax Incentive Calculator</CardTitle>
                  <CardDescription>Engine 1</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                Calculate tax credits and incentives across multiple
                jurisdictions with cash flow projections.
              </p>
              <Link href="/dashboard/incentives">
                <Button className="w-full group-hover:bg-blue-600">
                  Open Calculator
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Engine 2: Waterfall */}
          <Card className="group hover:shadow-lg transition-all duration-200 border-green-200">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center group-hover:bg-green-200 transition-colors">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Waterfall Analysis</CardTitle>
                  <CardDescription>Engine 2</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                Execute waterfall distributions with IRR/NPV calculations and
                Monte Carlo simulations.
              </p>
              <Link href="/dashboard/waterfall">
                <Button className="w-full bg-green-600 hover:bg-green-700">
                  Open Analyzer
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Engine 3: Scenarios */}
          <Card className="group hover:shadow-lg transition-all duration-200 border-purple-200">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center group-hover:bg-purple-200 transition-colors">
                  <Lightbulb className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Scenario Optimizer</CardTitle>
                  <CardDescription>Engine 3</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                Generate and optimize capital stack scenarios with
                comprehensive trade-off analysis.
              </p>
              <Link href="/dashboard/scenarios">
                <Button className="w-full bg-purple-600 hover:bg-purple-700">
                  Open Optimizer
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Capital Programs */}
          <Card className="group hover:shadow-lg transition-all duration-200 border-amber-200">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-lg bg-amber-100 flex items-center justify-center group-hover:bg-amber-200 transition-colors">
                  <Briefcase className="h-5 w-5 text-amber-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Capital Programs</CardTitle>
                  <CardDescription>Engine 5</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                Manage capital programs, LP sources, and portfolio-level
                constraints with allocation tracking.
              </p>
              <Link href="/dashboard/capital-programs">
                <Button className="w-full bg-amber-600 hover:bg-amber-700">
                  Manage Programs
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Projects */}
          <Card className="group hover:shadow-lg transition-all duration-200 border-cyan-200">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-lg bg-cyan-100 flex items-center justify-center group-hover:bg-cyan-200 transition-colors">
                  <FolderOpen className="h-5 w-5 text-cyan-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Projects</CardTitle>
                  <CardDescription>Project Management</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                Track all projects, funding gaps, and capital deployments
                across your portfolio.
              </p>
              <Link href="/dashboard/projects">
                <Button className="w-full bg-cyan-600 hover:bg-cyan-700">
                  View Projects
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Portfolio Metrics */}
          <Card className="group hover:shadow-lg transition-all duration-200 border-rose-200">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-lg bg-rose-100 flex items-center justify-center group-hover:bg-rose-200 transition-colors">
                  <BarChart3 className="h-5 w-5 text-rose-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Portfolio Analytics</CardTitle>
                  <CardDescription>Insights</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                View portfolio-level metrics, concentration analysis,
                and performance tracking.
              </p>
              <Link href="/dashboard/portfolio">
                <Button className="w-full bg-rose-600 hover:bg-rose-700">
                  View Analytics
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Your latest projects and analyses</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              </div>
            ) : (
              <div className="space-y-4">
                {activity.map((item, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between border-b pb-4 last:border-0 last:pb-0"
                  >
                    <div className="flex items-center space-x-4">
                      <div
                        className={`h-2 w-2 rounded-full ${
                          item.activity_type === 'scenario'
                            ? 'bg-purple-500'
                            : item.activity_type === 'incentive'
                            ? 'bg-blue-500'
                            : item.activity_type === 'waterfall'
                            ? 'bg-green-500'
                            : item.activity_type === 'capital'
                            ? 'bg-amber-500'
                            : item.activity_type === 'project'
                            ? 'bg-cyan-500'
                            : 'bg-gray-500'
                        }`}
                      ></div>
                      <div>
                        <p className="font-medium text-sm">{item.project}</p>
                        <p className="text-xs text-gray-500">{item.action}</p>
                      </div>
                    </div>
                    <p className="text-xs text-gray-400">{item.time}</p>
                  </div>
                ))}
                {activity.length === 0 && (
                  <p className="text-center text-sm text-muted-foreground py-8">
                    No recent activity. Start by creating a project!
                  </p>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
