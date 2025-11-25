'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Header } from '@/components/layout/header';
import { scoreOwnership, getDefaultWeights, getDimensionInfo } from '@/lib/api/services';
import type { DealBlockInput, OwnershipScoreResponse, ScoreWeights } from '@/lib/api/types';
import {
  Shield,
  Target,
  Gauge,
  AlertTriangle,
  CheckCircle,
  Info,
  Plus,
  Trash2,
  BarChart3,
  Loader2,
  Lightbulb,
  Scale,
  Lock,
  Unlock,
} from 'lucide-react';

const DIMENSION_ICONS = {
  ownership: Shield,
  control: Lock,
  optionality: Unlock,
  friction: AlertTriangle,
};

const DIMENSION_COLORS = {
  ownership: 'text-blue-500',
  control: 'text-purple-500',
  optionality: 'text-green-500',
  friction: 'text-orange-500',
};

const DEAL_TYPES = [
  { value: 'equity', label: 'Equity' },
  { value: 'presale', label: 'Pre-Sale' },
  { value: 'theatrical_distribution', label: 'Theatrical' },
  { value: 'streamer_license', label: 'Streamer' },
  { value: 'gap_financing', label: 'Gap Financing' },
  { value: 'co_production', label: 'Co-Production' },
];

interface DealForScoring {
  id: string;
  deal_name: string;
  deal_type: string;
  counterparty_name: string;
  amount: number;
  ownership_percentage?: number;
  approval_rights_granted?: string[];
  has_veto_rights?: boolean;
  mfn_clause?: boolean;
  term_years?: number;
  reversion_trigger_years?: number;
  sequel_rights_holder?: string;
}

export default function OwnershipPage() {
  const [deals, setDeals] = useState<DealForScoring[]>([]);
  const [weights, setWeights] = useState<ScoreWeights>({
    ownership: 30,
    control: 30,
    optionality: 25,
    friction: 15,
  });
  const [result, setResult] = useState<OwnershipScoreResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addDeal = () => {
    const newDeal: DealForScoring = {
      id: crypto.randomUUID(),
      deal_name: '',
      deal_type: 'equity',
      counterparty_name: '',
      amount: 0,
      ownership_percentage: 0,
      approval_rights_granted: [],
      has_veto_rights: false,
      mfn_clause: false,
      term_years: 10,
    };
    setDeals([...deals, newDeal]);
  };

  const removeDeal = (id: string) => {
    setDeals(deals.filter((d) => d.id !== id));
  };

  const updateDeal = (id: string, field: keyof DealForScoring, value: any) => {
    setDeals(
      deals.map((d) => (d.id === id ? { ...d, [field]: value } : d))
    );
  };

  const handleScore = async () => {
    if (deals.length === 0) {
      setError('Add at least one deal to score');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const dealBlocks: DealBlockInput[] = deals.map((d) => ({
        deal_name: d.deal_name || 'Unnamed Deal',
        deal_type: d.deal_type,
        counterparty_name: d.counterparty_name || 'Unknown',
        amount: d.amount,
        ownership_percentage: d.ownership_percentage,
        approval_rights_granted: d.approval_rights_granted,
        has_veto_rights: d.has_veto_rights,
        mfn_clause: d.mfn_clause,
        term_years: d.term_years,
        reversion_trigger_years: d.reversion_trigger_years,
        sequel_rights_holder: d.sequel_rights_holder,
      }));

      const response = await scoreOwnership({
        deal_blocks: dealBlocks,
        weights,
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to score ownership');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-green-500';
    if (score >= 50) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getScoreBarColor = (score: number) => {
    if (score >= 70) return 'bg-green-500';
    if (score >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="flex-1 flex flex-col min-h-0">
      <Header
        title="Ownership & Control Scoring"
        description="Engine 4: Analyze strategic ownership position and control dynamics"
      />

      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Weight Configuration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Scale className="h-5 w-5" />
                Dimension Weights
              </CardTitle>
              <CardDescription>
                Configure the importance of each scoring dimension (must sum to 100)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {(Object.keys(weights) as Array<keyof ScoreWeights>).map((dim) => {
                  const Icon = DIMENSION_ICONS[dim];
                  return (
                    <div key={dim} className="space-y-2">
                      <Label className="flex items-center gap-2 capitalize">
                        <Icon className={`h-4 w-4 ${DIMENSION_COLORS[dim]}`} />
                        {dim}
                      </Label>
                      <Input
                        type="number"
                        min={0}
                        max={100}
                        value={weights[dim]}
                        onChange={(e) =>
                          setWeights({ ...weights, [dim]: Number(e.target.value) })
                        }
                      />
                    </div>
                  );
                })}
              </div>
              <p className="text-sm text-muted-foreground mt-2">
                Current sum: {Object.values(weights).reduce((a, b) => a + b, 0)}%
              </p>
            </CardContent>
          </Card>

          {/* Deals Input */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5" />
                    Deals to Analyze
                  </CardTitle>
                  <CardDescription>
                    Add deals to calculate their strategic impact on ownership and control
                  </CardDescription>
                </div>
                <Button onClick={addDeal} variant="outline" size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Deal
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {deals.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Target className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p>No deals added yet</p>
                  <p className="text-sm">Click "Add Deal" to start scoring</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {deals.map((deal, index) => (
                    <div
                      key={deal.id}
                      className="border rounded-lg p-4 space-y-4 bg-muted/30"
                    >
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium">Deal #{index + 1}</h4>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeDeal(deal.id)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="space-y-2">
                          <Label>Deal Name</Label>
                          <Input
                            value={deal.deal_name}
                            onChange={(e) =>
                              updateDeal(deal.id, 'deal_name', e.target.value)
                            }
                            placeholder="e.g., North America Distribution"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Deal Type</Label>
                          <select
                            className="w-full h-10 px-3 rounded-md border border-input bg-background"
                            value={deal.deal_type}
                            onChange={(e) =>
                              updateDeal(deal.id, 'deal_type', e.target.value)
                            }
                          >
                            {DEAL_TYPES.map((type) => (
                              <option key={type.value} value={type.value}>
                                {type.label}
                              </option>
                            ))}
                          </select>
                        </div>
                        <div className="space-y-2">
                          <Label>Counterparty</Label>
                          <Input
                            value={deal.counterparty_name}
                            onChange={(e) =>
                              updateDeal(deal.id, 'counterparty_name', e.target.value)
                            }
                            placeholder="e.g., Major Studios Inc."
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="space-y-2">
                          <Label>Amount ($)</Label>
                          <Input
                            type="number"
                            value={deal.amount}
                            onChange={(e) =>
                              updateDeal(deal.id, 'amount', Number(e.target.value))
                            }
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Ownership %</Label>
                          <Input
                            type="number"
                            min={0}
                            max={100}
                            value={deal.ownership_percentage || 0}
                            onChange={(e) =>
                              updateDeal(
                                deal.id,
                                'ownership_percentage',
                                Number(e.target.value)
                              )
                            }
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Term (Years)</Label>
                          <Input
                            type="number"
                            value={deal.term_years || 10}
                            onChange={(e) =>
                              updateDeal(deal.id, 'term_years', Number(e.target.value))
                            }
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Reversion (Years)</Label>
                          <Input
                            type="number"
                            value={deal.reversion_trigger_years || ''}
                            onChange={(e) =>
                              updateDeal(
                                deal.id,
                                'reversion_trigger_years',
                                e.target.value ? Number(e.target.value) : undefined
                              )
                            }
                            placeholder="Optional"
                          />
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-4">
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={deal.has_veto_rights || false}
                            onChange={(e) =>
                              updateDeal(deal.id, 'has_veto_rights', e.target.checked)
                            }
                            className="rounded"
                          />
                          <span className="text-sm">Has Veto Rights</span>
                        </label>
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={deal.mfn_clause || false}
                            onChange={(e) =>
                              updateDeal(deal.id, 'mfn_clause', e.target.checked)
                            }
                            className="rounded"
                          />
                          <span className="text-sm">MFN Clause</span>
                        </label>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {error && (
                <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md text-red-700 dark:text-red-400 flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4" />
                  {error}
                </div>
              )}

              <div className="mt-6 flex justify-end">
                <Button onClick={handleScore} disabled={loading || deals.length === 0}>
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <BarChart3 className="h-4 w-4 mr-2" />
                      Score Ownership
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Results */}
          {result && (
            <>
              {/* Score Overview */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Gauge className="h-5 w-5" />
                    Strategic Position Scores
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    {/* Composite Score - Larger */}
                    <div className="col-span-2 md:col-span-1 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg p-4 text-white">
                      <p className="text-sm opacity-80">Composite Score</p>
                      <p className="text-4xl font-bold">
                        {result.composite_score.toFixed(1)}
                      </p>
                      <p className="text-xs opacity-70 mt-1">Overall Position</p>
                    </div>

                    {/* Individual Dimensions */}
                    {[
                      { key: 'ownership_score', label: 'Ownership', icon: Shield },
                      { key: 'control_score', label: 'Control', icon: Lock },
                      { key: 'optionality_score', label: 'Optionality', icon: Unlock },
                      { key: 'friction_score', label: 'Friction', icon: AlertTriangle },
                    ].map(({ key, label, icon: Icon }) => {
                      const score = result[key as keyof OwnershipScoreResponse] as number;
                      const isInverted = key === 'friction_score';
                      const displayScore = isInverted ? 100 - score : score;
                      return (
                        <div key={key} className="bg-muted rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <Icon className={`h-4 w-4 ${getScoreColor(displayScore)}`} />
                            <span className="text-sm text-muted-foreground">{label}</span>
                          </div>
                          <p className={`text-2xl font-bold ${getScoreColor(displayScore)}`}>
                            {score.toFixed(1)}
                          </p>
                          <div className="mt-2 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${getScoreBarColor(displayScore)} transition-all`}
                              style={{ width: `${score}%` }}
                            />
                          </div>
                          {isInverted && (
                            <p className="text-xs text-muted-foreground mt-1">
                              (Lower is better)
                            </p>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              {/* Flags */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className={result.flags.has_mfn_risk ? 'border-orange-500' : ''}>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      {result.flags.has_mfn_risk ? (
                        <AlertTriangle className="h-8 w-8 text-orange-500" />
                      ) : (
                        <CheckCircle className="h-8 w-8 text-green-500" />
                      )}
                      <div>
                        <p className="font-medium">MFN Risk</p>
                        <p className="text-sm text-muted-foreground">
                          {result.flags.has_mfn_risk
                            ? 'MFN clause detected - may limit deal flexibility'
                            : 'No MFN clauses present'}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className={result.flags.has_control_concentration ? 'border-red-500' : ''}>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      {result.flags.has_control_concentration ? (
                        <AlertTriangle className="h-8 w-8 text-red-500" />
                      ) : (
                        <CheckCircle className="h-8 w-8 text-green-500" />
                      )}
                      <div>
                        <p className="font-medium">Control Concentration</p>
                        <p className="text-sm text-muted-foreground">
                          {result.flags.has_control_concentration
                            ? 'Control concentrated with single party'
                            : 'Control well distributed'}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className={result.flags.has_reversion_opportunity ? 'border-green-500' : ''}>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      {result.flags.has_reversion_opportunity ? (
                        <CheckCircle className="h-8 w-8 text-green-500" />
                      ) : (
                        <Info className="h-8 w-8 text-gray-400" />
                      )}
                      <div>
                        <p className="font-medium">Reversion Opportunity</p>
                        <p className="text-sm text-muted-foreground">
                          {result.flags.has_reversion_opportunity
                            ? 'Rights reversion opportunity exists'
                            : 'No reversion triggers set'}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Recommendations */}
              {result.recommendations.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Lightbulb className="h-5 w-5 text-yellow-500" />
                      Strategic Recommendations
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {result.recommendations.map((rec, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {/* Impact Details */}
              {result.impacts.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Impact Analysis</CardTitle>
                    <CardDescription>
                      Detailed breakdown of how each factor affects your position
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {result.impacts.map((impact, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between p-3 bg-muted rounded-lg"
                        >
                          <div className="flex-1">
                            <p className="font-medium">{impact.source}</p>
                            <p className="text-sm text-muted-foreground">
                              {impact.explanation}
                            </p>
                          </div>
                          <div className="text-right">
                            <span
                              className={`inline-block px-2 py-1 rounded text-sm font-medium ${
                                impact.impact > 0
                                  ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                                  : impact.impact < 0
                                  ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
                                  : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
                              }`}
                            >
                              {impact.impact > 0 ? '+' : ''}
                              {impact.impact.toFixed(1)}
                            </span>
                            <p className="text-xs text-muted-foreground mt-1 capitalize">
                              {impact.dimension}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
