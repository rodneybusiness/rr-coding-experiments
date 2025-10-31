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
  Lightbulb,
  Sparkles,
  TrendingUp,
  TrendingDown,
  Download,
  CheckCircle2,
  AlertCircle,
  Target,
  BarChart3,
  Zap,
} from 'lucide-react';
import { formatCurrency, formatPercentage, cn } from '@/lib/utils';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from 'recharts';

export default function ScenariosPage() {
  const [projectBudget, setProjectBudget] = useState<number>(30000000);
  const [loading, setLoading] = useState(false);
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [selectedScenarios, setSelectedScenarios] = useState<string[]>([]);

  const generateScenarios = async () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      const mockScenarios = [
        {
          id: 'max-leverage',
          name: 'Maximum Leverage',
          score: 82.5,
          structure: {
            seniorDebt: 12000000,
            gap: 4500000,
            mezzanine: 3000000,
            equity: 7500000,
            taxIncentives: 3000000,
          },
          metrics: {
            equityIRR: 28.5,
            costOfCapital: 11.2,
            taxIncentiveRate: 10.0,
            riskScore: 65,
            debtCoverage: 1.8,
            probabilityRecoupment: 78.9,
          },
          strengths: [
            'Excellent equity returns (28.5% IRR)',
            'Strong debt coverage ratio',
            'Balanced risk profile',
          ],
          weaknesses: ['Moderate tax incentive capture', 'Higher cost of capital'],
        },
        {
          id: 'tax-optimized',
          name: 'Tax Optimized',
          score: 88.2,
          structure: {
            seniorDebt: 9000000,
            gap: 3000000,
            mezzanine: 2000000,
            equity: 10000000,
            taxIncentives: 6000000,
          },
          metrics: {
            equityIRR: 32.1,
            costOfCapital: 10.5,
            taxIncentiveRate: 20.0,
            riskScore: 55,
            debtCoverage: 2.2,
            probabilityRecoupment: 85.5,
          },
          strengths: [
            'Exceptional tax incentive capture (20%)',
            'Highest equity returns (32.1% IRR)',
            'Low risk profile',
            'Excellent debt coverage',
          ],
          weaknesses: ['Requires more equity capital'],
        },
        {
          id: 'balanced',
          name: 'Balanced',
          score: 85.7,
          structure: {
            seniorDebt: 10500000,
            gap: 3750000,
            mezzanine: 2250000,
            equity: 8500000,
            taxIncentives: 5000000,
          },
          metrics: {
            equityIRR: 30.2,
            costOfCapital: 10.8,
            taxIncentiveRate: 16.7,
            riskScore: 58,
            debtCoverage: 2.0,
            probabilityRecoupment: 82.3,
          },
          strengths: [
            'Balanced capital structure',
            'Strong equity returns (30.2% IRR)',
            'Good tax incentive capture (16.7%)',
            'Low risk profile',
          ],
          weaknesses: ['No significant weaknesses'],
        },
        {
          id: 'low-risk',
          name: 'Low Risk',
          score: 79.3,
          structure: {
            seniorDebt: 8000000,
            gap: 2000000,
            mezzanine: 1000000,
            equity: 12000000,
            taxIncentives: 7000000,
          },
          metrics: {
            equityIRR: 25.8,
            costOfCapital: 9.8,
            taxIncentiveRate: 23.3,
            riskScore: 45,
            debtCoverage: 2.8,
            probabilityRecoupment: 92.1,
          },
          strengths: [
            'Highest tax incentive capture (23.3%)',
            'Lowest risk profile',
            'Very high probability of recoupment (92%)',
            'Lowest cost of capital',
          ],
          weaknesses: [
            'Lower equity returns (25.8% IRR)',
            'Requires most equity capital',
          ],
        },
      ];
      setScenarios(mockScenarios);
      setSelectedScenarios([mockScenarios[1].id, mockScenarios[2].id]);
      setLoading(false);
    }, 2000);
  };

  const toggleScenarioSelection = (id: string) => {
    setSelectedScenarios((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id].slice(-3)
    );
  };

  const selectedScenariosData = scenarios.filter((s) =>
    selectedScenarios.includes(s.id)
  );

  // Prepare radar chart data for comparison
  const radarData = [
    {
      metric: 'Equity IRR',
      ...Object.fromEntries(
        selectedScenariosData.map((s) => [s.name, s.metrics.equityIRR])
      ),
    },
    {
      metric: 'Tax Incentives',
      ...Object.fromEntries(
        selectedScenariosData.map((s) => [s.name, s.metrics.taxIncentiveRate * 5])
      ),
    },
    {
      metric: 'Low Risk',
      ...Object.fromEntries(
        selectedScenariosData.map((s) => [s.name, 100 - s.metrics.riskScore])
      ),
    },
    {
      metric: 'Debt Coverage',
      ...Object.fromEntries(
        selectedScenariosData.map((s) => [s.name, s.metrics.debtCoverage * 15])
      ),
    },
    {
      metric: 'Low Cost',
      ...Object.fromEntries(
        selectedScenariosData.map((s) => [s.name, 100 - s.metrics.costOfCapital * 5])
      ),
    },
  ];

  // Prepare scatter data for trade-off analysis
  const scatterData = scenarios.map((s) => ({
    x: s.metrics.equityIRR,
    y: s.metrics.riskScore,
    z: s.score,
    name: s.name,
  }));

  const COLORS = ['#3b82f6', '#10b981', '#8b5cf6', '#f59e0b'];

  return (
    <div className="flex flex-col">
      <Header
        title="Scenario Optimizer"
        description="Engine 3: Generate and compare capital stack scenarios"
      />

      <div className="p-6 space-y-6">
        {/* Input and Generate */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5" />
              Generate Scenarios
            </CardTitle>
            <CardDescription>
              Configure project parameters and generate optimized capital stacks
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6 md:grid-cols-2">
              <div>
                <Label htmlFor="projectBudget">Project Budget</Label>
                <Input
                  id="projectBudget"
                  type="number"
                  value={projectBudget}
                  onChange={(e) => setProjectBudget(Number(e.target.value))}
                  className="mt-1.5"
                />
              </div>

              <div className="flex items-end">
                <Button
                  className="w-full"
                  size="lg"
                  onClick={generateScenarios}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      Generating Scenarios...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-2" />
                      Generate Optimized Scenarios
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Scenarios Grid */}
        {scenarios.length > 0 && (
          <>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {scenarios.map((scenario) => {
                const isSelected = selectedScenarios.includes(scenario.id);
                const isTopScorer = scenario.score === Math.max(...scenarios.map((s) => s.score));

                return (
                  <Card
                    key={scenario.id}
                    className={cn(
                      'relative cursor-pointer transition-all hover:shadow-lg',
                      isSelected && 'ring-2 ring-blue-500',
                      isTopScorer && 'border-green-500 border-2'
                    )}
                    onClick={() => toggleScenarioSelection(scenario.id)}
                  >
                    {isTopScorer && (
                      <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                        <span className="bg-green-500 text-white text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1">
                          <Zap className="h-3 w-3" />
                          Best Score
                        </span>
                      </div>
                    )}

                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-lg">{scenario.name}</CardTitle>
                        {isSelected && (
                          <CheckCircle2 className="h-5 w-5 text-blue-500" />
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full"
                            style={{ width: `${scenario.score}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-bold">{scenario.score.toFixed(1)}</span>
                      </div>
                    </CardHeader>

                    <CardContent>
                      <div className="space-y-3">
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div>
                            <p className="text-gray-500 text-xs">Equity IRR</p>
                            <p className="font-bold text-green-600">
                              {formatPercentage(scenario.metrics.equityIRR)}
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-500 text-xs">Risk Score</p>
                            <p className="font-bold">{scenario.metrics.riskScore}</p>
                          </div>
                          <div>
                            <p className="text-gray-500 text-xs">Tax Rate</p>
                            <p className="font-bold text-blue-600">
                              {formatPercentage(scenario.metrics.taxIncentiveRate)}
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-500 text-xs">Recoupment</p>
                            <p className="font-bold">
                              {formatPercentage(scenario.metrics.probabilityRecoupment)}
                            </p>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            <p className="text-sm text-center text-gray-500">
              Click scenarios to select (up to 3) for detailed comparison
            </p>

            {/* Comparison Tabs */}
            {selectedScenariosData.length > 0 && (
              <Tabs defaultValue="structure">
                <TabsList>
                  <TabsTrigger value="structure">Capital Structure</TabsTrigger>
                  <TabsTrigger value="comparison">Side-by-Side</TabsTrigger>
                  <TabsTrigger value="radar">Performance Radar</TabsTrigger>
                  <TabsTrigger value="tradeoffs">Trade-off Analysis</TabsTrigger>
                </TabsList>

                <TabsContent value="structure">
                  <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {selectedScenariosData.map((scenario) => (
                      <Card key={scenario.id}>
                        <CardHeader>
                          <CardTitle className="text-base">{scenario.name}</CardTitle>
                          <CardDescription>
                            Score: {scenario.score.toFixed(1)}/100
                          </CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-2">
                            {Object.entries(scenario.structure).map(([key, value]: [string, any]) => {
                              const percentage = (value / projectBudget) * 100;
                              return (
                                <div key={key}>
                                  <div className="flex justify-between text-sm mb-1">
                                    <span className="capitalize">
                                      {key.replace(/([A-Z])/g, ' $1').trim()}
                                    </span>
                                    <span className="font-semibold">
                                      {formatCurrency(value)} ({percentage.toFixed(1)}%)
                                    </span>
                                  </div>
                                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                                    <div
                                      className="h-full bg-blue-500"
                                      style={{ width: `${percentage}%` }}
                                    ></div>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="comparison">
                  <Card>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle>Detailed Comparison</CardTitle>
                          <CardDescription>
                            Key metrics across selected scenarios
                          </CardDescription>
                        </div>
                        <Button variant="outline" size="sm">
                          <Download className="h-4 w-4 mr-2" />
                          Export
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="border-b">
                              <th className="text-left p-3 font-medium">Metric</th>
                              {selectedScenariosData.map((s) => (
                                <th key={s.id} className="text-center p-3 font-medium">
                                  {s.name}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            <tr className="border-b hover:bg-gray-50">
                              <td className="p-3 font-medium">Overall Score</td>
                              {selectedScenariosData.map((s) => (
                                <td key={s.id} className="text-center p-3">
                                  <span className="font-bold text-lg">{s.score.toFixed(1)}</span>
                                </td>
                              ))}
                            </tr>
                            <tr className="border-b hover:bg-gray-50">
                              <td className="p-3">Equity IRR</td>
                              {selectedScenariosData.map((s) => (
                                <td key={s.id} className="text-center p-3 font-semibold text-green-600">
                                  {formatPercentage(s.metrics.equityIRR)}
                                </td>
                              ))}
                            </tr>
                            <tr className="border-b hover:bg-gray-50">
                              <td className="p-3">Cost of Capital</td>
                              {selectedScenariosData.map((s) => (
                                <td key={s.id} className="text-center p-3">
                                  {formatPercentage(s.metrics.costOfCapital)}
                                </td>
                              ))}
                            </tr>
                            <tr className="border-b hover:bg-gray-50">
                              <td className="p-3">Tax Incentive Rate</td>
                              {selectedScenariosData.map((s) => (
                                <td key={s.id} className="text-center p-3 font-semibold text-blue-600">
                                  {formatPercentage(s.metrics.taxIncentiveRate)}
                                </td>
                              ))}
                            </tr>
                            <tr className="border-b hover:bg-gray-50">
                              <td className="p-3">Risk Score</td>
                              {selectedScenariosData.map((s) => (
                                <td key={s.id} className="text-center p-3">
                                  <span
                                    className={cn(
                                      'px-2 py-1 rounded-full text-xs font-semibold',
                                      s.metrics.riskScore < 50
                                        ? 'bg-green-100 text-green-700'
                                        : s.metrics.riskScore < 70
                                        ? 'bg-yellow-100 text-yellow-700'
                                        : 'bg-red-100 text-red-700'
                                    )}
                                  >
                                    {s.metrics.riskScore}
                                  </span>
                                </td>
                              ))}
                            </tr>
                            <tr className="border-b hover:bg-gray-50">
                              <td className="p-3">Debt Coverage</td>
                              {selectedScenariosData.map((s) => (
                                <td key={s.id} className="text-center p-3">
                                  {s.metrics.debtCoverage.toFixed(1)}x
                                </td>
                              ))}
                            </tr>
                            <tr className="border-b hover:bg-gray-50">
                              <td className="p-3">P(Recoupment)</td>
                              {selectedScenariosData.map((s) => (
                                <td key={s.id} className="text-center p-3">
                                  {formatPercentage(s.metrics.probabilityRecoupment)}
                                </td>
                              ))}
                            </tr>
                          </tbody>
                        </table>
                      </div>

                      {/* Strengths & Weaknesses */}
                      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 mt-6">
                        {selectedScenariosData.map((scenario) => (
                          <Card key={scenario.id} className="border-2">
                            <CardHeader className="pb-3">
                              <CardTitle className="text-sm">{scenario.name}</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                              <div>
                                <div className="flex items-center gap-2 mb-2">
                                  <TrendingUp className="h-4 w-4 text-green-600" />
                                  <span className="text-xs font-semibold text-green-700">
                                    STRENGTHS
                                  </span>
                                </div>
                                <ul className="space-y-1">
                                  {scenario.strengths.map((s: string, idx: number) => (
                                    <li
                                      key={idx}
                                      className="text-xs text-gray-600 flex items-start gap-1"
                                    >
                                      <CheckCircle2 className="h-3 w-3 text-green-500 mt-0.5 flex-shrink-0" />
                                      <span>{s}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>

                              <div>
                                <div className="flex items-center gap-2 mb-2">
                                  <TrendingDown className="h-4 w-4 text-orange-600" />
                                  <span className="text-xs font-semibold text-orange-700">
                                    WEAKNESSES
                                  </span>
                                </div>
                                <ul className="space-y-1">
                                  {scenario.weaknesses.map((w: string, idx: number) => (
                                    <li
                                      key={idx}
                                      className="text-xs text-gray-600 flex items-start gap-1"
                                    >
                                      <AlertCircle className="h-3 w-3 text-orange-500 mt-0.5 flex-shrink-0" />
                                      <span>{w}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="radar">
                  <Card>
                    <CardHeader>
                      <CardTitle>Performance Radar</CardTitle>
                      <CardDescription>
                        Multi-dimensional comparison of key metrics
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={400}>
                        <RadarChart data={radarData}>
                          <PolarGrid />
                          <PolarAngleAxis dataKey="metric" />
                          <PolarRadiusAxis angle={90} domain={[0, 100]} />
                          {selectedScenariosData.map((scenario, index) => (
                            <Radar
                              key={scenario.id}
                              name={scenario.name}
                              dataKey={scenario.name}
                              stroke={COLORS[index]}
                              fill={COLORS[index]}
                              fillOpacity={0.3}
                            />
                          ))}
                          <Legend />
                        </RadarChart>
                      </ResponsiveContainer>

                      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                        <h4 className="font-semibold text-sm mb-2">How to Read This Chart:</h4>
                        <ul className="text-xs text-gray-700 space-y-1">
                          <li>• Larger areas indicate better overall performance</li>
                          <li>• Each axis represents a normalized metric (0-100 scale)</li>
                          <li>• Compare shapes to identify strengths and trade-offs</li>
                        </ul>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="tradeoffs">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Target className="h-5 w-5" />
                        Risk-Return Trade-off Analysis
                      </CardTitle>
                      <CardDescription>
                        Equity IRR vs Risk Score (bubble size = overall score)
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={400}>
                        <ScatterChart
                          margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis
                            type="number"
                            dataKey="x"
                            name="Equity IRR"
                            unit="%"
                            label={{ value: 'Equity IRR (%)', position: 'insideBottom', offset: -10 }}
                          />
                          <YAxis
                            type="number"
                            dataKey="y"
                            name="Risk Score"
                            label={{ value: 'Risk Score', angle: -90, position: 'insideLeft' }}
                          />
                          <ZAxis type="number" dataKey="z" range={[100, 1000]} />
                          <Tooltip
                            cursor={{ strokeDasharray: '3 3' }}
                            content={({ payload }: any) => {
                              if (payload && payload.length) {
                                const data = payload[0].payload;
                                return (
                                  <div className="bg-white p-3 border rounded-lg shadow-lg">
                                    <p className="font-semibold mb-1">{data.name}</p>
                                    <p className="text-sm">IRR: {formatPercentage(data.x)}</p>
                                    <p className="text-sm">Risk: {data.y}</p>
                                    <p className="text-sm">Score: {data.z.toFixed(1)}</p>
                                  </div>
                                );
                              }
                              return null;
                            }}
                          />
                          <Scatter name="Scenarios" data={scatterData}>
                            {scatterData.map((entry, index) => (
                              <Cell
                                key={`cell-${index}`}
                                fill={COLORS[index % COLORS.length]}
                              />
                            ))}
                          </Scatter>
                        </ScatterChart>
                      </ResponsiveContainer>

                      <div className="grid gap-4 md:grid-cols-3 mt-6">
                        <div className="p-4 bg-green-50 rounded-lg">
                          <div className="flex items-center gap-2 mb-2">
                            <div className="h-3 w-3 rounded-full bg-green-500"></div>
                            <span className="text-sm font-semibold">Optimal Zone</span>
                          </div>
                          <p className="text-xs text-gray-600">
                            High IRR (30%+) with moderate risk (50-60). Best risk-adjusted returns.
                          </p>
                        </div>

                        <div className="p-4 bg-yellow-50 rounded-lg">
                          <div className="flex items-center gap-2 mb-2">
                            <div className="h-3 w-3 rounded-full bg-yellow-500"></div>
                            <span className="text-sm font-semibold">Conservative Zone</span>
                          </div>
                          <p className="text-xs text-gray-600">
                            Lower IRR (25-28%) with low risk (&lt;50). Suitable for risk-averse investors.
                          </p>
                        </div>

                        <div className="p-4 bg-red-50 rounded-lg">
                          <div className="flex items-center gap-2 mb-2">
                            <div className="h-3 w-3 rounded-full bg-red-500"></div>
                            <span className="text-sm font-semibold">High-Risk Zone</span>
                          </div>
                          <p className="text-xs text-gray-600">
                            Risk score &gt;65 requires careful evaluation regardless of IRR potential.
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            )}
          </>
        )}
      </div>
    </div>
  );
}
