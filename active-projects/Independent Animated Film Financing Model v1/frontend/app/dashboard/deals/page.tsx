'use client';

import { useState, useEffect } from 'react';
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
  FileText,
  Plus,
  Trash2,
  DollarSign,
  Users,
  Globe,
  Shield,
  AlertTriangle,
} from 'lucide-react';
import { formatCurrency, formatPercentage } from '@/lib/utils';
import { createDeal, listDeals, deleteDeal } from '@/lib/api/services';
import type { DealBlockResponse, DealBlockInput } from '@/lib/api/types';

const DEAL_TYPES = [
  { value: 'equity', label: 'Equity Investment', icon: DollarSign },
  { value: 'presale', label: 'Pre-Sale', icon: Globe },
  { value: 'theatrical_distribution', label: 'Theatrical Distribution', icon: FileText },
  { value: 'streamer_license', label: 'Streamer License', icon: Globe },
  { value: 'gap_financing', label: 'Gap Financing', icon: DollarSign },
  { value: 'co_production', label: 'Co-Production', icon: Users },
];

const APPROVAL_RIGHTS = [
  'final_cut',
  'marketing',
  'casting',
  'budget',
  'schedule',
  'distribution',
];

export default function DealsPage() {
  const [deals, setDeals] = useState<DealBlockResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  // Form state
  const [dealName, setDealName] = useState('');
  const [dealType, setDealType] = useState('equity');
  const [counterpartyName, setCounterpartyName] = useState('');
  const [amount, setAmount] = useState(5000000);
  const [ownershipPct, setOwnershipPct] = useState<number | undefined>(undefined);
  const [territories, setTerritories] = useState('');
  const [termYears, setTermYears] = useState(10);
  const [distributionFeePct, setDistributionFeePct] = useState<number | undefined>(undefined);
  const [approvalRights, setApprovalRights] = useState<string[]>([]);
  const [mfnClause, setMfnClause] = useState(false);
  const [probability, setProbability] = useState(75);

  useEffect(() => {
    loadDeals();
  }, []);

  const loadDeals = async () => {
    try {
      const response = await listDeals();
      setDeals(response.deals || []);
    } catch (err) {
      // API might not be running - use empty state
      setDeals([]);
    }
  };

  const handleCreateDeal = async () => {
    setLoading(true);
    setError(null);

    try {
      const deal: DealBlockInput = {
        deal_name: dealName,
        deal_type: dealType,
        counterparty_name: counterpartyName,
        amount: amount,
        ownership_percentage: ownershipPct,
        territories: territories ? territories.split(',').map(t => t.trim()) : [],
        term_years: termYears,
        distribution_fee_pct: distributionFeePct,
        approval_rights_granted: approvalRights,
        mfn_clause: mfnClause,
        probability_of_closing: probability,
      };

      await createDeal({
        project_id: `proj_${Date.now()}`,
        deal: deal,
      });

      await loadDeals();
      setShowForm(false);
      resetForm();
    } catch (err: any) {
      setError(err.message || 'Failed to create deal');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDeal = async (dealId: string) => {
    try {
      await deleteDeal(dealId);
      await loadDeals();
    } catch (err: any) {
      setError(err.message || 'Failed to delete deal');
    }
  };

  const resetForm = () => {
    setDealName('');
    setDealType('equity');
    setCounterpartyName('');
    setAmount(5000000);
    setOwnershipPct(undefined);
    setTerritories('');
    setTermYears(10);
    setDistributionFeePct(undefined);
    setApprovalRights([]);
    setMfnClause(false);
    setProbability(75);
  };

  const toggleApprovalRight = (right: string) => {
    setApprovalRights(prev =>
      prev.includes(right)
        ? prev.filter(r => r !== right)
        : [...prev, right]
    );
  };

  const totalDealValue = deals.reduce((sum, d) => sum + d.amount, 0);
  const avgProbability = deals.length > 0
    ? deals.reduce((sum, d) => sum + d.probability_of_closing, 0) / deals.length
    : 0;

  return (
    <div className="flex flex-col">
      <Header
        title="Deal Blocks"
        description="Engine 4: Manage deal structures and analyze ownership impact"
      />

      <div className="p-6 space-y-6">
        {/* Summary Cards */}
        <div className="grid gap-6 md:grid-cols-4">
          <Card className="bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-blue-100">
                Total Deals
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{deals.length}</div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-500 to-emerald-600 text-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-green-100">
                Total Value
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {formatCurrency(totalDealValue)}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-500 to-violet-600 text-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-purple-100">
                Avg Probability
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {formatPercentage(avgProbability)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">
                Actions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Button
                onClick={() => setShowForm(!showForm)}
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                {showForm ? 'Cancel' : 'New Deal'}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Create Deal Form */}
        {showForm && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Create New Deal
              </CardTitle>
              <CardDescription>
                Define deal terms to analyze ownership and control impact
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <Tabs defaultValue="basic">
                <TabsList>
                  <TabsTrigger value="basic">Basic Info</TabsTrigger>
                  <TabsTrigger value="financial">Financial</TabsTrigger>
                  <TabsTrigger value="rights">Rights & Control</TabsTrigger>
                </TabsList>

                <TabsContent value="basic" className="space-y-4 mt-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <Label htmlFor="dealName">Deal Name</Label>
                      <Input
                        id="dealName"
                        value={dealName}
                        onChange={(e) => setDealName(e.target.value)}
                        placeholder="e.g., North America Theatrical"
                        className="mt-1.5"
                      />
                    </div>
                    <div>
                      <Label htmlFor="counterparty">Counterparty</Label>
                      <Input
                        id="counterparty"
                        value={counterpartyName}
                        onChange={(e) => setCounterpartyName(e.target.value)}
                        placeholder="e.g., Major Studios Inc."
                        className="mt-1.5"
                      />
                    </div>
                  </div>

                  <div>
                    <Label>Deal Type</Label>
                    <div className="grid gap-2 md:grid-cols-3 mt-1.5">
                      {DEAL_TYPES.map((type) => (
                        <button
                          key={type.value}
                          onClick={() => setDealType(type.value)}
                          className={`p-3 rounded-lg border text-left transition-all ${
                            dealType === type.value
                              ? 'border-blue-500 bg-blue-50 text-blue-700'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <type.icon className="h-5 w-5 mb-1" />
                          <div className="font-medium text-sm">{type.label}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <Label htmlFor="territories">Territories (comma-separated)</Label>
                      <Input
                        id="territories"
                        value={territories}
                        onChange={(e) => setTerritories(e.target.value)}
                        placeholder="e.g., United States, Canada"
                        className="mt-1.5"
                      />
                    </div>
                    <div>
                      <Label htmlFor="termYears">Term (Years)</Label>
                      <Input
                        id="termYears"
                        type="number"
                        value={termYears}
                        onChange={(e) => setTermYears(Number(e.target.value))}
                        className="mt-1.5"
                      />
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="financial" className="space-y-4 mt-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <Label htmlFor="amount">Deal Amount ($)</Label>
                      <Input
                        id="amount"
                        type="number"
                        value={amount}
                        onChange={(e) => setAmount(Number(e.target.value))}
                        className="mt-1.5"
                      />
                    </div>
                    <div>
                      <Label htmlFor="probability">Probability of Closing (%)</Label>
                      <Input
                        id="probability"
                        type="number"
                        value={probability}
                        onChange={(e) => setProbability(Number(e.target.value))}
                        min={0}
                        max={100}
                        className="mt-1.5"
                      />
                    </div>
                  </div>

                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <Label htmlFor="ownershipPct">Ownership % (if equity)</Label>
                      <Input
                        id="ownershipPct"
                        type="number"
                        value={ownershipPct || ''}
                        onChange={(e) => setOwnershipPct(e.target.value ? Number(e.target.value) : undefined)}
                        placeholder="e.g., 30"
                        className="mt-1.5"
                      />
                    </div>
                    <div>
                      <Label htmlFor="distributionFee">Distribution Fee %</Label>
                      <Input
                        id="distributionFee"
                        type="number"
                        value={distributionFeePct || ''}
                        onChange={(e) => setDistributionFeePct(e.target.value ? Number(e.target.value) : undefined)}
                        placeholder="e.g., 30"
                        className="mt-1.5"
                      />
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="rights" className="space-y-4 mt-4">
                  <div>
                    <Label>Approval Rights Granted to Counterparty</Label>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {APPROVAL_RIGHTS.map((right) => (
                        <button
                          key={right}
                          onClick={() => toggleApprovalRight(right)}
                          className={`px-3 py-1.5 rounded-full text-sm transition-all ${
                            approvalRights.includes(right)
                              ? 'bg-red-100 text-red-700 border border-red-300'
                              : 'bg-gray-100 text-gray-600 border border-gray-200 hover:bg-gray-200'
                          }`}
                        >
                          {right.replace('_', ' ')}
                        </button>
                      ))}
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      Each approval right granted reduces your control score
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      id="mfnClause"
                      checked={mfnClause}
                      onChange={(e) => setMfnClause(e.target.checked)}
                      className="h-4 w-4 rounded border-gray-300"
                    />
                    <div>
                      <Label htmlFor="mfnClause" className="cursor-pointer">
                        Most Favored Nation (MFN) Clause
                      </Label>
                      <p className="text-xs text-gray-500">
                        Creates risk - must match better terms offered elsewhere
                      </p>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>

              <Button
                className="w-full"
                size="lg"
                onClick={handleCreateDeal}
                disabled={loading || !dealName || !counterpartyName}
              >
                {loading ? (
                  <>
                    <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Deal
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Error Display */}
        {error && (
          <Card className="border-red-300 bg-red-50">
            <CardContent className="pt-6">
              <p className="text-red-700 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4" />
                {error}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Deals List */}
        <Card>
          <CardHeader>
            <CardTitle>Active Deals</CardTitle>
            <CardDescription>
              {deals.length} deal{deals.length !== 1 ? 's' : ''} in portfolio
            </CardDescription>
          </CardHeader>
          <CardContent>
            {deals.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No deals yet. Create your first deal to get started.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {deals.map((deal) => (
                  <div
                    key={deal.deal_id}
                    className="p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-all"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold text-lg">{deal.deal_name}</h3>
                        <p className="text-sm text-gray-500">
                          {deal.counterparty_name} • {deal.deal_type.replace('_', ' ')}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-lg">
                          {formatCurrency(deal.amount)}
                        </div>
                        <div className="text-sm text-gray-500">
                          {formatPercentage(deal.probability_of_closing)} likely
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 grid grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Control Impact</span>
                        <div className={`font-medium ${deal.control_impact_score < 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {deal.control_impact_score > 0 ? '+' : ''}{deal.control_impact_score}
                        </div>
                      </div>
                      <div>
                        <span className="text-gray-500">Ownership Impact</span>
                        <div className={`font-medium ${deal.ownership_impact_score < 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {deal.ownership_impact_score > 0 ? '+' : ''}{deal.ownership_impact_score}
                        </div>
                      </div>
                      <div>
                        <span className="text-gray-500">Optionality</span>
                        <div className="font-medium">{deal.optionality_score}</div>
                      </div>
                      <div>
                        <span className="text-gray-500">Net Amount</span>
                        <div className="font-medium">{formatCurrency(deal.net_amount)}</div>
                      </div>
                    </div>

                    {deal.mfn_clause && (
                      <div className="mt-3 flex items-center gap-2 text-amber-600 text-sm">
                        <Shield className="h-4 w-4" />
                        MFN Clause Active
                      </div>
                    )}

                    <div className="mt-4 flex justify-end">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteDeal(deal.deal_id)}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4 mr-1" />
                        Delete
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
