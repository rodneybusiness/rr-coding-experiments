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
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Briefcase,
  Calculator,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Loader2,
  ArrowRight,
  Target,
  BarChart3,
  Shield,
  Lightbulb,
} from 'lucide-react';
import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';
import { listCapitalPrograms, generateScenarios } from '@/lib/api/services';
import type { CapitalProgramResponse, ScenarioGenerationResponse, Scenario } from '@/lib/api/types';
import { formatCurrency, formatPercentage } from '@/lib/utils';

interface ConstraintViolation {
  constraint_name: string;
  constraint_type: 'hard' | 'soft';
  current_value: string;
  limit_value: string;
  description: string;
  is_blocking: boolean;
}

interface ProgramEvaluation {
  program_id: string;
  program_name: string;
  passes_constraints: boolean;
  violations: ConstraintViolation[];
  portfolio_fit_score: number;
  recommendations: string[];
  selected_source_id?: string;
  source_selection_reason?: string;
}

interface ScenarioWithProgramFit extends Scenario {
  program_evaluation?: ProgramEvaluation;
}

export default function ProgramEvaluatorPage() {
  const [programs, setPrograms] = useState<CapitalProgramResponse[]>([]);
  const [selectedProgramId, setSelectedProgramId] = useState<string>('');
  const [projectName, setProjectName] = useState('New Animation Project');
  const [projectBudget, setProjectBudget] = useState(30000000);
  const [requestedAmount, setRequestedAmount] = useState(10000000);
  const [jurisdiction, setJurisdiction] = useState('United States');
  const [genre, setGenre] = useState('Animation');
  const [scenarios, setScenarios] = useState<ScenarioWithProgramFit[]>([]);
  const [loading, setLoading] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPrograms();
  }, []);

  const loadPrograms = async () => {
    setLoading(true);
    try {
      const response = await listCapitalPrograms();
      setPrograms(response.programs);
      if (response.programs.length > 0) {
        setSelectedProgramId(response.programs[0].program_id);
      }
    } catch (err) {
      setError('Failed to load capital programs');
    } finally {
      setLoading(false);
    }
  };

  const evaluateForProgram = async () => {
    if (!selectedProgramId) {
      setError('Please select a capital program');
      return;
    }

    setEvaluating(true);
    setError(null);

    try {
      // Generate scenarios
      const scenarioResponse: ScenarioGenerationResponse = await generateScenarios({
        project_id: `proj_eval_${Date.now()}`,
        project_name: projectName,
        project_budget: projectBudget,
        waterfall_id: `wf_eval_${Date.now()}`,
        num_scenarios: 4,
      });

      // Find the selected program
      const selectedProgram = programs.find((p) => p.program_id === selectedProgramId);

      // Evaluate each scenario against program constraints
      const evaluatedScenarios: ScenarioWithProgramFit[] = scenarioResponse.scenarios.map(
        (scenario) => {
          const evaluation = evaluateScenarioForProgram(
            scenario,
            selectedProgram!,
            requestedAmount,
            jurisdiction,
            genre
          );
          return {
            ...scenario,
            program_evaluation: evaluation,
          };
        }
      );

      setScenarios(evaluatedScenarios);
    } catch (err) {
      setError('Failed to evaluate scenarios');
    } finally {
      setEvaluating(false);
    }
  };

  const evaluateScenarioForProgram = (
    scenario: Scenario,
    program: CapitalProgramResponse,
    requested: number,
    projectJurisdiction: string,
    projectGenre: string
  ): ProgramEvaluation => {
    const violations: ConstraintViolation[] = [];
    const recommendations: string[] = [];
    let portfolioFitScore = 80;

    // Check available capital
    const available = program.metrics.total_available;
    if (requested > available) {
      violations.push({
        constraint_name: 'Available Capital',
        constraint_type: 'hard',
        current_value: formatCurrency(requested),
        limit_value: formatCurrency(available),
        description: 'Requested amount exceeds available capital',
        is_blocking: true,
      });
      portfolioFitScore -= 30;
    }

    // Check max single project percentage
    const maxProjectPct = program.constraints?.max_single_project_pct || 20;
    const projectPct = (requested / program.target_size) * 100;
    if (projectPct > maxProjectPct) {
      violations.push({
        constraint_name: 'Max Single Project %',
        constraint_type: 'hard',
        current_value: `${projectPct.toFixed(1)}%`,
        limit_value: `${maxProjectPct}%`,
        description: 'Project would exceed concentration limit',
        is_blocking: true,
      });
      portfolioFitScore -= 25;
    }

    // Check min/max budget constraints
    const minBudget = program.constraints?.min_project_budget || 0;
    const maxBudget = program.constraints?.max_project_budget || Infinity;
    if (projectBudget < minBudget) {
      violations.push({
        constraint_name: 'Minimum Budget',
        constraint_type: 'hard',
        current_value: formatCurrency(projectBudget),
        limit_value: formatCurrency(minBudget),
        description: 'Project budget below minimum',
        is_blocking: true,
      });
      portfolioFitScore -= 20;
    }
    if (projectBudget > maxBudget) {
      violations.push({
        constraint_name: 'Maximum Budget',
        constraint_type: 'hard',
        current_value: formatCurrency(projectBudget),
        limit_value: formatCurrency(maxBudget),
        description: 'Project budget exceeds maximum',
        is_blocking: true,
      });
      portfolioFitScore -= 20;
    }

    // Check jurisdiction restrictions
    const prohibitedJurisdictions = program.constraints?.prohibited_jurisdictions || [];
    const requiredJurisdictions = program.constraints?.required_jurisdictions || [];
    if (prohibitedJurisdictions.includes(projectJurisdiction)) {
      violations.push({
        constraint_name: 'Prohibited Jurisdiction',
        constraint_type: 'hard',
        current_value: projectJurisdiction,
        limit_value: 'Not allowed',
        description: 'Jurisdiction is prohibited by program',
        is_blocking: true,
      });
      portfolioFitScore -= 25;
    }
    if (requiredJurisdictions.length > 0 && !requiredJurisdictions.includes(projectJurisdiction)) {
      violations.push({
        constraint_name: 'Required Jurisdiction',
        constraint_type: 'soft',
        current_value: projectJurisdiction,
        limit_value: requiredJurisdictions.join(', '),
        description: 'Project not in required jurisdiction',
        is_blocking: false,
      });
      portfolioFitScore -= 10;
    }

    // Check genre restrictions
    const prohibitedGenres = program.constraints?.prohibited_genres || [];
    const requiredGenres = program.constraints?.required_genres || [];
    if (prohibitedGenres.includes(projectGenre)) {
      violations.push({
        constraint_name: 'Prohibited Genre',
        constraint_type: 'hard',
        current_value: projectGenre,
        limit_value: 'Not allowed',
        description: 'Genre is prohibited by program',
        is_blocking: true,
      });
      portfolioFitScore -= 25;
    }
    if (requiredGenres.length > 0 && !requiredGenres.includes(projectGenre)) {
      violations.push({
        constraint_name: 'Required Genre',
        constraint_type: 'soft',
        current_value: projectGenre,
        limit_value: requiredGenres.join(', '),
        description: 'Project not in required genre',
        is_blocking: false,
      });
      portfolioFitScore -= 10;
    }

    // Generate recommendations
    if (violations.length === 0) {
      recommendations.push('Project passes all constraints - ready for allocation');
    } else {
      const hardViolations = violations.filter((v) => v.constraint_type === 'hard');
      if (hardViolations.length > 0) {
        recommendations.push('Address hard constraint violations before proceeding');
        if (hardViolations.some((v) => v.constraint_name === 'Available Capital')) {
          recommendations.push('Consider reducing requested amount or adding capital sources');
        }
      } else {
        recommendations.push(
          'Soft constraint violations noted - proceed with caution'
        );
      }
    }

    // Add scenario-specific recommendations
    if (scenario.metrics?.equity_irr && Number(scenario.metrics.equity_irr) > 25) {
      recommendations.push('High IRR scenario aligns with fund return objectives');
      portfolioFitScore += 5;
    }
    if (scenario.metrics?.tax_incentive_rate && Number(scenario.metrics.tax_incentive_rate) > 15) {
      recommendations.push('Strong tax incentive capture reduces capital at risk');
      portfolioFitScore += 5;
    }

    // Find best source
    let selectedSourceId: string | undefined;
    let sourceReason = 'No sources available';
    if (program.sources.length > 0) {
      const availableSources = program.sources.filter(
        (s) => s.available_amount >= requested
      );
      if (availableSources.length > 0) {
        // Select source with lowest utilization
        const bestSource = availableSources.reduce((prev, curr) =>
          curr.utilization_rate < prev.utilization_rate ? curr : prev
        );
        selectedSourceId = bestSource.source_id;
        sourceReason = `${bestSource.source_name} selected - lowest utilization (${bestSource.utilization_rate.toFixed(0)}%)`;
      } else {
        sourceReason = 'No single source has sufficient available capital';
      }
    }

    const passesConstraints = !violations.some((v) => v.is_blocking);

    return {
      program_id: program.program_id,
      program_name: program.program_name,
      passes_constraints: passesConstraints,
      violations,
      portfolio_fit_score: Math.max(0, Math.min(100, portfolioFitScore)),
      recommendations,
      selected_source_id: selectedSourceId,
      source_selection_reason: sourceReason,
    };
  };

  const getConstraintIcon = (type: 'hard' | 'soft', isBlocking: boolean) => {
    if (isBlocking) {
      return <XCircle className="h-4 w-4 text-red-500" />;
    }
    return type === 'hard' ? (
      <AlertTriangle className="h-4 w-4 text-amber-500" />
    ) : (
      <AlertTriangle className="h-4 w-4 text-yellow-500" />
    );
  };

  const selectedProgram = programs.find((p) => p.program_id === selectedProgramId);

  return (
    <div className="flex flex-col">
      <Header
        title="Scenario Program Evaluator"
        description="Evaluate capital stack scenarios against program constraints"
      />

      <div className="p-6 space-y-6">
        {/* Input Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calculator className="h-5 w-5" />
              Evaluation Configuration
            </CardTitle>
            <CardDescription>
              Configure project details and select a capital program
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {/* Capital Program Selection */}
              <div className="space-y-2">
                <Label>Capital Program</Label>
                <Select
                  value={selectedProgramId}
                  onValueChange={setSelectedProgramId}
                  disabled={loading}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a program" />
                  </SelectTrigger>
                  <SelectContent>
                    {programs.map((p) => (
                      <SelectItem key={p.program_id} value={p.program_id}>
                        {p.program_name} ({formatCurrency(p.metrics.total_available)} available)
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Project Name */}
              <div className="space-y-2">
                <Label>Project Name</Label>
                <Input
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="Project name"
                />
              </div>

              {/* Project Budget */}
              <div className="space-y-2">
                <Label>Project Budget ($)</Label>
                <Input
                  type="number"
                  value={projectBudget}
                  onChange={(e) => setProjectBudget(parseInt(e.target.value) || 0)}
                  min={0}
                />
              </div>

              {/* Requested Amount */}
              <div className="space-y-2">
                <Label>Requested Allocation ($)</Label>
                <Input
                  type="number"
                  value={requestedAmount}
                  onChange={(e) => setRequestedAmount(parseInt(e.target.value) || 0)}
                  min={0}
                />
              </div>

              {/* Jurisdiction */}
              <div className="space-y-2">
                <Label>Jurisdiction</Label>
                <Select value={jurisdiction} onValueChange={setJurisdiction}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="United States">United States</SelectItem>
                    <SelectItem value="Canada">Canada</SelectItem>
                    <SelectItem value="United Kingdom">United Kingdom</SelectItem>
                    <SelectItem value="Ireland">Ireland</SelectItem>
                    <SelectItem value="France">France</SelectItem>
                    <SelectItem value="Germany">Germany</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Genre */}
              <div className="space-y-2">
                <Label>Genre</Label>
                <Select value={genre} onValueChange={setGenre}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Animation">Animation</SelectItem>
                    <SelectItem value="Action">Action</SelectItem>
                    <SelectItem value="Comedy">Comedy</SelectItem>
                    <SelectItem value="Drama">Drama</SelectItem>
                    <SelectItem value="Family">Family</SelectItem>
                    <SelectItem value="Sci-Fi">Sci-Fi</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="mt-6">
              <Button
                onClick={evaluateForProgram}
                disabled={evaluating || !selectedProgramId}
                className="w-full md:w-auto"
              >
                {evaluating ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Evaluating...
                  </>
                ) : (
                  <>
                    <Target className="h-4 w-4 mr-2" />
                    Evaluate Scenarios for Program
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Program Summary */}
        {selectedProgram && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Briefcase className="h-5 w-5" />
                {selectedProgram.program_name}
              </CardTitle>
              <CardDescription>
                {selectedProgram.program_type.replace('_', ' ').toUpperCase()}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-4">
                <div>
                  <p className="text-sm text-muted-foreground">Target Size</p>
                  <p className="text-lg font-semibold">
                    {formatCurrency(selectedProgram.target_size)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Committed</p>
                  <p className="text-lg font-semibold">
                    {formatCurrency(selectedProgram.metrics.total_committed)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Available</p>
                  <p className="text-lg font-semibold text-green-600">
                    {formatCurrency(selectedProgram.metrics.total_available)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Deployment Rate</p>
                  <p className="text-lg font-semibold">
                    {selectedProgram.metrics.deployment_rate.toFixed(1)}%
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Scenario Results */}
        {scenarios.length > 0 && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold">Evaluation Results</h2>

            {/* Comparison Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Scenario Comparison
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={scenarios.map((s) => ({
                        name: s.scenario_name,
                        'Portfolio Fit': s.program_evaluation?.portfolio_fit_score || 0,
                        'Optimization Score': Number(s.optimization_score),
                        IRR: Number(s.metrics?.equity_irr || 0),
                      }))}
                    >
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="Portfolio Fit" fill="#3b82f6" />
                      <Bar dataKey="Optimization Score" fill="#10b981" />
                      <Bar dataKey="IRR" fill="#f59e0b" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Scenario Cards */}
            <div className="grid gap-6 md:grid-cols-2">
              {scenarios.map((scenario) => (
                <Card
                  key={scenario.scenario_id}
                  className={`${
                    scenario.program_evaluation?.passes_constraints
                      ? 'border-green-200'
                      : 'border-red-200'
                  }`}
                >
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{scenario.scenario_name}</CardTitle>
                      {scenario.program_evaluation?.passes_constraints ? (
                        <span className="flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                          <CheckCircle2 className="h-4 w-4" />
                          Eligible
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 rounded-full text-sm">
                          <XCircle className="h-4 w-4" />
                          Blocked
                        </span>
                      )}
                    </div>
                    <CardDescription>
                      Portfolio Fit Score:{' '}
                      <span className="font-semibold">
                        {scenario.program_evaluation?.portfolio_fit_score.toFixed(0)}/100
                      </span>
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Metrics */}
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">IRR</p>
                        <p className="font-semibold">
                          {Number(scenario.metrics?.equity_irr || 0).toFixed(1)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Tax Rate</p>
                        <p className="font-semibold">
                          {Number(scenario.metrics?.tax_incentive_rate || 0).toFixed(1)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Score</p>
                        <p className="font-semibold">
                          {Number(scenario.optimization_score).toFixed(0)}
                        </p>
                      </div>
                    </div>

                    {/* Violations */}
                    {scenario.program_evaluation &&
                      scenario.program_evaluation.violations.length > 0 && (
                        <div className="space-y-2">
                          <p className="text-sm font-medium">Constraint Violations:</p>
                          {scenario.program_evaluation.violations.map((v, idx) => (
                            <div
                              key={idx}
                              className={`flex items-start gap-2 p-2 rounded text-sm ${
                                v.is_blocking ? 'bg-red-50' : 'bg-amber-50'
                              }`}
                            >
                              {getConstraintIcon(v.constraint_type, v.is_blocking)}
                              <div>
                                <p className="font-medium">{v.constraint_name}</p>
                                <p className="text-muted-foreground">
                                  {v.current_value} (limit: {v.limit_value})
                                </p>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                    {/* Source Selection */}
                    {scenario.program_evaluation?.source_selection_reason && (
                      <div className="p-2 bg-blue-50 rounded text-sm">
                        <p className="font-medium text-blue-700">Source Selection:</p>
                        <p className="text-blue-600">
                          {scenario.program_evaluation.source_selection_reason}
                        </p>
                      </div>
                    )}

                    {/* Recommendations */}
                    {scenario.program_evaluation &&
                      scenario.program_evaluation.recommendations.length > 0 && (
                        <div className="space-y-1">
                          <p className="text-sm font-medium flex items-center gap-1">
                            <Lightbulb className="h-4 w-4" />
                            Recommendations:
                          </p>
                          <ul className="text-sm text-muted-foreground space-y-1">
                            {scenario.program_evaluation.recommendations.map((r, idx) => (
                              <li key={idx} className="flex items-start gap-2">
                                <ArrowRight className="h-4 w-4 mt-0.5 flex-shrink-0" />
                                {r}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {scenarios.length === 0 && !loading && !evaluating && (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Shield className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No Evaluations Yet</h3>
              <p className="text-sm text-muted-foreground text-center max-w-md">
                Configure your project details above and click "Evaluate Scenarios for
                Program" to see how different capital stack scenarios fit your selected
                capital program.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
