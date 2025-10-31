'use client';

import { useState } from 'react';
import { Header } from '@/components/layout/header';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  TrendingUp,
  Play,
  Download,
  BarChart3,
  Users,
  DollarSign,
  Percent,
  TrendingDown,
} from 'lucide-react';
import { formatCurrency, formatPercentage } from '@/lib/utils';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

export default function WaterfallPage() {
  const [totalRevenue, setTotalRevenue] = useState<number>(75000000);
  const [releaseStrategy, setReleaseStrategy] = useState<string>('wide_theatrical');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);

  const executeWaterfall = async () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      // Mock results
      const mockResults = {
        totalRevenue: 75000000,
        totalDistributed: 68250000,
        totalRecouped: 45000000,
        stakeholders: [
          {
            id: 'senior-debt',
            name: 'Senior Debt',
            type: 'Debt',
            invested: 12000000,
            received: 13440000,
            cashOnCash: 1.12,
            irr: 15.5,
            color: '#3b82f6',
          },
          {
            id: 'gap-financing',
            name: 'Gap Financing',
            type: 'Debt',
            invested: 4500000,
            received: 5175000,
            cashOnCash: 1.15,
            irr: 18.2,
            color: '#8b5cf6',
          },
          {
            id: 'equity-investor',
            name: 'Equity Investor',
            type: 'Equity',
            invested: 7500000,
            received: 15750000,
            cashOnCash: 2.1,
            irr: 28.5,
            color: '#10b981',
          },
          {
            id: 'producer',
            name: 'Producer',
            type: 'Backend',
            invested: 0,
            received: 11250000,
            cashOnCash: null,
            irr: null,
            color: '#f59e0b',
          },
        ],
        distributionTimeline: [
          { quarter: 'Q1', senior: 3000000, gap: 0, equity: 0, backend: 0 },
          { quarter: 'Q2', senior: 6000000, gap: 1500000, equity: 0, backend: 0 },
          { quarter: 'Q3', senior: 4440000, gap: 3675000, equity: 3000000, backend: 0 },
          { quarter: 'Q4', senior: 0, gap: 0, equity: 6000000, backend: 4500000 },
          { quarter: 'Q5', senior: 0, gap: 0, equity: 4500000, backend: 4500000 },
          { quarter: 'Q6', senior: 0, gap: 0, equity: 2250000, backend: 2250000 },
        ],
        revenueProjection: [
          { window: 'Theatrical', revenue: 30000000, pct: 40 },
          { window: 'PVOD', revenue: 7500000, pct: 10 },
          { window: 'SVOD', revenue: 15000000, pct: 20 },
          { window: 'TV', revenue: 11250000, pct: 15 },
          { window: 'Other', revenue: 11250000, pct: 15 },
        ],
        monteCarloResults: {
          equityIRR: {
            p10: 12.5,
            p50: 28.5,
            p90: 45.2,
          },
          probabilityOfRecoupment: {
            seniorDebt: 98.5,
            gap: 92.3,
            equity: 78.9,
          },
        },
      };
      setResults(mockResults);
      setLoading(false);
    }, 2000);
  };

  const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'];

  return (
    <div className="flex flex-col">
      <Header
        title="Waterfall Analysis"
        description="Engine 2: Revenue distribution and stakeholder returns"
      />

      <div className="p-6 space-y-6">
        {/* Input Section */}
        <div className="grid gap-6 lg:grid-cols-4">
          <Card className="lg:col-span-3">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Revenue Projection
              </CardTitle>
              <CardDescription>
                Configure revenue assumptions and execute waterfall analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label htmlFor="totalRevenue">Total Ultimate Revenue</Label>
                  <Input
                    id="totalRevenue"
                    type="number"
                    value={totalRevenue}
                    onChange={(e) => setTotalRevenue(Number(e.target.value))}
                    className="mt-1.5"
                  />
                </div>
                <div>
                  <Label htmlFor="releaseStrategy">Release Strategy</Label>
                  <select
                    id="releaseStrategy"
                    value={releaseStrategy}
                    onChange={(e) => setReleaseStrategy(e.target.value)}
                    className="mt-1.5 flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  >
                    <option value="wide_theatrical">Wide Theatrical</option>
                    <option value="limited_theatrical">Limited Theatrical</option>
                    <option value="direct_to_streaming">Direct to Streaming</option>
                  </select>
                </div>
              </div>

              <Button
                className="w-full mt-6"
                size="lg"
                onClick={executeWaterfall}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Executing Waterfall...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Execute Waterfall Analysis
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {results && (
            <Card className="bg-gradient-to-br from-green-500 to-emerald-600 text-white">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <DollarSign className="h-5 w-5" />
                  Total Distributed
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold mb-2">
                  {formatCurrency(results.totalDistributed)}
                </div>
                <p className="text-sm text-green-100">
                  {formatPercentage((results.totalDistributed / results.totalRevenue) * 100)}
                  {' '}of gross revenue
                </p>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Results */}
        {results && (
          <>
            {/* Stakeholder Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {results.stakeholders.map((stakeholder: any) => (
                <Card key={stakeholder.id} className="border-t-4" style={{ borderTopColor: stakeholder.color }}>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium text-gray-500">
                      {stakeholder.name}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div>
                      <p className="text-xs text-gray-500">Total Received</p>
                      <p className="text-xl font-bold">{formatCurrency(stakeholder.received)}</p>
                    </div>
                    {stakeholder.invested > 0 && (
                      <>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-500">Cash-on-Cash:</span>
                          <span className="font-semibold">{stakeholder.cashOnCash}x</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-500">IRR:</span>
                          <span className="font-semibold">{formatPercentage(stakeholder.irr)}</span>
                        </div>
                      </>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Charts and Analysis */}
            <Tabs defaultValue="timeline">
              <TabsList>
                <TabsTrigger value="timeline">Distribution Timeline</TabsTrigger>
                <TabsTrigger value="revenue">Revenue Windows</TabsTrigger>
                <TabsTrigger value="returns">Stakeholder Returns</TabsTrigger>
                <TabsTrigger value="montecarlo">Monte Carlo</TabsTrigger>
              </TabsList>

              <TabsContent value="timeline">
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle>Distribution Timeline</CardTitle>
                        <CardDescription>
                          Quarterly cash distributions to stakeholders
                        </CardDescription>
                      </div>
                      <Button variant="outline" size="sm">
                        <Download className="h-4 w-4 mr-2" />
                        Export
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={400}>
                      <BarChart data={results.distributionTimeline}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="quarter" />
                        <YAxis
                          tickFormatter={(value) =>
                            `$${(value / 1000000).toFixed(0)}M`
                          }
                        />
                        <Tooltip
                          formatter={(value: number) => formatCurrency(value)}
                        />
                        <Legend />
                        <Bar dataKey="senior" name="Senior Debt" fill="#3b82f6" stackId="a" />
                        <Bar dataKey="gap" name="Gap Financing" fill="#8b5cf6" stackId="a" />
                        <Bar dataKey="equity" name="Equity" fill="#10b981" stackId="a" />
                        <Bar dataKey="backend" name="Backend" fill="#f59e0b" stackId="a" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="revenue">
                <div className="grid gap-6 md:grid-cols-2">
                  <Card>
                    <CardHeader>
                      <CardTitle>Revenue by Window</CardTitle>
                      <CardDescription>Distribution across release windows</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                          <Pie
                            data={results.revenueProjection}
                            dataKey="revenue"
                            nameKey="window"
                            cx="50%"
                            cy="50%"
                            outerRadius={100}
                            label={(entry) => `${entry.window} (${entry.pct}%)`}
                          >
                            {results.revenueProjection.map((entry: any, index: number) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip formatter={(value: number) => formatCurrency(value)} />
                        </PieChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Revenue Breakdown</CardTitle>
                      <CardDescription>Detailed window analysis</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {results.revenueProjection.map((window: any, idx: number) => (
                          <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center gap-3">
                              <div
                                className="h-4 w-4 rounded"
                                style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                              ></div>
                              <div>
                                <p className="font-medium text-sm">{window.window}</p>
                                <p className="text-xs text-gray-500">{formatPercentage(window.pct, 0)} of total</p>
                              </div>
                            </div>
                            <p className="font-bold">{formatCurrency(window.revenue)}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="returns">
                <Card>
                  <CardHeader>
                    <CardTitle>Stakeholder Returns Analysis</CardTitle>
                    <CardDescription>
                      Investment performance metrics
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b">
                            <th className="text-left p-3 font-medium">Stakeholder</th>
                            <th className="text-right p-3 font-medium">Invested</th>
                            <th className="text-right p-3 font-medium">Received</th>
                            <th className="text-right p-3 font-medium">Profit</th>
                            <th className="text-right p-3 font-medium">Cash-on-Cash</th>
                            <th className="text-right p-3 font-medium">IRR</th>
                          </tr>
                        </thead>
                        <tbody>
                          {results.stakeholders
                            .filter((s: any) => s.invested > 0)
                            .map((stakeholder: any) => {
                              const profit = stakeholder.received - stakeholder.invested;
                              return (
                                <tr key={stakeholder.id} className="border-b hover:bg-gray-50">
                                  <td className="p-3">
                                    <div className="flex items-center gap-2">
                                      <div
                                        className="h-3 w-3 rounded"
                                        style={{ backgroundColor: stakeholder.color }}
                                      ></div>
                                      <span className="font-medium">{stakeholder.name}</span>
                                    </div>
                                  </td>
                                  <td className="text-right p-3">{formatCurrency(stakeholder.invested)}</td>
                                  <td className="text-right p-3">{formatCurrency(stakeholder.received)}</td>
                                  <td className="text-right p-3">
                                    <span className={profit > 0 ? 'text-green-600' : 'text-red-600'}>
                                      {formatCurrency(profit)}
                                    </span>
                                  </td>
                                  <td className="text-right p-3 font-semibold">{stakeholder.cashOnCash}x</td>
                                  <td className="text-right p-3 font-semibold">{formatPercentage(stakeholder.irr)}</td>
                                </tr>
                              );
                            })}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="montecarlo">
                <div className="grid gap-6 md:grid-cols-2">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <BarChart3 className="h-5 w-5" />
                        Equity IRR Distribution
                      </CardTitle>
                      <CardDescription>
                        1,000 simulations with revenue variance
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-6">
                        <div className="grid grid-cols-3 gap-4">
                          <div className="text-center p-4 bg-red-50 rounded-lg">
                            <p className="text-xs text-gray-500 mb-1">P10 (Downside)</p>
                            <p className="text-2xl font-bold text-red-600">
                              {formatPercentage(results.monteCarloResults.equityIRR.p10)}
                            </p>
                          </div>
                          <div className="text-center p-4 bg-blue-50 rounded-lg">
                            <p className="text-xs text-gray-500 mb-1">P50 (Median)</p>
                            <p className="text-2xl font-bold text-blue-600">
                              {formatPercentage(results.monteCarloResults.equityIRR.p50)}
                            </p>
                          </div>
                          <div className="text-center p-4 bg-green-50 rounded-lg">
                            <p className="text-xs text-gray-500 mb-1">P90 (Upside)</p>
                            <p className="text-2xl font-bold text-green-600">
                              {formatPercentage(results.monteCarloResults.equityIRR.p90)}
                            </p>
                          </div>
                        </div>

                        <div className="p-4 bg-gray-50 rounded-lg">
                          <p className="text-sm text-gray-700">
                            <strong>Interpretation:</strong> There's a 10% chance the equity IRR falls below{' '}
                            {formatPercentage(results.monteCarloResults.equityIRR.p10)}, a 50% chance it exceeds{' '}
                            {formatPercentage(results.monteCarloResults.equityIRR.p50)}, and a 10% chance it exceeds{' '}
                            {formatPercentage(results.monteCarloResults.equityIRR.p90)}.
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Percent className="h-5 w-5" />
                        Probability of Recoupment
                      </CardTitle>
                      <CardDescription>
                        Likelihood of full principal recovery
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {Object.entries(results.monteCarloResults.probabilityOfRecoupment).map(
                          ([key, value]: [string, any]) => (
                            <div key={key}>
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-medium capitalize">
                                  {key.replace(/([A-Z])/g, ' $1').trim()}
                                </span>
                                <span className="text-sm font-bold">{formatPercentage(value)}</span>
                              </div>
                              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-gradient-to-r from-blue-500 to-green-500"
                                  style={{ width: `${value}%` }}
                                ></div>
                              </div>
                            </div>
                          )
                        )}

                        <div className="p-4 bg-blue-50 rounded-lg mt-6">
                          <p className="text-sm text-gray-700">
                            <strong>Risk Assessment:</strong> Senior debt has very high recovery probability (
                            {formatPercentage(results.monteCarloResults.probabilityOfRecoupment.seniorDebt)}), while
                            equity faces higher risk with{' '}
                            {formatPercentage(results.monteCarloResults.probabilityOfRecoupment.equity)} recoupment
                            probability.
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          </>
        )}
      </div>
    </div>
  );
}
