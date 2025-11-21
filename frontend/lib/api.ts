/**
 * API client for communicating with the backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface AdversarialPrompt {
  id: string;
  category: string;
  prompt: string;
  expected_blocked: boolean;
  severity: string;
  created_at: string;
  updated_at: string;
}

export interface TestRunResponse {
  id: string;
  prompt_id?: string;
  input_prompt: string;
  pre_guardrail_blocked: boolean;
  pre_guardrail_rules: string[];
  model_response?: string;
  post_guardrail_blocked: boolean;
  post_guardrail_rules: string[];
  jailbreak_successful: boolean;
  safety_score: number;
  model_used: string;
  created_at: string;
}

export interface SafetyMetrics {
  total_tests: number;
  tests_today: number;
  jailbreak_success_rate: number;
  guardrail_trigger_rate: number;
  false_positive_rate: number;
  average_safety_score: number;
  active_incidents: number;
  incidents_today: number;
}

export interface SafetyScoreTimeSeries {
  date: string;
  average_score: number;
  test_count: number;
}

export interface CategoryBreakdown {
  category: string;
  total_tests: number;
  jailbreak_success_rate: number;
  average_safety_score: number;
}

export interface Incident {
  id: string;
  test_run_id: string;
  severity: string;
  description: string;
  created_at: string;
}

class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl;
  }

  private async fetch<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Library endpoints
  async getPrompts(params?: {
    category?: string;
    severity?: string;
    limit?: number;
    offset?: number;
  }): Promise<AdversarialPrompt[]> {
    const queryParams = new URLSearchParams();
    if (params?.category) queryParams.set('category', params.category);
    if (params?.severity) queryParams.set('severity', params.severity);
    if (params?.limit) queryParams.set('limit', params.limit.toString());
    if (params?.offset) queryParams.set('offset', params.offset.toString());

    const query = queryParams.toString();
    return this.fetch(`/api/library${query ? `?${query}` : ''}`);
  }

  async getPrompt(id: string): Promise<AdversarialPrompt> {
    return this.fetch(`/api/library/${id}`);
  }

  async createPrompt(data: {
    category: string;
    prompt: string;
    expected_blocked: boolean;
    severity: string;
  }): Promise<AdversarialPrompt> {
    return this.fetch('/api/library', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updatePrompt(id: string, data: Partial<AdversarialPrompt>): Promise<AdversarialPrompt> {
    return this.fetch(`/api/library/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deletePrompt(id: string): Promise<void> {
    return this.fetch(`/api/library/${id}`, {
      method: 'DELETE',
    });
  }

  // Test endpoints
  async runTest(data: {
    prompt_id?: string;
    input_prompt: string;
    model_used?: string;
  }): Promise<TestRunResponse> {
    return this.fetch('/api/test/run', {
      method: 'POST',
      body: JSON.stringify({
        prompt_id: data.prompt_id || null,
        input_prompt: data.input_prompt,
        model_used: data.model_used || 'gemini-pro',
      }),
    });
  }

  async runBatchTest(data: {
    category?: string;
    prompt_ids?: string[];
    model_used?: string;
  }): Promise<{ total_tests: number; completed: number; results: TestRunResponse[] }> {
    return this.fetch('/api/test/batch', {
      method: 'POST',
      body: JSON.stringify({
        category: data.category || null,
        prompt_ids: data.prompt_ids || null,
        model_used: data.model_used || 'gemini-pro',
      }),
    });
  }

  // Results endpoints
  async getResults(params?: {
    start_date?: string;
    end_date?: string;
    category?: string;
    jailbreak_successful?: boolean;
    min_safety_score?: number;
    max_safety_score?: number;
    limit?: number;
    offset?: number;
  }): Promise<TestRunResponse[]> {
    const queryParams = new URLSearchParams();
    if (params?.start_date) queryParams.set('start_date', params.start_date);
    if (params?.end_date) queryParams.set('end_date', params.end_date);
    if (params?.category) queryParams.set('category', params.category);
    if (params?.jailbreak_successful !== undefined) queryParams.set('jailbreak_successful', params.jailbreak_successful.toString());
    if (params?.min_safety_score !== undefined) queryParams.set('min_safety_score', params.min_safety_score.toString());
    if (params?.max_safety_score !== undefined) queryParams.set('max_safety_score', params.max_safety_score.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());
    if (params?.offset) queryParams.set('offset', params.offset.toString());

    const query = queryParams.toString();
    return this.fetch(`/api/results${query ? `?${query}` : ''}`);
  }

  async getResult(id: string): Promise<TestRunResponse> {
    return this.fetch(`/api/results/${id}`);
  }

  async getMetrics(): Promise<SafetyMetrics> {
    return this.fetch('/api/results/metrics/summary');
  }

  async getTimeSeries(days: number = 7): Promise<SafetyScoreTimeSeries[]> {
    return this.fetch(`/api/results/metrics/timeseries?days=${days}`);
  }

  async getCategoryBreakdown(): Promise<CategoryBreakdown[]> {
    return this.fetch('/api/results/metrics/categories');
  }

  // Incidents endpoints
  async getIncidents(params?: {
    severity?: string;
    limit?: number;
    offset?: number;
  }): Promise<Incident[]> {
    const queryParams = new URLSearchParams();
    if (params?.severity) queryParams.set('severity', params.severity);
    if (params?.limit) queryParams.set('limit', params.limit.toString());
    if (params?.offset) queryParams.set('offset', params.offset.toString());

    const query = queryParams.toString();
    return this.fetch(`/api/library/incidents/${query ? `?${query}` : ''}`);
  }

  async getIncident(id: string): Promise<Incident> {
    return this.fetch(`/api/library/incidents/${id}`);
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string; version: string }> {
    return this.fetch('/health');
  }
}

export const api = new APIClient();
