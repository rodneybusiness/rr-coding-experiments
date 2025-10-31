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
import { executeWaterfall as executeWaterfallAPI } from '@/lib/api/services';
import type { WaterfallExecutionResponse } from '@/lib/api/types';

export default function WaterfallPage() {
  const [totalRevenue, setTotalRevenue] = useState<number>(75000000);
  const [releaseStrategy, setReleaseStrategy] = useState<string>('wide_theatrical');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<WaterfallExecutionResponse | null>(null);

  const executeWaterfall = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await executeWaterfallAPI({
        project_id: `proj_${Date.now()}`,
        capital_stack_id: `stack_${Date.now()}`,
        waterfall_id: `waterfall_${Date.now()}`,
        total_revenue: totalRevenue,
        release_strategy: releaseStrategy,
        run_monte_carlo: true,
        monte_carlo_iterations: 1000,
      });

      setResults(response);
    } catch (err: any) {
      setError(err.message || 'Failed to execute waterfall analysis');
      console.error('Error executing waterfall:', err);
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'];

  // Helper to get color for stakeholder by index
  const getStakeholderColor = (index: number) => COLORS[index % COLORS.length];

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
                  {formatCurrency(results.total_distributed)}
                </div>
                <p className="text-sm text-green-100">
                  {formatPercentage((results.total_distributed / results.total_revenue) * 100)}
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
              {results.stakeholder_returns.map((stakeholder, index: number) => (
                <Card key={stakeholder.stakeholder_id} className="border-t-4" style={{ borderTopColor: getStakeholderColor(index) }}>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium text-gray-500">
                      {stakeholder.stakeholder_name}
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
                          <span className="font-semibold">{stakeholder.cash_on_cash}x</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-500">IRR:</span>
                          <span className="font-semibold">{stakeholder.irr ? formatPercentage(stakeholder.irr) : 'N/A'}</span>
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
                      <BarChart data={results.distribution_timeline}>
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
                            data={results.revenue_by_window}
                            dataKey="revenue"
                            nameKey="window"
                            cx="50%"
                            cy="50%"
                            outerRadius={100}
                            label={(entry) => `${entry.window} (${entry.percentage}%)`}
                          >
                            {results.revenue_by_window.map((entry: any, index: number) => (
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
                        {results.revenue_by_window.map((window: any, idx: number) => (
                          <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center gap-3">
                              <div
                                className="h-4 w-4 rounded"
                                style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                              ></div>
                              <div>
                                <p className="font-medium text-sm">{window.window}</p>
                                <p className="text-xs text-gray-500">{formatPercentage(window.percentage, 0)} of total</p>
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
                          {results.stakeholder_returns
                            .filter((s) => s.invested > 0)
                            .map((stakeholder, index: number) => {
                              const profit = stakeholder.received - stakeholder.invested;
                              return (
                                <tr key={stakeholder.stakeholder_id} className="border-b hover:bg-gray-50">
                                  <td className="p-3">
                                    <div className="flex items-center gap-2">
                                      <div
                                        className="h-3 w-3 rounded"
                                        style={{ backgroundColor: getStakeholderColor(index) }}
                                      ></div>
                                      <span className="font-medium">{stakeholder.stakeholder_name}</span>
                                    </div>
                                  </td>
                                  <td className="text-right p-3">{formatCurrency(stakeholder.invested)}</td>
                                  <td className="text-right p-3">{formatCurrency(stakeholder.received)}</td>
                                  <td className="text-right p-3">
                                    <span className={profit > 0 ? 'text-green-600' : 'text-red-600'}>
                                      {formatCurrency(profit)}
                                    </span>
                                  </td>
                                  <td className="text-right p-3 font-semibold">{stakeholder.cash_on_cash}x</td>
                                  <td className="text-right p-3 font-semibold">{stakeholder.irr ? formatPercentage(stakeholder.irr) : 'N/A'}</td>
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
                {results.monte_carlo_results ? (
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
                                {formatPercentage(results.monte_carlo_results.equity_irr.p10)}
                            </p>
                          </div>
                          <div className="text-center p-4 bg-blue-50 rounded-lg">
                            <p className="text-xs text-gray-500 mb-1">P50 (Median)</p>
                            <p className="text-2xl font-bold text-blue-600">
                              {formatPercentage(results.monte_carlo_results.equity_irr.p50)}
                            </p>
                          </div>
                          <div className="text-center p-4 bg-green-50 rounded-lg">
                            <p className="text-xs text-gray-500 mb-1">P90 (Upside)</p>
                            <p className="text-2xl font-bold text-green-600">
                              {formatPercentage(results.monte_carlo_results.equity_irr.p90)}
                            </p>
                          </div>
                        </div>

                        <div className="p-4 bg-gray-50 rounded-lg">
                          <p className="text-sm text-gray-700">
                            <strong>Interpretation:</strong> There's a 10% chance the equity IRR falls below{' '}
                            {formatPercentage(results.monte_carlo_results.equity_irr.p10)}, a 50% chance it exceeds{' '}
                            {formatPercentage(results.monte_carlo_results.equity_irr.p50)}, and a 10% chance it exceeds{' '}
                            {formatPercentage(results.monte_carlo_results.equity_irr.p90)}.
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
                        {Object.entries(results.monte_carlo_results.probability_of_recoupment).map(
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
                            {formatPercentage(results.monte_carlo_results.probability_of_recoupment.seniorDebt)}), while
                            equity faces higher risk with{' '}
                            {formatPercentage(results.monte_carlo_results.probability_of_recoupment.equity)} recoupment
                            probability.
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
                ) : (
                  <div className="p-8 text-center text-gray-500">
                    Monte Carlo simulation was not run for this analysis.
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </>
        )}
      </div>
    </div>
  );
}
