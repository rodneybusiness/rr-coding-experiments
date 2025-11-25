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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import {
  Settings,
  Bell,
  Globe,
  Palette,
  Database,
  Shield,
  Save,
  RefreshCw,
  CheckCircle,
} from 'lucide-react';

export default function SettingsPage() {
  const [saved, setSaved] = useState(false);
  const [settings, setSettings] = useState({
    // General
    defaultCurrency: 'USD',
    dateFormat: 'MM/DD/YYYY',
    numberFormat: 'comma',

    // API
    apiUrl: 'http://localhost:8000',
    timeout: 30,

    // Notifications
    emailNotifications: true,
    projectUpdates: true,
    portfolioAlerts: true,

    // Display
    theme: 'light',
    compactMode: false,
    showAnimations: true,

    // Defaults
    defaultJurisdiction: 'United States',
    defaultMonteCarloIterations: 1000,
    defaultRiskFreeRate: 4.5,
  });

  const handleSave = () => {
    // In production, this would save to backend/localStorage
    localStorage.setItem('filmFinancingSettings', JSON.stringify(settings));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleReset = () => {
    setSettings({
      defaultCurrency: 'USD',
      dateFormat: 'MM/DD/YYYY',
      numberFormat: 'comma',
      apiUrl: 'http://localhost:8000',
      timeout: 30,
      emailNotifications: true,
      projectUpdates: true,
      portfolioAlerts: true,
      theme: 'light',
      compactMode: false,
      showAnimations: true,
      defaultJurisdiction: 'United States',
      defaultMonteCarloIterations: 1000,
      defaultRiskFreeRate: 4.5,
    });
  };

  return (
    <div className="flex flex-col">
      <Header
        title="Settings"
        description="Configure your Film Financing Navigator preferences"
      />

      <div className="p-6 space-y-6">
        {/* Save Banner */}
        {saved && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg flex items-center gap-2">
            <CheckCircle className="h-4 w-4" />
            <span className="text-sm">Settings saved successfully</span>
          </div>
        )}

        {/* General Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-5 w-5" />
              General Settings
            </CardTitle>
            <CardDescription>Configure regional and formatting preferences</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <Label>Default Currency</Label>
                <Select
                  value={settings.defaultCurrency}
                  onValueChange={(v) => setSettings({ ...settings, defaultCurrency: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="USD">USD ($)</SelectItem>
                    <SelectItem value="EUR">EUR (E)</SelectItem>
                    <SelectItem value="GBP">GBP (L)</SelectItem>
                    <SelectItem value="CAD">CAD (C$)</SelectItem>
                    <SelectItem value="AUD">AUD (A$)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Date Format</Label>
                <Select
                  value={settings.dateFormat}
                  onValueChange={(v) => setSettings({ ...settings, dateFormat: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="MM/DD/YYYY">MM/DD/YYYY</SelectItem>
                    <SelectItem value="DD/MM/YYYY">DD/MM/YYYY</SelectItem>
                    <SelectItem value="YYYY-MM-DD">YYYY-MM-DD</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Number Format</Label>
                <Select
                  value={settings.numberFormat}
                  onValueChange={(v) => setSettings({ ...settings, numberFormat: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="comma">1,234,567.89</SelectItem>
                    <SelectItem value="space">1 234 567.89</SelectItem>
                    <SelectItem value="period">1.234.567,89</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* API Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              API Configuration
            </CardTitle>
            <CardDescription>Backend connection settings</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label>API Base URL</Label>
                <Input
                  value={settings.apiUrl}
                  onChange={(e) => setSettings({ ...settings, apiUrl: e.target.value })}
                  placeholder="http://localhost:8000"
                />
              </div>

              <div className="space-y-2">
                <Label>Request Timeout (seconds)</Label>
                <Input
                  type="number"
                  value={settings.timeout}
                  onChange={(e) =>
                    setSettings({ ...settings, timeout: parseInt(e.target.value) || 30 })
                  }
                  min={5}
                  max={120}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Notification Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              Notifications
            </CardTitle>
            <CardDescription>Configure notification preferences</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label>Email Notifications</Label>
                <p className="text-sm text-muted-foreground">
                  Receive email updates about your projects
                </p>
              </div>
              <Switch
                checked={settings.emailNotifications}
                onCheckedChange={(v) => setSettings({ ...settings, emailNotifications: v })}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Project Updates</Label>
                <p className="text-sm text-muted-foreground">
                  Get notified when project status changes
                </p>
              </div>
              <Switch
                checked={settings.projectUpdates}
                onCheckedChange={(v) => setSettings({ ...settings, projectUpdates: v })}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Portfolio Alerts</Label>
                <p className="text-sm text-muted-foreground">
                  Receive alerts for portfolio metrics
                </p>
              </div>
              <Switch
                checked={settings.portfolioAlerts}
                onCheckedChange={(v) => setSettings({ ...settings, portfolioAlerts: v })}
              />
            </div>
          </CardContent>
        </Card>

        {/* Display Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Palette className="h-5 w-5" />
              Display
            </CardTitle>
            <CardDescription>Customize the appearance</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label>Theme</Label>
                <Select
                  value={settings.theme}
                  onValueChange={(v) => setSettings({ ...settings, theme: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="light">Light</SelectItem>
                    <SelectItem value="dark">Dark</SelectItem>
                    <SelectItem value="system">System</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Compact Mode</Label>
                <p className="text-sm text-muted-foreground">
                  Reduce spacing for more content density
                </p>
              </div>
              <Switch
                checked={settings.compactMode}
                onCheckedChange={(v) => setSettings({ ...settings, compactMode: v })}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label>Animations</Label>
                <p className="text-sm text-muted-foreground">
                  Enable UI animations and transitions
                </p>
              </div>
              <Switch
                checked={settings.showAnimations}
                onCheckedChange={(v) => setSettings({ ...settings, showAnimations: v })}
              />
            </div>
          </CardContent>
        </Card>

        {/* Calculation Defaults */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Calculation Defaults
            </CardTitle>
            <CardDescription>Default values for calculations</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <Label>Default Jurisdiction</Label>
                <Select
                  value={settings.defaultJurisdiction}
                  onValueChange={(v) => setSettings({ ...settings, defaultJurisdiction: v })}
                >
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

              <div className="space-y-2">
                <Label>Monte Carlo Iterations</Label>
                <Input
                  type="number"
                  value={settings.defaultMonteCarloIterations}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      defaultMonteCarloIterations: parseInt(e.target.value) || 1000,
                    })
                  }
                  min={100}
                  max={10000}
                />
              </div>

              <div className="space-y-2">
                <Label>Risk-Free Rate (%)</Label>
                <Input
                  type="number"
                  step="0.1"
                  value={settings.defaultRiskFreeRate}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      defaultRiskFreeRate: parseFloat(e.target.value) || 4.5,
                    })
                  }
                  min={0}
                  max={15}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex justify-end gap-4">
          <Button variant="outline" onClick={handleReset}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Reset to Defaults
          </Button>
          <Button onClick={handleSave}>
            <Save className="h-4 w-4 mr-2" />
            Save Settings
          </Button>
        </div>
      </div>
    </div>
  );
}
