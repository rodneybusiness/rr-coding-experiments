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

  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

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
    // Simulate API call
    setTimeout(() => {
      // Mock results
      const mockResults = {
        totalGrossCredit: 5790000,
        totalNetBenefit: 4632000,
        effectiveRate: 15.44,
        jurisdictionBreakdown: [
          {
            jurisdiction: 'Quebec, Canada',
            grossCredit: 5790000,
            policies: [
              {
                name: 'Canadian Film or Video Production Tax Credit (CPTC)',
                credit: 3000000,
                rate: 25,
              },
              {
                name: 'Quebec Production Services Tax Credit (PSTC)',
                credit: 2790000,
                rate: 20,
              },
            ],
          },
        ],
        cashFlowProjection: [
          { quarter: 1, amount: 0 },
          { quarter: 2, amount: 0 },
          { quarter: 3, amount: 0 },
          { quarter: 4, amount: 0 },
          { quarter: 5, amount: 0 },
          { quarter: 6, amount: 2316000 },
          { quarter: 7, amount: 2316000 },
          { quarter: 8, amount: 0 },
        ],
      };
      setResults(mockResults);
      setLoading(false);
    }, 1500);
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
                    {formatCurrency(results.totalGrossCredit)}
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
                    {formatCurrency(results.totalNetBenefit)}
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
                    {formatPercentage(results.effectiveRate)}
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
                  {results.jurisdictionBreakdown.map((jb: any, idx: number) => (
                    <Card key={idx} className="border-2">
                      <CardHeader>
                        <CardTitle className="text-lg">
                          {jb.jurisdiction}
                        </CardTitle>
                        <CardDescription>
                          Total Credit: {formatCurrency(jb.grossCredit)}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {jb.policies.map((policy: any, pidx: number) => (
                            <div
                              key={pidx}
                              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                            >
                              <div>
                                <p className="font-medium text-sm">
                                  {policy.name}
                                </p>
                                <p className="text-xs text-gray-500">
                                  {formatPercentage(policy.rate, 0)} rate
                                </p>
                              </div>
                              <div className="text-right">
                                <p className="font-bold text-lg">
                                  {formatCurrency(policy.credit)}
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
                      {results.cashFlowProjection.map((cf: any) => (
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
                          {formatCurrency(results.totalGrossCredit)}
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
                          {formatCurrency(results.totalGrossCredit * 0.85)}
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
                          {formatCurrency(results.totalGrossCredit * 0.8)}
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
