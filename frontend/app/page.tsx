'use client';

import { useEffect, useState } from 'react';
import { api, SafetyMetrics, SafetyScoreTimeSeries, TestRunResponse } from '@/lib/api';
import MetricsCard from '@/components/MetricsCard';
import SafetyChart from '@/components/SafetyChart';
import TestResultCard from '@/components/TestResultCard';

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<SafetyMetrics | null>(null);
  const [timeSeries, setTimeSeries] = useState<SafetyScoreTimeSeries[]>([]);
  const [recentResults, setRecentResults] = useState<TestRunResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [metricsData, timeSeriesData, resultsData] = await Promise.all([
        api.getMetrics(),
        api.getTimeSeries(7),
        api.getResults({ limit: 5 }),
      ]);

      setMetrics(metricsData);
      setTimeSeries(timeSeriesData);
      setRecentResults(resultsData);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <p className="text-gray-600 dark:text-gray-400">Failed to load dashboard data</p>
          <button
            onClick={loadDashboardData}
            className="mt-4 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          AI Safety Dashboard
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Monitor AI system safety metrics and test results in real-time
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricsCard
          title="Average Safety Score"
          value={`${metrics.average_safety_score.toFixed(1)}%`}
          subtitle="Overall system safety"
          icon="🛡️"
          valueClassName={
            metrics.average_safety_score >= 80
              ? 'text-green-600'
              : metrics.average_safety_score >= 60
              ? 'text-yellow-600'
              : 'text-red-600'
          }
        />
        <MetricsCard
          title="Tests Today"
          value={metrics.tests_today}
          subtitle={`${metrics.total_tests} total tests`}
          icon="🧪"
        />
        <MetricsCard
          title="Jailbreak Rate"
          value={`${metrics.jailbreak_success_rate.toFixed(1)}%`}
          subtitle="Successful bypass attempts"
          icon="⚠️"
          valueClassName="text-red-600"
        />
        <MetricsCard
          title="Active Incidents"
          value={metrics.active_incidents}
          subtitle={`${metrics.incidents_today} today`}
          icon="🚨"
          valueClassName={
            metrics.active_incidents > 0 ? 'text-orange-600' : 'text-green-600'
          }
        />
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <MetricsCard
          title="Guardrail Trigger Rate"
          value={`${metrics.guardrail_trigger_rate.toFixed(1)}%`}
          subtitle="Prompts caught by guardrails"
          icon="🔒"
        />
        <MetricsCard
          title="False Positive Rate"
          value={`${metrics.false_positive_rate.toFixed(1)}%`}
          subtitle="Legitimate prompts blocked"
          icon="📊"
        />
      </div>

      {/* Safety Score Chart */}
      {timeSeries.length > 0 && <SafetyChart data={timeSeries} />}

      {/* Recent Test Results */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Recent Test Results
          </h2>
          <a
            href="/results"
            className="text-primary hover:underline text-sm font-medium"
          >
            View all →
          </a>
        </div>

        {recentResults.length > 0 ? (
          <div className="space-y-4">
            {recentResults.map((result) => (
              <TestResultCard key={result.id} result={result} />
            ))}
          </div>
        ) : (
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-8 text-center">
            <p className="text-gray-600 dark:text-gray-400">
              No test results yet. Run your first test to get started!
            </p>
            <a
              href="/tests"
              className="mt-4 inline-block px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 font-medium"
            >
              Run Test
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
