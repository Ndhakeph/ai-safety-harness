'use client';

import { useEffect, useState } from 'react';
import { api, AdversarialPrompt } from '@/lib/api';
import AdversarialPromptForm from '@/components/AdversarialPromptForm';
import { getCategoryLabel, getSeverityColor, truncateText } from '@/lib/utils';

export default function LibraryPage() {
  const [prompts, setPrompts] = useState<AdversarialPrompt[]>([]);
  const [filteredCategory, setFilteredCategory] = useState<string>('all');
  const [showForm, setShowForm] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<AdversarialPrompt | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPrompts();
  }, [filteredCategory]);

  const loadPrompts = async () => {
    try {
      setLoading(true);
      const params = filteredCategory !== 'all' ? { category: filteredCategory } : {};
      const data = await api.getPrompts(params);
      setPrompts(data);
    } catch (error) {
      console.error('Error loading prompts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this prompt?')) {
      return;
    }

    try {
      await api.deletePrompt(id);
      setPrompts(prompts.filter((p) => p.id !== id));
    } catch (error) {
      console.error('Error deleting prompt:', error);
      alert('Failed to delete prompt');
    }
  };

  const handleFormSuccess = () => {
    setShowForm(false);
    setEditingPrompt(null);
    loadPrompts();
  };

  const handleEdit = (prompt: AdversarialPrompt) => {
    setEditingPrompt(prompt);
    setShowForm(true);
  };

  const categoryCounts = prompts.reduce((acc, p) => {
    acc[p.category] = (acc[p.category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Adversarial Prompt Library
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Manage your collection of adversarial test prompts
          </p>
        </div>
        <button
          onClick={() => {
            setEditingPrompt(null);
            setShowForm(true);
          }}
          className="px-6 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 focus:ring-4 focus:ring-primary/20 transition-colors"
        >
          + Add New Prompt
        </button>
      </div>

      {/* Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
              {editingPrompt ? 'Edit Prompt' : 'Create New Prompt'}
            </h2>
            <AdversarialPromptForm
              mode={editingPrompt ? 'edit' : 'create'}
              initialData={editingPrompt || undefined}
              onSuccess={handleFormSuccess}
              onCancel={() => {
                setShowForm(false);
                setEditingPrompt(null);
              }}
            />
          </div>
        </div>
      )}

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        {['all', 'jailbreak', 'injection', 'harmful', 'manipulation', 'encoding'].map(
          (category) => (
            <button
              key={category}
              onClick={() => setFilteredCategory(category)}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                filteredCategory === category
                  ? 'bg-primary text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {category === 'all' ? 'All' : getCategoryLabel(category)}
              {category !== 'all' && categoryCounts[category] && (
                <span className="ml-2">({categoryCounts[category]})</span>
              )}
            </button>
          )
        )}
      </div>

      {/* Prompts List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      ) : prompts.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {prompts.map((prompt) => (
            <div
              key={prompt.id}
              className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <span className="px-3 py-1 rounded-full text-xs font-medium bg-primary/10 text-primary">
                    {getCategoryLabel(prompt.category)}
                  </span>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium border ${getSeverityColor(
                      prompt.severity
                    )}`}
                  >
                    {prompt.severity.toUpperCase()}
                  </span>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEdit(prompt)}
                    className="text-gray-400 hover:text-primary transition-colors"
                    title="Edit"
                  >
                    ✏️
                  </button>
                  <button
                    onClick={() => handleDelete(prompt.id)}
                    className="text-gray-400 hover:text-red-600 transition-colors"
                    title="Delete"
                  >
                    🗑️
                  </button>
                </div>
              </div>

              <p className="text-gray-900 dark:text-white mb-3">
                {truncateText(prompt.prompt, 200)}
              </p>

              <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
                <span>
                  Expected: {prompt.expected_blocked ? '🛡️ Blocked' : '✓ Allowed'}
                </span>
                <span>
                  {new Date(prompt.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-12 text-center">
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            No prompts found in this category
          </p>
          <button
            onClick={() => {
              setEditingPrompt(null);
              setShowForm(true);
            }}
            className="px-6 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary/90"
          >
            Create First Prompt
          </button>
        </div>
      )}
    </div>
  );
}
