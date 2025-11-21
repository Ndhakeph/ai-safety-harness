'use client';

import { useEffect, useState } from 'react';
import { api, TestRunResponse } from '@/lib/api';
import TestResultCard from '@/components/TestResultCard';

export default function ResultsPage() {
  const [results, setResults] = useState<TestRunResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    jailbreak_successful: undefined as boolean | undefined,
    min_safety_score: undefined as number | undefined,
    max_safety_score: undefined as number | undefined,
  });

  useEffect(() => {
    loadResults();
  }, []);

  const loadResults = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 50 };

      if (filters.jailbreak_successful !== undefined) {
        params.jailbreak_successful = filters.jailbreak_successful;
      }
      if (filters.min_safety_score !== undefined) {
        params.min_safety_score = filters.min_safety_score;
      }
      if (filters.max_safety_score !== undefined) {
        params.max_safety_score = filters.max_safety_score;
      }

      const data = await api.getResults(params);
      setResults(data);
    } catch (error) {
      console.error('Error loading results:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyFilters = () => {
    loadResults();
  };

  const handleResetFilters = () => {
    setFilters({
      jailbreak_successful: undefined,
      min_safety_score: undefined,
      max_safety_score: undefined,
    });
    setTimeout(loadResults, 0);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Test Results
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          View and analyze adversarial test results
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Filters
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Jailbreak Status
            </label>
            <select
              value={
                filters.jailbreak_successful === undefined
                  ? 'all'
                  : filters.jailbreak_successful.toString()
              }
              onChange={(e) =>
                setFilters({
                  ...filters,
                  jailbreak_successful:
                    e.target.value === 'all'
                      ? undefined
                      : e.target.value === 'true',
                })
              }
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">All</option>
              <option value="true">Jailbreak Successful</option>
              <option value="false">Jailbreak Prevented</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Min Safety Score
            </label>
            <input
              type="number"
              min="0"
              max="100"
              value={filters.min_safety_score || ''}
              onChange={(e) =>
                setFilters({
                  ...filters,
                  min_safety_score: e.target.value
                    ? parseInt(e.target.value)
                    : undefined,
                })
              }
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              placeholder="0"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Max Safety Score
            </label>
            <input
              type="number"
              min="0"
              max="100"
              value={filters.max_safety_score || ''}
              onChange={(e) =>
                setFilters({
                  ...filters,
                  max_safety_score: e.target.value
                    ? parseInt(e.target.value)
                    : undefined,
                })
              }
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              placeholder="100"
            />
          </div>
        </div>

        <div className="mt-4 flex space-x-4">
          <button
            onClick={handleApplyFilters}
            className="px-6 py-2 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-colors"
          >
            Apply Filters
          </button>
          <button
            onClick={handleResetFilters}
            className="px-6 py-2 border border-gray-300 dark:border-gray-600 rounded-lg font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            Reset
          </button>
        </div>
      </div>

      {/* Results List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      ) : results.length > 0 ? (
        <div className="space-y-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Showing {results.length} result{results.length !== 1 ? 's' : ''}
          </p>
          {results.map((result) => (
            <TestResultCard key={result.id} result={result} />
          ))}
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-12 text-center">
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            No test results found matching your filters
          </p>
          <button
            onClick={handleResetFilters}
            className="px-6 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary/90"
          >
            Clear Filters
          </button>
        </div>
      )}
    </div>
  );
}
