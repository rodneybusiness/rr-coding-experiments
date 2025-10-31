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
} from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  return (
    <div className="flex flex-col">
      <Header
        title="Dashboard"
        description="Welcome to Film Financing Navigator"
      />

      <div className="p-6 space-y-6">
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
              <div className="text-2xl font-bold">12</div>
              <p className="text-xs text-muted-foreground">
                +2 from last month
              </p>
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
              <div className="text-2xl font-bold">$360M</div>
              <p className="text-xs text-muted-foreground">
                Across all projects
              </p>
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
              <div className="text-2xl font-bold">$72M</div>
              <p className="text-xs text-muted-foreground">
                20% average capture rate
              </p>
            </CardContent>
          </Card>

          <Card className="animate-slide-in" style={{ animationDelay: '0.3s' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Scenarios Generated
              </CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">48</div>
              <p className="text-xs text-muted-foreground">
                Optimized capital stacks
              </p>
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
        </div>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Your latest projects and analyses</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                {
                  project: 'Animated Feature - Sky Warriors',
                  action: 'Optimized capital stack',
                  time: '2 hours ago',
                  type: 'scenario',
                },
                {
                  project: 'CGI Feature - Deep Space',
                  action: 'Calculated tax incentives',
                  time: '5 hours ago',
                  type: 'incentive',
                },
                {
                  project: 'Adventure Film - Lost Kingdom',
                  action: 'Ran waterfall analysis',
                  time: '1 day ago',
                  type: 'waterfall',
                },
              ].map((activity, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between border-b pb-4 last:border-0 last:pb-0"
                >
                  <div className="flex items-center space-x-4">
                    <div
                      className={`h-2 w-2 rounded-full ${
                        activity.type === 'scenario'
                          ? 'bg-purple-500'
                          : activity.type === 'incentive'
                          ? 'bg-blue-500'
                          : 'bg-green-500'
                      }`}
                    ></div>
                    <div>
                      <p className="font-medium text-sm">{activity.project}</p>
                      <p className="text-xs text-gray-500">{activity.action}</p>
                    </div>
                  </div>
                  <p className="text-xs text-gray-400">{activity.time}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
