'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { api, TestRunResponse } from '@/lib/api';
import { formatDate, getSafetyScoreColor } from '@/lib/utils';

export default function ResultDetailPage() {
  const params = useParams();
  const [result, setResult] = useState<TestRunResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (params.id) {
      loadResult(params.id as string);
    }
  }, [params.id]);

  const loadResult = async (id: string) => {
    try {
      setLoading(true);
      const data = await api.getResult(id);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load result');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">{error || 'Result not found'}</p>
        <Link
          href="/results"
          className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 inline-block"
        >
          Back to Results
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <Link
          href="/results"
          className="text-primary hover:underline text-sm font-medium mb-4 inline-block"
        >
          ← Back to Results
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Test Result Details
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          {formatDate(result.created_at)}
        </p>
      </div>

      {/* Safety Score Card */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Safety Score
            </h2>
            <p
              className={`text-5xl font-bold mt-2 ${getSafetyScoreColor(result.safety_score)}`}
            >
              {result.safety_score}
            </p>
          </div>
          <div className="text-right space-y-2">
            {result.jailbreak_successful && (
              <div className="px-4 py-2 rounded-lg bg-red-100 text-red-700 font-semibold">
                ⚠️ Jailbreak Successful
              </div>
            )}
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Model: {result.model_used}
            </div>
          </div>
        </div>
      </div>

      {/* Input Prompt */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Input Prompt
        </h2>
        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <p className="text-gray-900 dark:text-white whitespace-pre-wrap">
            {result.input_prompt}
          </p>
        </div>
      </div>

      {/* Pre-Guardrail Check */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Pre-Guardrail Check
        </h2>
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <span className="font-medium text-gray-700 dark:text-gray-300">Status:</span>
            <span
              className={`px-3 py-1 rounded-full text-sm font-medium ${
                result.pre_guardrail_blocked
                  ? 'bg-green-100 text-green-700'
                  : 'bg-gray-100 text-gray-700'
              }`}
            >
              {result.pre_guardrail_blocked ? '🛡️ Blocked' : '✓ Passed'}
            </span>
          </div>
          {result.pre_guardrail_rules.length > 0 && (
            <div>
              <p className="font-medium text-gray-700 dark:text-gray-300 mb-2">
                Triggered Rules ({result.pre_guardrail_rules.length}):
              </p>
              <div className="flex flex-wrap gap-2">
                {result.pre_guardrail_rules.map((rule, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm"
                  >
                    {rule}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Model Response */}
      {result.model_response && (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Model Response
          </h2>
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <p className="text-gray-900 dark:text-white whitespace-pre-wrap">
              {result.model_response}
            </p>
          </div>
        </div>
      )}

      {/* Post-Guardrail Check */}
      {result.model_response && (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Post-Guardrail Check
          </h2>
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <span className="font-medium text-gray-700 dark:text-gray-300">Status:</span>
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  result.post_guardrail_blocked
                    ? 'bg-orange-100 text-orange-700'
                    : 'bg-green-100 text-green-700'
                }`}
              >
                {result.post_guardrail_blocked ? '⚠️ Flagged' : '✓ Safe'}
              </span>
            </div>
            {result.post_guardrail_rules.length > 0 && (
              <div>
                <p className="font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Triggered Rules ({result.post_guardrail_rules.length}):
                </p>
                <div className="flex flex-wrap gap-2">
                  {result.post_guardrail_rules.map((rule, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm"
                    >
                      {rule}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
