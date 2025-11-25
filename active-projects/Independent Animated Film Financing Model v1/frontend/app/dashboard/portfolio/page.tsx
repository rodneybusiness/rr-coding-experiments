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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  BarChart3,
  PieChart,
  TrendingUp,
  DollarSign,
  Target,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  RefreshCw,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import {
  ResponsiveContainer,
  PieChart as RePieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import { listCapitalPrograms, getPortfolioMetrics } from '@/lib/api/services';
import type { CapitalProgramResponse, PortfolioMetricsResponse } from '@/lib/api/types';
import { formatCurrency, formatPercentage } from '@/lib/utils';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

interface PortfolioMetrics {
  totalCommitted: number;
  totalDeployed: number;
  deploymentRate: number;
  activeProjects: number;
  avgProjectSize: number;
  portfolioMultiple: number;
  totalRecouped: number;
  totalProfit: number;
}

interface ConcentrationData {
  name: string;
  value: number;
  percentage: number;
}

interface PerformanceData {
  metric: string;
  target: number;
  actual: number;
  status: 'on_track' | 'at_risk' | 'behind';
}

// Fallback data when API is unavailable
const fallbackMetrics: PortfolioMetrics = {
  totalCommitted: 250000000,
  totalDeployed: 180000000,
  deploymentRate: 72,
  activeProjects: 12,
  avgProjectSize: 15000000,
  portfolioMultiple: 1.35,
  totalRecouped: 95000000,
  totalProfit: 28000000,
};

const fallbackConcentration: ConcentrationData[] = [
  { name: 'Animation', value: 85000000, percentage: 47 },
  { name: 'Live Action', value: 55000000, percentage: 31 },
  { name: 'Documentary', value: 25000000, percentage: 14 },
  { name: 'Other', value: 15000000, percentage: 8 },
];

const fallbackJurisdiction: ConcentrationData[] = [
  { name: 'United States', value: 90000000, percentage: 50 },
  { name: 'Canada', value: 45000000, percentage: 25 },
  { name: 'United Kingdom', value: 27000000, percentage: 15 },
  { name: 'Ireland', value: 18000000, percentage: 10 },
];

const fallbackPerformance: PerformanceData[] = [
  { metric: 'Deployment Rate', target: 80, actual: 72, status: 'on_track' },
  { metric: 'Portfolio IRR', target: 18, actual: 15.5, status: 'at_risk' },
  { metric: 'Average Multiple', target: 1.5, actual: 1.35, status: 'on_track' },
  { metric: 'Recoupment Rate', target: 90, actual: 85, status: 'on_track' },
  { metric: 'Project Count', target: 15, actual: 12, status: 'behind' },
];

export default function PortfolioPage() {
  const [programs, setPrograms] = useState<CapitalProgramResponse[]>([]);
  const [selectedProgramId, setSelectedProgramId] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<PortfolioMetrics>(fallbackMetrics);
  const [genreConcentration, setGenreConcentration] = useState<ConcentrationData[]>(fallbackConcentration);
  const [jurisdictionConcentration, setJurisdictionConcentration] = useState<ConcentrationData[]>(fallbackJurisdiction);
  const [performance, setPerformance] = useState<PerformanceData[]>(fallbackPerformance);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const programsResponse = await listCapitalPrograms();
      setPrograms(programsResponse.programs);

      if (programsResponse.programs.length > 0) {
        setSelectedProgramId(programsResponse.programs[0].program_id);

        // Calculate aggregate metrics from programs
        const totalCommitted = programsResponse.programs.reduce(
          (sum, p) => sum + p.metrics.total_committed,
          0
        );
        const totalDeployed = programsResponse.programs.reduce(
          (sum, p) => sum + p.metrics.total_funded,
          0
        );
        const totalRecouped = programsResponse.programs.reduce(
          (sum, p) => sum + p.metrics.total_recouped,
          0
        );
        const totalProfit = programsResponse.programs.reduce(
          (sum, p) => sum + p.metrics.total_profit,
          0
        );
        const activeProjects = programsResponse.programs.reduce(
          (sum, p) => sum + p.metrics.num_active_projects,
          0
        );

        setMetrics({
          totalCommitted,
          totalDeployed,
          deploymentRate: totalCommitted > 0 ? (totalDeployed / totalCommitted) * 100 : 0,
          activeProjects,
          avgProjectSize: activeProjects > 0 ? totalDeployed / activeProjects : 0,
          portfolioMultiple: totalDeployed > 0 ? (totalRecouped + totalProfit) / totalDeployed : 0,
          totalRecouped,
          totalProfit,
        });
      }

      setError(null);
    } catch (err) {
      console.error('Failed to load portfolio data:', err);
      setError('Using demo data - API unavailable');
    } finally {
      setLoading(false);
    }
  };

  const radarData = [
    { subject: 'Deployment', A: metrics.deploymentRate, fullMark: 100 },
    { subject: 'Diversification', A: 75, fullMark: 100 },
    { subject: 'Returns', A: metrics.portfolioMultiple * 50, fullMark: 100 },
    { subject: 'Risk', A: 65, fullMark: 100 },
    { subject: 'Liquidity', A: 55, fullMark: 100 },
    { subject: 'Growth', A: 80, fullMark: 100 },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'on_track':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'at_risk':
        return <AlertTriangle className="h-4 w-4 text-amber-500" />;
      case 'behind':
        return <ArrowDownRight className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'on_track':
        return 'text-green-600 bg-green-50';
      case 'at_risk':
        return 'text-amber-600 bg-amber-50';
      case 'behind':
        return 'text-red-600 bg-red-50';
      default:
        return '';
    }
  };

  return (
    <div className="flex flex-col">
      <Header
        title="Portfolio Analytics"
        description="Monitor portfolio performance, concentration, and risk metrics"
      />

      <div className="p-6 space-y-6">
        {/* Error Banner */}
        {error && (
          <div className="bg-amber-50 border border-amber-200 text-amber-700 px-4 py-3 rounded-lg flex items-center justify-between">
            <span className="text-sm">{error}</span>
            <Button variant="ghost" size="sm" onClick={loadData}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        )}

        {/* Program Selector */}
        {programs.length > 0 && (
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-gray-700">Capital Program:</span>
            <Select
              value={selectedProgramId || undefined}
              onValueChange={setSelectedProgramId}
            >
              <SelectTrigger className="w-64">
                <SelectValue placeholder="All Programs" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Programs</SelectItem>
                {programs.map((p) => (
                  <SelectItem key={p.program_id} value={p.program_id}>
                    {p.program_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {/* KPI Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Committed</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {loading ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                <>
                  <div className="text-2xl font-bold">
                    {formatCurrency(metrics.totalCommitted)}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Across {programs.length || 3} programs
                  </p>
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Deployed Capital</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {loading ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                <>
                  <div className="text-2xl font-bold">
                    {formatCurrency(metrics.totalDeployed)}
                  </div>
                  <div className="flex items-center text-xs text-green-600">
                    <ArrowUpRight className="h-3 w-3 mr-1" />
                    {metrics.deploymentRate.toFixed(1)}% deployment rate
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Portfolio Multiple</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {loading ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                <>
                  <div className="text-2xl font-bold">
                    {metrics.portfolioMultiple.toFixed(2)}x
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Target: 1.5x
                  </p>
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Projects</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {loading ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                <>
                  <div className="text-2xl font-bold">{metrics.activeProjects}</div>
                  <p className="text-xs text-muted-foreground">
                    Avg. size: {formatCurrency(metrics.avgProjectSize)}
                  </p>
                </>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Charts Row */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Genre Concentration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChart className="h-5 w-5" />
                Genre Concentration
              </CardTitle>
              <CardDescription>Distribution by project genre</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RePieChart>
                    <Pie
                      data={genreConcentration}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label={({ name, percentage }) => `${name}: ${percentage}%`}
                    >
                      {genreConcentration.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  </RePieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Jurisdiction Distribution */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Jurisdiction Distribution
              </CardTitle>
              <CardDescription>Capital deployed by region</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={jurisdictionConcentration} layout="vertical">
                    <XAxis type="number" tickFormatter={(v) => `$${(v / 1000000).toFixed(0)}M`} />
                    <YAxis dataKey="name" type="category" width={100} />
                    <Tooltip formatter={(value: number) => formatCurrency(value)} />
                    <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Portfolio Health Radar */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Portfolio Health
              </CardTitle>
              <CardDescription>Multi-dimensional assessment</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="subject" />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} />
                    <Radar
                      name="Portfolio"
                      dataKey="A"
                      stroke="#3b82f6"
                      fill="#3b82f6"
                      fillOpacity={0.5}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Performance Tracking */}
        <Card>
          <CardHeader>
            <CardTitle>Performance Tracking</CardTitle>
            <CardDescription>Key metrics vs. targets</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {performance.map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(item.status)}
                    <span className="font-medium">{item.metric}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-sm font-medium">{item.actual}</div>
                      <div className="text-xs text-muted-foreground">
                        Target: {item.target}
                      </div>
                    </div>
                    <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          item.status === 'on_track'
                            ? 'bg-green-500'
                            : item.status === 'at_risk'
                            ? 'bg-amber-500'
                            : 'bg-red-500'
                        }`}
                        style={{ width: `${Math.min((item.actual / item.target) * 100, 100)}%` }}
                      />
                    </div>
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${getStatusColor(
                        item.status
                      )}`}
                    >
                      {item.status === 'on_track'
                        ? 'On Track'
                        : item.status === 'at_risk'
                        ? 'At Risk'
                        : 'Behind'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Financial Summary */}
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Returns Summary</CardTitle>
              <CardDescription>Capital flow and returns</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Total Deployed</span>
                  <span className="font-medium">{formatCurrency(metrics.totalDeployed)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Total Recouped</span>
                  <span className="font-medium">{formatCurrency(metrics.totalRecouped)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Total Profit</span>
                  <span className="font-medium text-green-600">
                    {formatCurrency(metrics.totalProfit)}
                  </span>
                </div>
                <hr />
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Total Returns</span>
                  <span className="font-bold text-lg">
                    {formatCurrency(metrics.totalRecouped + metrics.totalProfit)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Net Gain</span>
                  <span
                    className={`font-bold ${
                      metrics.totalRecouped + metrics.totalProfit - metrics.totalDeployed >= 0
                        ? 'text-green-600'
                        : 'text-red-600'
                    }`}
                  >
                    {formatCurrency(
                      metrics.totalRecouped + metrics.totalProfit - metrics.totalDeployed
                    )}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Risk Indicators</CardTitle>
              <CardDescription>Portfolio risk assessment</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Concentration Risk</span>
                  <span className="px-2 py-1 text-xs rounded-full bg-amber-50 text-amber-700">
                    Medium
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Geographic Diversity</span>
                  <span className="px-2 py-1 text-xs rounded-full bg-green-50 text-green-700">
                    Good
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Counterparty Risk</span>
                  <span className="px-2 py-1 text-xs rounded-full bg-green-50 text-green-700">
                    Low
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Market Timing</span>
                  <span className="px-2 py-1 text-xs rounded-full bg-amber-50 text-amber-700">
                    Medium
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Liquidity Risk</span>
                  <span className="px-2 py-1 text-xs rounded-full bg-green-50 text-green-700">
                    Low
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
