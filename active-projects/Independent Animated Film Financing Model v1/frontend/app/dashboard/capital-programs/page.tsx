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
  Building2,
  Plus,
  Trash2,
  DollarSign,
  TrendingUp,
  Briefcase,
  PiggyBank,
  Target,
  AlertTriangle,
  CheckCircle,
  Loader2,
  BarChart3,
  Wallet,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import { formatCurrency, formatPercentage } from '@/lib/utils';
import {
  createCapitalProgram,
  listCapitalPrograms,
  deleteCapitalProgram,
  allocateCapital,
  getPortfolioMetrics,
} from '@/lib/api/services';
import type {
  CapitalProgramResponse,
  CapitalProgramInput,
  ProgramType,
  AllocationRequestInput,
} from '@/lib/api/types';

const PROGRAM_TYPES: { value: ProgramType; label: string; icon: typeof Building2 }[] = [
  { value: 'internal_pool', label: 'Internal Pool', icon: PiggyBank },
  { value: 'external_fund', label: 'External Fund', icon: Briefcase },
  { value: 'private_equity', label: 'Private Equity', icon: TrendingUp },
  { value: 'family_office', label: 'Family Office', icon: Building2 },
  { value: 'output_deal', label: 'Output Deal', icon: Target },
  { value: 'first_look', label: 'First Look', icon: Target },
  { value: 'spv', label: 'SPV', icon: Wallet },
  { value: 'tax_credit_fund', label: 'Tax Credit Fund', icon: DollarSign },
];

const STATUS_COLORS: Record<string, string> = {
  prospective: 'bg-gray-100 text-gray-700',
  in_negotiation: 'bg-yellow-100 text-yellow-700',
  active: 'bg-green-100 text-green-700',
  fully_deployed: 'bg-blue-100 text-blue-700',
  winding_down: 'bg-orange-100 text-orange-700',
  closed: 'bg-gray-200 text-gray-500',
};

export default function CapitalProgramsPage() {
  const [programs, setPrograms] = useState<CapitalProgramResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [selectedProgram, setSelectedProgram] = useState<CapitalProgramResponse | null>(null);

  // Form state
  const [programName, setProgramName] = useState('');
  const [programType, setProgramType] = useState<ProgramType>('external_fund');
  const [targetSize, setTargetSize] = useState(50000000);
  const [managerName, setManagerName] = useState('');
  const [managementFeePct, setManagementFeePct] = useState(2.0);
  const [carryPercentage, setCarryPercentage] = useState(20.0);
  const [hurdleRate, setHurdleRate] = useState(8.0);
  const [vintageYear, setVintageYear] = useState(new Date().getFullYear());
  const [description, setDescription] = useState('');

  // Allocation form state
  const [showAllocateForm, setShowAllocateForm] = useState(false);
  const [allocProjectId, setAllocProjectId] = useState('');
  const [allocProjectName, setAllocProjectName] = useState('');
  const [allocAmount, setAllocAmount] = useState(5000000);
  const [allocBudget, setAllocBudget] = useState(30000000);

  useEffect(() => {
    loadPrograms();
  }, []);

  const loadPrograms = async () => {
    try {
      const response = await listCapitalPrograms();
      setPrograms(response.programs || []);
    } catch (err) {
      setPrograms([]);
    }
  };

  const handleCreateProgram = async () => {
    setLoading(true);
    setError(null);

    try {
      const program: CapitalProgramInput = {
        program_name: programName,
        program_type: programType,
        target_size: targetSize,
        manager_name: managerName || undefined,
        management_fee_pct: managementFeePct,
        carry_percentage: carryPercentage,
        hurdle_rate: hurdleRate,
        vintage_year: vintageYear,
        description: description || undefined,
      };

      await createCapitalProgram(program);
      await loadPrograms();
      setShowForm(false);
      resetForm();
    } catch (err: any) {
      setError(err.message || 'Failed to create program');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProgram = async (programId: string) => {
    try {
      await deleteCapitalProgram(programId);
      await loadPrograms();
      if (selectedProgram?.program_id === programId) {
        setSelectedProgram(null);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to delete program');
    }
  };

  const handleAllocateCapital = async () => {
    if (!selectedProgram) return;
    setLoading(true);
    setError(null);

    try {
      const allocation: AllocationRequestInput = {
        project_id: allocProjectId || `proj_${Date.now()}`,
        project_name: allocProjectName,
        requested_amount: allocAmount,
        project_budget: allocBudget,
      };

      await allocateCapital(selectedProgram.program_id, allocation);
      await loadPrograms();
      setShowAllocateForm(false);
      resetAllocForm();
    } catch (err: any) {
      setError(err.message || 'Failed to allocate capital');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setProgramName('');
    setProgramType('external_fund');
    setTargetSize(50000000);
    setManagerName('');
    setManagementFeePct(2.0);
    setCarryPercentage(20.0);
    setHurdleRate(8.0);
    setVintageYear(new Date().getFullYear());
    setDescription('');
  };

  const resetAllocForm = () => {
    setAllocProjectId('');
    setAllocProjectName('');
    setAllocAmount(5000000);
    setAllocBudget(30000000);
  };

  const totalCommitted = programs.reduce((sum, p) => sum + (p.metrics?.total_committed || 0), 0);
  const totalDeployed = programs.reduce((sum, p) => sum + (p.metrics?.total_allocated || 0), 0);
  const totalAvailable = programs.reduce((sum, p) => sum + (p.metrics?.total_available || 0), 0);
  const activeProjects = programs.reduce((sum, p) => sum + (p.metrics?.num_active_projects || 0), 0);

  return (
    <div className="flex flex-col">
      <Header
        title="Capital Programs"
        description="Engine 5: Manage capital vehicles, allocations, and portfolio constraints"
      />

      <div className="p-6 space-y-6">
        {/* Summary Cards */}
        <div className="grid gap-6 md:grid-cols-4">
          <Card className="bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-blue-100">
                Total Programs
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{programs.length}</div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-500 to-emerald-600 text-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-green-100">
                Total Committed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {formatCurrency(totalCommitted)}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-500 to-violet-600 text-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-purple-100">
                Deployed Capital
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {formatCurrency(totalDeployed)}
              </div>
              <div className="text-sm text-purple-100 mt-1">
                {totalCommitted > 0 ? formatPercentage((totalDeployed / totalCommitted) * 100) : '0%'} deployed
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
                {showForm ? 'Cancel' : 'New Program'}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Create Program Form */}
        {showForm && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Briefcase className="h-5 w-5" />
                Create Capital Program
              </CardTitle>
              <CardDescription>
                Define a new capital vehicle with terms and constraints
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <Tabs defaultValue="basic">
                <TabsList>
                  <TabsTrigger value="basic">Basic Info</TabsTrigger>
                  <TabsTrigger value="terms">Fund Terms</TabsTrigger>
                </TabsList>

                <TabsContent value="basic" className="space-y-4 mt-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <Label htmlFor="programName">Program Name</Label>
                      <Input
                        id="programName"
                        value={programName}
                        onChange={(e) => setProgramName(e.target.value)}
                        placeholder="e.g., Animation Fund I"
                        className="mt-1.5"
                      />
                    </div>
                    <div>
                      <Label htmlFor="managerName">Manager</Label>
                      <Input
                        id="managerName"
                        value={managerName}
                        onChange={(e) => setManagerName(e.target.value)}
                        placeholder="e.g., Film Finance Partners"
                        className="mt-1.5"
                      />
                    </div>
                  </div>

                  <div>
                    <Label>Program Type</Label>
                    <div className="grid gap-2 md:grid-cols-4 mt-1.5">
                      {PROGRAM_TYPES.map((type) => (
                        <button
                          key={type.value}
                          onClick={() => setProgramType(type.value)}
                          className={`p-3 rounded-lg border text-left transition-all ${
                            programType === type.value
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
                      <Label htmlFor="targetSize">Target Size ($)</Label>
                      <Input
                        id="targetSize"
                        type="number"
                        value={targetSize}
                        onChange={(e) => setTargetSize(Number(e.target.value))}
                        className="mt-1.5"
                      />
                    </div>
                    <div>
                      <Label htmlFor="vintageYear">Vintage Year</Label>
                      <Input
                        id="vintageYear"
                        type="number"
                        value={vintageYear}
                        onChange={(e) => setVintageYear(Number(e.target.value))}
                        className="mt-1.5"
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="description">Description</Label>
                    <Input
                      id="description"
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      placeholder="Brief description of the program"
                      className="mt-1.5"
                    />
                  </div>
                </TabsContent>

                <TabsContent value="terms" className="space-y-4 mt-4">
                  <div className="grid gap-4 md:grid-cols-3">
                    <div>
                      <Label htmlFor="managementFee">Management Fee (%)</Label>
                      <Input
                        id="managementFee"
                        type="number"
                        step="0.1"
                        value={managementFeePct}
                        onChange={(e) => setManagementFeePct(Number(e.target.value))}
                        className="mt-1.5"
                      />
                    </div>
                    <div>
                      <Label htmlFor="carry">Carried Interest (%)</Label>
                      <Input
                        id="carry"
                        type="number"
                        step="0.5"
                        value={carryPercentage}
                        onChange={(e) => setCarryPercentage(Number(e.target.value))}
                        className="mt-1.5"
                      />
                    </div>
                    <div>
                      <Label htmlFor="hurdle">Hurdle Rate (%)</Label>
                      <Input
                        id="hurdle"
                        type="number"
                        step="0.5"
                        value={hurdleRate}
                        onChange={(e) => setHurdleRate(Number(e.target.value))}
                        className="mt-1.5"
                      />
                    </div>
                  </div>
                  <p className="text-sm text-gray-500">
                    Standard fund terms: 2% management fee, 20% carry above 8% hurdle
                  </p>
                </TabsContent>
              </Tabs>

              <Button
                className="w-full"
                size="lg"
                onClick={handleCreateProgram}
                disabled={loading || !programName || targetSize <= 0}
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Program
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

        {/* Programs Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {programs.length === 0 ? (
            <Card className="col-span-full">
              <CardContent className="py-12 text-center text-gray-500">
                <Briefcase className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No capital programs yet. Create your first program to get started.</p>
              </CardContent>
            </Card>
          ) : (
            programs.map((program) => (
              <Card
                key={program.program_id}
                className={`cursor-pointer transition-all hover:shadow-lg ${
                  selectedProgram?.program_id === program.program_id
                    ? 'ring-2 ring-blue-500'
                    : ''
                }`}
                onClick={() => setSelectedProgram(program)}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{program.program_name}</CardTitle>
                      <CardDescription className="mt-1">
                        {program.program_type.replace('_', ' ')}
                        {program.vintage_year && ` • ${program.vintage_year}`}
                      </CardDescription>
                    </div>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        STATUS_COLORS[program.status] || STATUS_COLORS.prospective
                      }`}
                    >
                      {program.status.replace('_', ' ')}
                    </span>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Target Size</span>
                      <span className="font-medium">{formatCurrency(program.target_size)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Committed</span>
                      <span className="font-medium">
                        {formatCurrency(program.metrics?.total_committed || 0)}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Deployed</span>
                      <span className="font-medium">
                        {formatCurrency(program.metrics?.total_allocated || 0)}
                      </span>
                    </div>

                    {/* Deployment Progress Bar */}
                    <div className="mt-2">
                      <div className="flex justify-between text-xs text-gray-500 mb-1">
                        <span>Deployment Progress</span>
                        <span>
                          {formatPercentage(program.metrics?.deployment_rate || 0)}
                        </span>
                      </div>
                      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 transition-all"
                          style={{
                            width: `${Math.min(program.metrics?.deployment_rate || 0, 100)}%`,
                          }}
                        />
                      </div>
                    </div>

                    <div className="pt-2 flex justify-between items-center">
                      <span className="text-sm text-gray-500">
                        {program.metrics?.num_active_projects || 0} active projects
                      </span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteProgram(program.program_id);
                        }}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Selected Program Details */}
        {selectedProgram && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    {selectedProgram.program_name} - Details
                  </CardTitle>
                  <CardDescription>
                    {selectedProgram.manager_name && `Managed by ${selectedProgram.manager_name}`}
                  </CardDescription>
                </div>
                <Button
                  onClick={() => setShowAllocateForm(!showAllocateForm)}
                  variant="outline"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Allocate Capital
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center gap-2 text-blue-700 mb-1">
                    <DollarSign className="h-4 w-4" />
                    <span className="text-sm">Available</span>
                  </div>
                  <p className="text-xl font-bold text-blue-900">
                    {formatCurrency(selectedProgram.metrics?.total_available || 0)}
                  </p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <div className="flex items-center gap-2 text-green-700 mb-1">
                    <ArrowUpRight className="h-4 w-4" />
                    <span className="text-sm">Recouped</span>
                  </div>
                  <p className="text-xl font-bold text-green-900">
                    {formatCurrency(selectedProgram.metrics?.total_recouped || 0)}
                  </p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <div className="flex items-center gap-2 text-purple-700 mb-1">
                    <TrendingUp className="h-4 w-4" />
                    <span className="text-sm">Profit</span>
                  </div>
                  <p className="text-xl font-bold text-purple-900">
                    {formatCurrency(selectedProgram.metrics?.total_profit || 0)}
                  </p>
                </div>
                <div className="p-4 bg-orange-50 rounded-lg">
                  <div className="flex items-center gap-2 text-orange-700 mb-1">
                    <Target className="h-4 w-4" />
                    <span className="text-sm">Multiple</span>
                  </div>
                  <p className="text-xl font-bold text-orange-900">
                    {selectedProgram.metrics?.portfolio_multiple
                      ? `${selectedProgram.metrics.portfolio_multiple.toFixed(2)}x`
                      : 'N/A'}
                  </p>
                </div>
              </div>

              {/* Allocation Form */}
              {showAllocateForm && (
                <div className="p-4 border rounded-lg bg-gray-50 space-y-4">
                  <h4 className="font-medium">Allocate Capital to Project</h4>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <Label htmlFor="allocProjectName">Project Name</Label>
                      <Input
                        id="allocProjectName"
                        value={allocProjectName}
                        onChange={(e) => setAllocProjectName(e.target.value)}
                        placeholder="e.g., Sky Warriors"
                        className="mt-1.5"
                      />
                    </div>
                    <div>
                      <Label htmlFor="allocProjectId">Project ID (optional)</Label>
                      <Input
                        id="allocProjectId"
                        value={allocProjectId}
                        onChange={(e) => setAllocProjectId(e.target.value)}
                        placeholder="Auto-generated if empty"
                        className="mt-1.5"
                      />
                    </div>
                    <div>
                      <Label htmlFor="allocAmount">Allocation Amount ($)</Label>
                      <Input
                        id="allocAmount"
                        type="number"
                        value={allocAmount}
                        onChange={(e) => setAllocAmount(Number(e.target.value))}
                        className="mt-1.5"
                      />
                    </div>
                    <div>
                      <Label htmlFor="allocBudget">Project Budget ($)</Label>
                      <Input
                        id="allocBudget"
                        type="number"
                        value={allocBudget}
                        onChange={(e) => setAllocBudget(Number(e.target.value))}
                        className="mt-1.5"
                      />
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      onClick={handleAllocateCapital}
                      disabled={loading || !allocProjectName || allocAmount <= 0}
                    >
                      {loading ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <CheckCircle className="h-4 w-4 mr-2" />
                      )}
                      Allocate
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => setShowAllocateForm(false)}
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              )}

              {/* Deployments List */}
              <div>
                <h4 className="font-medium mb-3">Deployments</h4>
                {selectedProgram.deployments.length === 0 ? (
                  <p className="text-gray-500 text-sm">No deployments yet</p>
                ) : (
                  <div className="space-y-2">
                    {selectedProgram.deployments.map((deployment) => (
                      <div
                        key={deployment.deployment_id}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div>
                          <p className="font-medium">{deployment.project_name}</p>
                          <p className="text-sm text-gray-500">
                            {deployment.status} • {deployment.allocation_date}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">
                            {formatCurrency(deployment.allocated_amount)}
                          </p>
                          {deployment.multiple && (
                            <p className="text-sm text-green-600">
                              {deployment.multiple.toFixed(2)}x return
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Fund Terms */}
              <div className="grid grid-cols-3 gap-4 pt-4 border-t">
                <div className="text-center">
                  <p className="text-sm text-gray-500">Management Fee</p>
                  <p className="font-medium">
                    {selectedProgram.management_fee_pct
                      ? `${selectedProgram.management_fee_pct}%`
                      : 'N/A'}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-500">Carry</p>
                  <p className="font-medium">
                    {selectedProgram.carry_percentage
                      ? `${selectedProgram.carry_percentage}%`
                      : 'N/A'}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-500">Hurdle</p>
                  <p className="font-medium">
                    {selectedProgram.hurdle_rate
                      ? `${selectedProgram.hurdle_rate}%`
                      : 'N/A'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
