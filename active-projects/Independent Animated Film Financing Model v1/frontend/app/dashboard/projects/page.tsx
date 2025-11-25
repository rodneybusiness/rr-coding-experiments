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
import {
  Film,
  Plus,
  Trash2,
  DollarSign,
  Calendar,
  MapPin,
  Tag,
  AlertTriangle,
  CheckCircle,
  Loader2,
  Clock,
  TrendingUp,
  Users,
  Clapperboard,
} from 'lucide-react';
import { formatCurrency, formatPercentage } from '@/lib/utils';
import {
  createProject,
  listProjects,
  deleteProject,
  updateProject,
} from '@/lib/api/services';
import type { ProjectProfileResponse, ProjectProfileInput } from '@/lib/api/types';

interface ProjectProfile {
  project_id: string;
  project_name: string;
  project_budget: number;
  genre?: string;
  jurisdiction?: string;
  rating?: string;
  is_development: boolean;
  is_first_time_director: boolean;
  expected_revenue?: number;
  production_start_date?: string;
  expected_release_date?: string;
  description?: string;
  total_funding: number;
  funding_gap: number;
  status: 'development' | 'pre_production' | 'production' | 'post_production' | 'completed';
}

const GENRES = [
  'Animation',
  'Action',
  'Comedy',
  'Drama',
  'Family',
  'Fantasy',
  'Horror',
  'Sci-Fi',
  'Thriller',
];

const JURISDICTIONS = [
  'United States',
  'Canada',
  'United Kingdom',
  'Ireland',
  'France',
  'Germany',
  'Australia',
  'New Zealand',
];

const STATUS_COLORS: Record<string, string> = {
  development: 'bg-yellow-100 text-yellow-700',
  pre_production: 'bg-blue-100 text-blue-700',
  production: 'bg-purple-100 text-purple-700',
  post_production: 'bg-orange-100 text-orange-700',
  completed: 'bg-green-100 text-green-700',
};

// Helper function to convert API response to local type
function toProjectProfile(p: ProjectProfileResponse): ProjectProfile {
  return {
    project_id: p.project_id,
    project_name: p.project_name,
    project_budget: p.project_budget,
    genre: p.genre,
    jurisdiction: p.jurisdiction,
    rating: p.rating,
    is_development: p.is_development,
    is_first_time_director: p.is_first_time_director,
    expected_revenue: p.expected_revenue,
    production_start_date: p.production_start_date,
    expected_release_date: p.expected_release_date,
    description: p.description,
    total_funding: p.total_funding,
    funding_gap: p.funding_gap,
    status: p.is_development ? 'development' : 'pre_production',
  };
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<ProjectProfile[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [selectedProject, setSelectedProject] = useState<ProjectProfile | null>(null);
  const [apiAvailable, setApiAvailable] = useState(true);

  // Form state
  const [projectName, setProjectName] = useState('');
  const [projectBudget, setProjectBudget] = useState(30000000);
  const [genre, setGenre] = useState('Animation');
  const [jurisdiction, setJurisdiction] = useState('United States');
  const [rating, setRating] = useState('PG');
  const [isDevelopment, setIsDevelopment] = useState(false);
  const [isFirstTimeDirector, setIsFirstTimeDirector] = useState(false);
  const [expectedRevenue, setExpectedRevenue] = useState(75000000);
  const [productionStartDate, setProductionStartDate] = useState('');
  const [expectedReleaseDate, setExpectedReleaseDate] = useState('');
  const [description, setDescription] = useState('');

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setLoading(true);
    try {
      const response = await listProjects();
      setProjects(response.projects.map(toProjectProfile));
      setApiAvailable(true);
      setError(null);
    } catch (err) {
      console.error('Failed to load projects from API:', err);
      setApiAvailable(false);
      setError('API unavailable - using demo mode');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async () => {
    setLoading(true);
    setError(null);

    try {
      const projectInput: ProjectProfileInput = {
        project_name: projectName,
        project_budget: projectBudget,
        genre,
        jurisdiction,
        rating,
        is_development: isDevelopment,
        is_first_time_director: isFirstTimeDirector,
        expected_revenue: expectedRevenue,
        production_start_date: productionStartDate || undefined,
        expected_release_date: expectedReleaseDate || undefined,
        description: description || undefined,
      };

      const created = await createProject(projectInput);
      setProjects((prev) => [...prev, toProjectProfile(created)]);
      setShowForm(false);
      resetForm();
    } catch (err: any) {
      setError(err.message || 'Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProject = async (projectId: string) => {
    try {
      await deleteProject(projectId);
      setProjects((prev) => prev.filter((p) => p.project_id !== projectId));
      if (selectedProject?.project_id === projectId) {
        setSelectedProject(null);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to delete project');
    }
  };

  const resetForm = () => {
    setProjectName('');
    setProjectBudget(30000000);
    setGenre('Animation');
    setJurisdiction('United States');
    setRating('PG');
    setIsDevelopment(false);
    setIsFirstTimeDirector(false);
    setExpectedRevenue(75000000);
    setProductionStartDate('');
    setExpectedReleaseDate('');
    setDescription('');
  };

  const totalBudget = projects.reduce((sum, p) => sum + p.project_budget, 0);
  const totalFunding = projects.reduce((sum, p) => sum + p.total_funding, 0);
  const totalGap = projects.reduce((sum, p) => sum + p.funding_gap, 0);
  const developmentProjects = projects.filter((p) => p.is_development).length;

  return (
    <div className="flex flex-col">
      <Header
        title="Projects"
        description="Manage your film projects and track financing progress"
      />

      <div className="p-6 space-y-6">
        {/* Summary Cards */}
        <div className="grid gap-6 md:grid-cols-4">
          <Card className="bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-blue-100">
                Total Projects
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{projects.length}</div>
              <div className="text-sm text-blue-100 mt-1">
                {developmentProjects} in development
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-500 to-emerald-600 text-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-green-100">
                Total Budget
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {formatCurrency(totalBudget)}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-500 to-violet-600 text-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-purple-100">
                Total Funding
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {formatCurrency(totalFunding)}
              </div>
              <div className="text-sm text-purple-100 mt-1">
                {totalBudget > 0 ? formatPercentage((totalFunding / totalBudget) * 100) : '0%'} funded
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
                {showForm ? 'Cancel' : 'New Project'}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Create Project Form */}
        {showForm && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Film className="h-5 w-5" />
                Create New Project
              </CardTitle>
              <CardDescription>
                Add a new film project to track financing and production
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label htmlFor="projectName">Project Name</Label>
                  <Input
                    id="projectName"
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    placeholder="e.g., Sky Warriors"
                    className="mt-1.5"
                  />
                </div>
                <div>
                  <Label htmlFor="projectBudget">Budget ($)</Label>
                  <Input
                    id="projectBudget"
                    type="number"
                    value={projectBudget}
                    onChange={(e) => setProjectBudget(Number(e.target.value))}
                    className="mt-1.5"
                  />
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <Label htmlFor="genre">Genre</Label>
                  <select
                    id="genre"
                    className="w-full h-10 px-3 rounded-md border border-input bg-background mt-1.5"
                    value={genre}
                    onChange={(e) => setGenre(e.target.value)}
                  >
                    {GENRES.map((g) => (
                      <option key={g} value={g}>
                        {g}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label htmlFor="jurisdiction">Primary Jurisdiction</Label>
                  <select
                    id="jurisdiction"
                    className="w-full h-10 px-3 rounded-md border border-input bg-background mt-1.5"
                    value={jurisdiction}
                    onChange={(e) => setJurisdiction(e.target.value)}
                  >
                    {JURISDICTIONS.map((j) => (
                      <option key={j} value={j}>
                        {j}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label htmlFor="rating">Target Rating</Label>
                  <select
                    id="rating"
                    className="w-full h-10 px-3 rounded-md border border-input bg-background mt-1.5"
                    value={rating}
                    onChange={(e) => setRating(e.target.value)}
                  >
                    <option value="G">G</option>
                    <option value="PG">PG</option>
                    <option value="PG-13">PG-13</option>
                    <option value="R">R</option>
                  </select>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label htmlFor="expectedRevenue">Expected Revenue ($)</Label>
                  <Input
                    id="expectedRevenue"
                    type="number"
                    value={expectedRevenue}
                    onChange={(e) => setExpectedRevenue(Number(e.target.value))}
                    className="mt-1.5"
                  />
                </div>
                <div>
                  <Label htmlFor="productionStart">Production Start</Label>
                  <Input
                    id="productionStart"
                    type="date"
                    value={productionStartDate}
                    onChange={(e) => setProductionStartDate(e.target.value)}
                    className="mt-1.5"
                  />
                </div>
              </div>

              <div className="flex flex-wrap gap-6">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isDevelopment}
                    onChange={(e) => setIsDevelopment(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm">Development Stage</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isFirstTimeDirector}
                    onChange={(e) => setIsFirstTimeDirector(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm">First-Time Director</span>
                </label>
              </div>

              <div>
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Brief project description"
                  className="mt-1.5"
                />
              </div>

              <Button
                className="w-full"
                size="lg"
                onClick={handleCreateProject}
                disabled={loading || !projectName || projectBudget <= 0}
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Project
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

        {/* Projects Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {projects.length === 0 ? (
            <Card className="col-span-full">
              <CardContent className="py-12 text-center text-gray-500">
                <Film className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No projects yet. Create your first project to get started.</p>
              </CardContent>
            </Card>
          ) : (
            projects.map((project) => (
              <Card
                key={project.project_id}
                className={`cursor-pointer transition-all hover:shadow-lg ${
                  selectedProject?.project_id === project.project_id
                    ? 'ring-2 ring-blue-500'
                    : ''
                }`}
                onClick={() => setSelectedProject(project)}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{project.project_name}</CardTitle>
                      <CardDescription className="mt-1 flex items-center gap-2">
                        <Tag className="h-3 w-3" />
                        {project.genre}
                        <span className="mx-1">•</span>
                        <MapPin className="h-3 w-3" />
                        {project.jurisdiction}
                      </CardDescription>
                    </div>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        STATUS_COLORS[project.status] || STATUS_COLORS.development
                      }`}
                    >
                      {project.status.replace('_', ' ')}
                    </span>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Budget</span>
                      <span className="font-medium">{formatCurrency(project.project_budget)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Funding</span>
                      <span className="font-medium">
                        {formatCurrency(project.total_funding)}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Gap</span>
                      <span className={`font-medium ${project.funding_gap > 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {formatCurrency(project.funding_gap)}
                      </span>
                    </div>

                    {/* Funding Progress Bar */}
                    <div className="mt-2">
                      <div className="flex justify-between text-xs text-gray-500 mb-1">
                        <span>Funding Progress</span>
                        <span>
                          {project.project_budget > 0
                            ? formatPercentage((project.total_funding / project.project_budget) * 100)
                            : '0%'}
                        </span>
                      </div>
                      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-green-500 transition-all"
                          style={{
                            width: `${Math.min(
                              (project.total_funding / project.project_budget) * 100,
                              100
                            )}%`,
                          }}
                        />
                      </div>
                    </div>

                    {/* Flags */}
                    <div className="flex gap-2 pt-2">
                      {project.is_development && (
                        <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded text-xs">
                          Development
                        </span>
                      )}
                      {project.is_first_time_director && (
                        <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                          First-Time Director
                        </span>
                      )}
                    </div>

                    <div className="pt-2 flex justify-end">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteProject(project.project_id);
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

        {/* Selected Project Details */}
        {selectedProject && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clapperboard className="h-5 w-5" />
                {selectedProject.project_name} - Details
              </CardTitle>
              <CardDescription>
                {selectedProject.description || 'No description provided'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center gap-2 text-blue-700 mb-1">
                    <DollarSign className="h-4 w-4" />
                    <span className="text-sm">Budget</span>
                  </div>
                  <p className="text-xl font-bold text-blue-900">
                    {formatCurrency(selectedProject.project_budget)}
                  </p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <div className="flex items-center gap-2 text-green-700 mb-1">
                    <TrendingUp className="h-4 w-4" />
                    <span className="text-sm">Expected Revenue</span>
                  </div>
                  <p className="text-xl font-bold text-green-900">
                    {formatCurrency(selectedProject.expected_revenue || 0)}
                  </p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <div className="flex items-center gap-2 text-purple-700 mb-1">
                    <CheckCircle className="h-4 w-4" />
                    <span className="text-sm">Funding Secured</span>
                  </div>
                  <p className="text-xl font-bold text-purple-900">
                    {formatCurrency(selectedProject.total_funding)}
                  </p>
                </div>
                <div className="p-4 bg-orange-50 rounded-lg">
                  <div className="flex items-center gap-2 text-orange-700 mb-1">
                    <AlertTriangle className="h-4 w-4" />
                    <span className="text-sm">Funding Gap</span>
                  </div>
                  <p className="text-xl font-bold text-orange-900">
                    {formatCurrency(selectedProject.funding_gap)}
                  </p>
                </div>
              </div>

              {/* Project Details */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t">
                <div>
                  <p className="text-sm text-gray-500">Genre</p>
                  <p className="font-medium">{selectedProject.genre || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Jurisdiction</p>
                  <p className="font-medium">{selectedProject.jurisdiction || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Rating</p>
                  <p className="font-medium">{selectedProject.rating || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Status</p>
                  <p className="font-medium capitalize">
                    {selectedProject.status.replace('_', ' ')}
                  </p>
                </div>
              </div>

              {/* Timeline */}
              {(selectedProject.production_start_date || selectedProject.expected_release_date) && (
                <div className="flex gap-8 pt-4 border-t">
                  {selectedProject.production_start_date && (
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="text-sm text-gray-500">Production Start</p>
                        <p className="font-medium">{selectedProject.production_start_date}</p>
                      </div>
                    </div>
                  )}
                  {selectedProject.expected_release_date && (
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="text-sm text-gray-500">Expected Release</p>
                        <p className="font-medium">{selectedProject.expected_release_date}</p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Expected ROI */}
              {selectedProject.expected_revenue && selectedProject.project_budget > 0 && (
                <div className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Expected ROI</p>
                      <p className="text-2xl font-bold text-indigo-700">
                        {(
                          ((selectedProject.expected_revenue - selectedProject.project_budget) /
                            selectedProject.project_budget) *
                          100
                        ).toFixed(1)}
                        %
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Multiple</p>
                      <p className="text-2xl font-bold text-purple-700">
                        {(selectedProject.expected_revenue / selectedProject.project_budget).toFixed(2)}x
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
