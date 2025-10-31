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
import { generateScenarios as generateScenariosAPI } from '@/lib/api/services';
import type { ScenarioGenerationResponse, Scenario } from '@/lib/api/types';
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
  const [error, setError] = useState<string | null>(null);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [selectedScenarios, setSelectedScenarios] = useState<string[]>([]);

  const generateScenarios = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await generateScenariosAPI({
        project_id: `proj_${Date.now()}`,
        project_name: 'Film Project',
        project_budget: projectBudget,
        waterfall_id: `waterfall_${Date.now()}`,
        num_scenarios: 4,
      });

      setScenarios(response.scenarios);
      // Auto-select the best scenario and one other
      if (response.scenarios.length >= 2) {
        setSelectedScenarios([
          response.best_scenario_id,
          response.scenarios.find((s) => s.scenario_id !== response.best_scenario_id)?.scenario_id || response.scenarios[0].scenario_id,
        ]);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to generate scenarios');
      console.error('Error generating scenarios:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleScenarioSelection = (id: string) => {
    setSelectedScenarios((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id].slice(-3)
    );
  };

  const selectedScenariosData = scenarios.filter((s) =>
    selectedScenarios.includes(s.scenario_id)
  );

  // Prepare radar chart data for comparison
  const radarData = [
    {
      metric: 'Equity IRR',
      ...Object.fromEntries(
        selectedScenariosData.map((s) => [s.scenario_name, s.metrics.equity_irr])
      ),
    },
    {
      metric: 'Tax Incentives',
      ...Object.fromEntries(
        selectedScenariosData.map((s) => [s.scenario_name, s.metrics.tax_incentive_rate * 5])
      ),
    },
    {
      metric: 'Low Risk',
      ...Object.fromEntries(
        selectedScenariosData.map((s) => [s.scenario_name, 100 - s.metrics.risk_score])
      ),
    },
    {
      metric: 'Debt Coverage',
      ...Object.fromEntries(
        selectedScenariosData.map((s) => [s.scenario_name, s.metrics.debt_coverage_ratio * 15])
      ),
    },
    {
      metric: 'Low Cost',
      ...Object.fromEntries(
        selectedScenariosData.map((s) => [s.scenario_name, 100 - s.metrics.cost_of_capital * 5])
      ),
    },
  ];

  // Prepare scatter data for trade-off analysis
  const scatterData = scenarios.map((s) => ({
    x: s.metrics.equity_irr,
    y: s.metrics.risk_score,
    z: s.optimization_score,
    name: s.scenario_name,
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

        {/* Error Display */}
        {error && (
          <Card className="border-red-300 bg-red-50">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-red-700">
                <AlertCircle className="h-5 w-5" />
                <p className="font-semibold">{error}</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Scenarios Grid */}
        {scenarios.length > 0 && (
          <>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {scenarios.map((scenario) => {
                const isSelected = selectedScenarios.includes(scenario.scenario_id);
                const isTopScorer = scenario.optimization_score === Math.max(...scenarios.map((s) => s.optimization_score));

                return (
                  <Card
                    key={scenario.scenario_id}
                    className={cn(
                      'relative cursor-pointer transition-all hover:shadow-lg',
                      isSelected && 'ring-2 ring-blue-500',
                      isTopScorer && 'border-green-500 border-2'
                    )}
                    onClick={() => toggleScenarioSelection(scenario.scenario_id)}
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
                        <CardTitle className="text-lg">{scenario.scenario_name}</CardTitle>
                        {isSelected && (
                          <CheckCircle2 className="h-5 w-5 text-blue-500" />
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full"
                            style={{ width: `${scenario.optimization_score}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-bold">{scenario.optimization_score.toFixed(1)}</span>
                      </div>
                    </CardHeader>

                    <CardContent>
                      <div className="space-y-3">
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div>
                            <p className="text-gray-500 text-xs">Equity IRR</p>
                            <p className="font-bold text-green-600">
                              {formatPercentage(scenario.metrics.equity_irr)}
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-500 text-xs">Risk Score</p>
                            <p className="font-bold">{scenario.metrics.risk_score}</p>
                          </div>
                          <div>
                            <p className="text-gray-500 text-xs">Tax Rate</p>
                            <p className="font-bold text-blue-600">
                              {formatPercentage(scenario.metrics.tax_incentive_rate)}
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-500 text-xs">Recoupment</p>
                            <p className="font-bold">
                              {formatPercentage(scenario.metrics.probability_of_recoupment)}
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
                      <Card key={scenario.scenario_id}>
                        <CardHeader>
                          <CardTitle className="text-base">{scenario.scenario_name}</CardTitle>
                          <CardDescription>
                            Score: {scenario.optimization_score.toFixed(1)}/100
                          </CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-2">
                            {Object.entries(scenario.capital_structure).map(([key, value]: [string, any]) => {
                              const percentage = (value / projectBudget) * 100;
                              return (
                                <div key={key}>
                                  <div className="flex justify-between text-sm mb-1">
                                    <span className="capitalize">
                                      {key.replace(/_/g, ' ')}
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
                                <th key={s.scenario_id} className="text-center p-3 font-medium">
                                  {s.scenario_name}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            <tr className="border-b hover:bg-gray-50">
                              <td className="p-3 font-medium">Overall Score</td>
                              {selectedScenariosData.map((s) => (
                                <td key={s.scenario_id} className="text-center p-3">
                                  <span className="font-bold text-lg">{s.optimization_score.toFixed(1)}</span>
                                </td>
                              ))}
                            </tr>
                            <tr className="border-b hover:bg-gray-50">
                              <td className="p-3">Equity IRR</td>
                              {selectedScenariosData.map((s) => (
                                <td key={s.scenario_id} className="text-center p-3 font-semibold text-green-600">
                                  {formatPercentage(s.metrics.equity_irr)}
                                </td>
                              ))}
                            </tr>
                            <tr className="border-b hover:bg-gray-50">
                              <td className="p-3">Cost of Capital</td>
                              {selectedScenariosData.map((s) => (
                                <td key={s.scenario_id} className="text-center p-3">
                                  {formatPercentage(s.metrics.cost_of_capital)}
                                </td>
                              ))}
                            </tr>
                            <tr className="border-b hover:bg-gray-50">
                              <td className="p-3">Tax Incentive Rate</td>
                              {selectedScenariosData.map((s) => (
                                <td key={s.scenario_id} className="text-center p-3 font-semibold text-blue-600">
                                  {formatPercentage(s.metrics.tax_incentive_rate)}
                                </td>
                              ))}
                            </tr>
                            <tr className="border-b hover:bg-gray-50">
                              <td className="p-3">Risk Score</td>
                              {selectedScenariosData.map((s) => (
                                <td key={s.scenario_id} className="text-center p-3">
                                  <span
                                    className={cn(
                                      'px-2 py-1 rounded-full text-xs font-semibold',
                                      s.metrics.risk_score < 50
                                        ? 'bg-green-100 text-green-700'
                                        : s.metrics.risk_score < 70
                                        ? 'bg-yellow-100 text-yellow-700'
                                        : 'bg-red-100 text-red-700'
                                    )}
                                  >
                                    {s.metrics.risk_score}
                                  </span>
                                </td>
                              ))}
                            </tr>
                            <tr className="border-b hover:bg-gray-50">
                              <td className="p-3">Debt Coverage</td>
                              {selectedScenariosData.map((s) => (
                                <td key={s.scenario_id} className="text-center p-3">
                                  {s.metrics.debt_coverage_ratio.toFixed(1)}x
                                </td>
                              ))}
                            </tr>
                            <tr className="border-b hover:bg-gray-50">
                              <td className="p-3">P(Recoupment)</td>
                              {selectedScenariosData.map((s) => (
                                <td key={s.scenario_id} className="text-center p-3">
                                  {formatPercentage(s.metrics.probability_of_recoupment)}
                                </td>
                              ))}
                            </tr>
                          </tbody>
                        </table>
                      </div>

                      {/* Strengths & Weaknesses */}
                      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 mt-6">
                        {selectedScenariosData.map((scenario) => (
                          <Card key={scenario.scenario_id} className="border-2">
                            <CardHeader className="pb-3">
                              <CardTitle className="text-sm">{scenario.scenario_name}</CardTitle>
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
                              key={scenario.scenario_id}
                              name={scenario.scenario_name}
                              dataKey={scenario.scenario_name}
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
