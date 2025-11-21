'use client';

import { useState } from 'react';
import { api, AdversarialPrompt } from '@/lib/api';

interface AdversarialPromptFormProps {
  onSuccess?: (prompt: AdversarialPrompt) => void;
  onCancel?: () => void;
  initialData?: AdversarialPrompt;
  mode?: 'create' | 'edit';
}

export default function AdversarialPromptForm({
  onSuccess,
  onCancel,
  initialData,
  mode = 'create',
}: AdversarialPromptFormProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    category: initialData?.category || 'jailbreak',
    prompt: initialData?.prompt || '',
    expected_blocked: initialData?.expected_blocked ?? true,
    severity: initialData?.severity || 'medium',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (mode === 'create') {
        const result = await api.createPrompt(formData);
        onSuccess?.(result);
      } else if (initialData) {
        const result = await api.updatePrompt(initialData.id, formData);
        onSuccess?.(result);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      <div>
        <label
          htmlFor="category"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          Category
        </label>
        <select
          id="category"
          value={formData.category}
          onChange={(e) =>
            setFormData({ ...formData, category: e.target.value })
          }
          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          required
        >
          <option value="jailbreak">Jailbreak</option>
          <option value="injection">Prompt Injection</option>
          <option value="harmful">Harmful Content</option>
          <option value="manipulation">Role Manipulation</option>
          <option value="encoding">Encoding Tricks</option>
        </select>
      </div>

      <div>
        <label
          htmlFor="prompt"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          Adversarial Prompt
        </label>
        <textarea
          id="prompt"
          value={formData.prompt}
          onChange={(e) =>
            setFormData({ ...formData, prompt: e.target.value })
          }
          rows={6}
          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          placeholder="Enter an adversarial prompt to test..."
          required
        />
      </div>

      <div>
        <label
          htmlFor="severity"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          Severity
        </label>
        <select
          id="severity"
          value={formData.severity}
          onChange={(e) =>
            setFormData({ ...formData, severity: e.target.value })
          }
          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          required
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="expected_blocked"
          checked={formData.expected_blocked}
          onChange={(e) =>
            setFormData({ ...formData, expected_blocked: e.target.checked })
          }
          className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
        />
        <label
          htmlFor="expected_blocked"
          className="ml-2 block text-sm text-gray-700 dark:text-gray-300"
        >
          Should be blocked by guardrails
        </label>
      </div>

      <div className="flex space-x-4">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 bg-primary text-white px-6 py-3 rounded-lg font-medium hover:bg-primary/90 focus:ring-4 focus:ring-primary/20 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Saving...' : mode === 'create' ? 'Create Prompt' : 'Update Prompt'}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-lg font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
