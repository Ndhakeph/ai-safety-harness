import Link from 'next/link';
import { TestRunResponse } from '@/lib/api';
import {
  formatRelativeTime,
  getSafetyScoreColor,
  truncateText,
} from '@/lib/utils';

interface TestResultCardProps {
  result: TestRunResponse;
}

export default function TestResultCard({ result }: TestResultCardProps) {
  return (
    <Link
      href={`/results/${result.id}`}
      className="block bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-lg transition-shadow"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-3">
            <span
              className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getSafetyScoreColor(
                result.safety_score
              )}`}
            >
              Safety Score: {result.safety_score}
            </span>
            {result.jailbreak_successful && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium text-red-700 bg-red-50 border border-red-200">
                ⚠️ Jailbreak Success
              </span>
            )}
            {result.pre_guardrail_blocked && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium text-blue-700 bg-blue-50 border border-blue-200">
                🛡️ Pre-blocked
              </span>
            )}
          </div>

          <p className="mt-3 text-gray-900 dark:text-white font-medium">
            {truncateText(result.input_prompt, 150)}
          </p>

          {result.model_response && (
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Response: {truncateText(result.model_response, 100)}
            </p>
          )}

          <div className="mt-4 flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
            <span>Model: {result.model_used}</span>
            <span>•</span>
            <span>{formatRelativeTime(result.created_at)}</span>
            {result.pre_guardrail_rules.length > 0 && (
              <>
                <span>•</span>
                <span>
                  {result.pre_guardrail_rules.length} rule
                  {result.pre_guardrail_rules.length > 1 ? 's' : ''} triggered
                </span>
              </>
            )}
          </div>
        </div>

        <div className="ml-4 flex-shrink-0">
          <svg
            className="w-5 h-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </div>
      </div>
    </Link>
  );
}
