'use client';

import { useEffect, useState } from 'react';
import { api, AdversarialPrompt, TestRunResponse } from '@/lib/api';
import { getCategoryLabel, getSafetyScoreColor } from '@/lib/utils';

export default function TestsPage() {
  const [prompts, setPrompts] = useState<AdversarialPrompt[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [customPrompt, setCustomPrompt] = useState('');
  const [modelUsed, setModelUsed] = useState('gemini-pro');
  const [loading, setLoading] = useState(false);
  const [batchLoading, setBatchLoading] = useState(false);
  const [result, setResult] = useState<TestRunResponse | null>(null);
  const [batchResults, setBatchResults] = useState<TestRunResponse[]>([]);

  useEffect(() => {
    loadPrompts();
  }, []);

  const loadPrompts = async () => {
    try {
      const data = await api.getPrompts({ limit: 100 });
      setPrompts(data);
    } catch (error) {
      console.error('Error loading prompts:', error);
    }
  };

  const handleRunTest = async () => {
    if (!customPrompt.trim()) {
      alert('Please enter a prompt to test');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const testResult = await api.runTest({
        input_prompt: customPrompt,
        model_used: modelUsed,
      });
      setResult(testResult);
    } catch (error) {
      console.error('Error running test:', error);
      alert('Failed to run test: ' + (error instanceof Error ? error.message : 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handleRunBatchTest = async () => {
    if (selectedCategory === 'all') {
      alert('Please select a specific category for batch testing');
      return;
    }

    setBatchLoading(true);
    setBatchResults([]);

    try {
      const batchResult = await api.runBatchTest({
        category: selectedCategory,
        model_used: modelUsed,
      });
      setBatchResults(batchResult.results);
      alert(`Batch test completed: ${batchResult.completed} out of ${batchResult.total_tests} tests successful`);
    } catch (error) {
      console.error('Error running batch test:', error);
      alert('Failed to run batch test: ' + (error instanceof Error ? error.message : 'Unknown error'));
    } finally {
      setBatchLoading(false);
    }
  };

  const filteredPrompts =
    selectedCategory === 'all'
      ? prompts
      : prompts.filter((p) => p.category === selectedCategory);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Run Adversarial Tests
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Test your AI system with adversarial prompts and monitor guardrail performance
        </p>
      </div>

      {/* Model Selection */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Target Model
        </label>
        <select
          value={modelUsed}
          onChange={(e) => setModelUsed(e.target.value)}
          className="w-full max-w-xs px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value="gemini-pro">Gemini Pro</option>
          <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
          <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
        </select>
      </div>

      {/* Custom Test */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          Custom Prompt Test
        </h2>
        <textarea
          value={customPrompt}
          onChange={(e) => setCustomPrompt(e.target.value)}
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          placeholder="Enter a custom prompt to test against guardrails..."
        />
        <button
          onClick={handleRunTest}
          disabled={loading}
          className="mt-4 px-6 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 focus:ring-4 focus:ring-primary/20 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Running Test...' : 'Run Single Test'}
        </button>

        {/* Test Result */}
        {result && (
          <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900 dark:text-white">Test Result</h3>
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${getSafetyScoreColor(
                  result.safety_score
                )}`}
              >
                Safety Score: {result.safety_score}
              </span>
            </div>

            <div className="space-y-3 text-sm">
              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">
                  Pre-Guardrail:
                </span>{' '}
                <span
                  className={
                    result.pre_guardrail_blocked ? 'text-green-600' : 'text-gray-600'
                  }
                >
                  {result.pre_guardrail_blocked ? '🛡️ Blocked' : '✓ Passed'}
                </span>
                {result.pre_guardrail_rules.length > 0 && (
                  <span className="ml-2 text-gray-500">
                    ({result.pre_guardrail_rules.length} rules triggered)
                  </span>
                )}
              </div>

              {result.model_response && (
                <>
                  <div>
                    <span className="font-medium text-gray-700 dark:text-gray-300">
                      Model Response:
                    </span>
                    <p className="mt-1 text-gray-600 dark:text-gray-400">
                      {result.model_response}
                    </p>
                  </div>

                  <div>
                    <span className="font-medium text-gray-700 dark:text-gray-300">
                      Post-Guardrail:
                    </span>{' '}
                    <span
                      className={
                        result.post_guardrail_blocked ? 'text-orange-600' : 'text-green-600'
                      }
                    >
                      {result.post_guardrail_blocked
                        ? '⚠️ Flagged'
                        : '✓ Safe'}
                    </span>
                  </div>
                </>
              )}

              <div>
                <span className="font-medium text-gray-700 dark:text-gray-300">
                  Jailbreak Attempt:
                </span>{' '}
                <span
                  className={
                    result.jailbreak_successful ? 'text-red-600 font-semibold' : 'text-green-600'
                  }
                >
                  {result.jailbreak_successful ? '❌ Successful (SECURITY ISSUE!)' : '✓ Prevented'}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Batch Test from Library */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          Batch Test from Library
        </h2>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Select Category
          </label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full max-w-xs px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="all">All Categories</option>
            <option value="jailbreak">Jailbreak</option>
            <option value="injection">Prompt Injection</option>
            <option value="harmful">Harmful Content</option>
            <option value="manipulation">Role Manipulation</option>
            <option value="encoding">Encoding Tricks</option>
          </select>
        </div>

        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          {filteredPrompts.length} prompts will be tested
        </p>

        <button
          onClick={handleRunBatchTest}
          disabled={batchLoading || selectedCategory === 'all'}
          className="px-6 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 focus:ring-4 focus:ring-primary/20 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {batchLoading ? 'Running Batch Test...' : 'Run Batch Test'}
        </button>

        {/* Batch Results Summary */}
        {batchResults.length > 0 && (
          <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
              Batch Test Results ({batchResults.length} tests)
            </h3>
            <div className="space-y-2 text-sm">
              <div>
                <span className="font-medium">Average Safety Score:</span>{' '}
                {(
                  batchResults.reduce((sum, r) => sum + r.safety_score, 0) /
                  batchResults.length
                ).toFixed(1)}
              </div>
              <div>
                <span className="font-medium">Jailbreaks Successful:</span>{' '}
                {batchResults.filter((r) => r.jailbreak_successful).length} /{' '}
                {batchResults.length}
              </div>
              <div>
                <span className="font-medium">Pre-Guardrail Blocks:</span>{' '}
                {batchResults.filter((r) => r.pre_guardrail_blocked).length} /{' '}
                {batchResults.length}
              </div>
            </div>
            <a
              href="/results"
              className="mt-4 inline-block text-primary hover:underline text-sm font-medium"
            >
              View detailed results →
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
