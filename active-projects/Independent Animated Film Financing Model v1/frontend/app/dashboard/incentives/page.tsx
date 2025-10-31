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
  Calculator,
  Plus,
  Trash2,
  Download,
  TrendingUp,
  DollarSign,
  Percent,
} from 'lucide-react';
import { formatCurrency, formatPercentage } from '@/lib/utils';
import { calculateIncentives as calculateIncentivesAPI } from '@/lib/api/services';
import type { IncentiveCalculationResponse } from '@/lib/api/types';

interface JurisdictionSpend {
  id: string;
  jurisdiction: string;
  qualifiedSpend: number;
  laborSpend: number;
}

export default function IncentivesPage() {
  const [totalBudget, setTotalBudget] = useState<number>(30000000);
  const [jurisdictions, setJurisdictions] = useState<JurisdictionSpend[]>([
    {
      id: '1',
      jurisdiction: 'Quebec, Canada',
      qualifiedSpend: 16500000,
      laborSpend: 12000000,
    },
  ]);

  const [results, setResults] = useState<IncentiveCalculationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addJurisdiction = () => {
    setJurisdictions([
      ...jurisdictions,
      {
        id: Date.now().toString(),
        jurisdiction: '',
        qualifiedSpend: 0,
        laborSpend: 0,
      },
    ]);
  };

  const removeJurisdiction = (id: string) => {
    setJurisdictions(jurisdictions.filter((j) => j.id !== id));
  };

  const updateJurisdiction = (
    id: string,
    field: keyof JurisdictionSpend,
    value: any
  ) => {
    setJurisdictions(
      jurisdictions.map((j) => (j.id === id ? { ...j, [field]: value } : j))
    );
  };

  const calculateIncentives = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await calculateIncentivesAPI({
        project_id: `proj_${Date.now()}`,
        project_name: 'Film Project',
        total_budget: totalBudget,
        jurisdiction_spends: jurisdictions.map((j) => ({
          jurisdiction: j.jurisdiction,
          qualified_spend: j.qualifiedSpend,
          labor_spend: j.laborSpend,
        })),
      });

      setResults(response);
    } catch (err: any) {
      setError(err.message || 'Failed to calculate incentives');
      console.error('Error calculating incentives:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col">
      <Header
        title="Tax Incentive Calculator"
        description="Engine 1: Calculate tax credits across multiple jurisdictions"
      />

      <div className="p-6 space-y-6">
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Input Form */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calculator className="h-5 w-5" />
                  Project Details
                </CardTitle>
                <CardDescription>
                  Enter your project budget and spending by jurisdiction
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Total Budget */}
                <div>
                  <Label htmlFor="totalBudget">Total Project Budget</Label>
                  <Input
                    id="totalBudget"
                    type="number"
                    value={totalBudget}
                    onChange={(e) => setTotalBudget(Number(e.target.value))}
                    className="mt-1.5"
                  />
                </div>

                {/* Jurisdictions */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label>Jurisdiction Spends</Label>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={addJurisdiction}
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Add Jurisdiction
                    </Button>
                  </div>

                  {jurisdictions.map((jurisdiction) => (
                    <Card key={jurisdiction.id} className="border-2">
                      <CardContent className="pt-6">
                        <div className="grid gap-4">
                          <div className="flex items-center gap-2">
                            <Input
                              placeholder="Jurisdiction (e.g., Quebec, Canada)"
                              value={jurisdiction.jurisdiction}
                              onChange={(e) =>
                                updateJurisdiction(
                                  jurisdiction.id,
                                  'jurisdiction',
                                  e.target.value
                                )
                              }
                              className="flex-1"
                            />
                            {jurisdictions.length > 1 && (
                              <Button
                                size="icon"
                                variant="ghost"
                                onClick={() =>
                                  removeJurisdiction(jurisdiction.id)
                                }
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            )}
                          </div>

                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <Label>Qualified Spend</Label>
                              <Input
                                type="number"
                                value={jurisdiction.qualifiedSpend}
                                onChange={(e) =>
                                  updateJurisdiction(
                                    jurisdiction.id,
                                    'qualifiedSpend',
                                    Number(e.target.value)
                                  )
                                }
                                className="mt-1.5"
                              />
                            </div>
                            <div>
                              <Label>Labor Spend</Label>
                              <Input
                                type="number"
                                value={jurisdiction.laborSpend}
                                onChange={(e) =>
                                  updateJurisdiction(
                                    jurisdiction.id,
                                    'laborSpend',
                                    Number(e.target.value)
                                  )
                                }
                                className="mt-1.5"
                              />
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                <Button
                  className="w-full"
                  size="lg"
                  onClick={calculateIncentives}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      Calculating...
                    </>
                  ) : (
                    <>
                      <Calculator className="h-4 w-4 mr-2" />
                      Calculate Incentives
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Quick Stats */}
          {results && (
            <div className="space-y-4">
              <Card className="bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-white">
                    <DollarSign className="h-5 w-5" />
                    Total Gross Credit
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">
                    {formatCurrency(results.total_gross_credit)}
                  </div>
                  <p className="text-sm text-blue-100 mt-2">
                    Before monetization
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-green-500 to-emerald-600 text-white">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-white">
                    <TrendingUp className="h-5 w-5" />
                    Net Benefit
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">
                    {formatCurrency(results.total_net_benefit)}
                  </div>
                  <p className="text-sm text-green-100 mt-2">
                    After 20% discount
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-purple-500 to-pink-600 text-white">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-white">
                    <Percent className="h-5 w-5" />
                    Effective Rate
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">
                    {formatPercentage(results.effective_rate)}
                  </div>
                  <p className="text-sm text-purple-100 mt-2">
                    Of total budget
                  </p>
                </CardContent>
              </Card>
            </div>
          )}
        </div>

        {/* Results Tabs */}
        {results && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Calculation Results</CardTitle>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Export Report
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="breakdown">
                <TabsList>
                  <TabsTrigger value="breakdown">Policy Breakdown</TabsTrigger>
                  <TabsTrigger value="cashflow">Cash Flow Projection</TabsTrigger>
                  <TabsTrigger value="monetization">
                    Monetization Options
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="breakdown" className="space-y-4">
                  {results.jurisdiction_breakdown.map((jb, idx: number) => (
                    <Card key={idx} className="border-2">
                      <CardHeader>
                        <CardTitle className="text-lg">
                          {jb.jurisdiction}
                        </CardTitle>
                        <CardDescription>
                          Total Credit: {formatCurrency(jb.gross_credit)}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {jb.policies.map((policy, pidx: number) => (
                            <div
                              key={pidx}
                              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                            >
                              <div>
                                <p className="font-medium text-sm">
                                  {policy.name}
                                </p>
                                <p className="text-xs text-gray-500">
                                  {formatPercentage(policy.credit_rate, 0)} rate
                                </p>
                              </div>
                              <div className="text-right">
                                <p className="font-bold text-lg">
                                  {formatCurrency(policy.credit_amount)}
                                </p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </TabsContent>

                <TabsContent value="cashflow">
                  <div className="space-y-4">
                    <div className="grid grid-cols-8 gap-2">
                      {results.cash_flow_projection.map((cf) => (
                        <div
                          key={cf.quarter}
                          className="text-center p-3 bg-gray-50 rounded-lg"
                        >
                          <p className="text-xs text-gray-500 mb-1">
                            Q{cf.quarter}
                          </p>
                          <p className="font-bold text-sm">
                            {cf.amount > 0
                              ? formatCurrency(cf.amount)
                              : '-'}
                          </p>
                        </div>
                      ))}
                    </div>
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <p className="text-sm text-gray-700">
                        Cash flow represents expected timing of tax credit
                        receipts based on typical processing timelines (18-24
                        months after eligible spend).
                      </p>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="monetization">
                  <div className="grid gap-4 md:grid-cols-3">
                    <Card className="border-2 border-blue-200">
                      <CardHeader>
                        <CardTitle className="text-base">Direct Receipt</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold text-blue-600 mb-2">
                          {formatCurrency(results.monetization_options.direct_receipt)}
                        </div>
                        <p className="text-sm text-gray-600 mb-4">
                          Wait 18-24 months for full credit
                        </p>
                        <ul className="text-xs text-gray-500 space-y-1">
                          <li>• 0% discount</li>
                          <li>• Longest wait time</li>
                          <li>• Maximum benefit</li>
                        </ul>
                      </CardContent>
                    </Card>

                    <Card className="border-2 border-green-200">
                      <CardHeader>
                        <CardTitle className="text-base">Bank Loan</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold text-green-600 mb-2">
                          {formatCurrency(results.monetization_options.bank_loan)}
                        </div>
                        <p className="text-sm text-gray-600 mb-4">
                          Immediate cash, repay from credit
                        </p>
                        <ul className="text-xs text-gray-500 space-y-1">
                          <li>• 15% cost (interest)</li>
                          <li>• Immediate access</li>
                          <li>• Good for cash flow</li>
                        </ul>
                      </CardContent>
                    </Card>

                    <Card className="border-2 border-purple-200">
                      <CardHeader>
                        <CardTitle className="text-base">Sale to Broker</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold text-purple-600 mb-2">
                          {formatCurrency(results.monetization_options.broker_sale)}
                        </div>
                        <p className="text-sm text-gray-600 mb-4">
                          Immediate sale at discount
                        </p>
                        <ul className="text-xs text-gray-500 space-y-1">
                          <li>• 20% discount</li>
                          <li>• Immediate cash</li>
                          <li>• Transfer risk</li>
                        </ul>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
