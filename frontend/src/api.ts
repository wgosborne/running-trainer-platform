/**
 * API client for Running Tracker backend
 */

import {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  RegisterResponse,
  Plan,
  Run,
  Workout,
  CreatePlanRequest,
  CreateWorkoutRequest,
  CreateRunRequest
} from './types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Handle API errors
 */
class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

/**
 * Authentication API
 */
export const auth = {
  async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: data.email,
        password: data.password,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new APIError(response.status, error || 'Registration failed');
    }

    return response.json();
  },

  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: data.email,
        password: data.password,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new APIError(response.status, error || 'Login failed');
    }

    return response.json();
  },
};

/**
 * Plans API
 */
export const plans = {
  async getAll(token: string): Promise<Plan[]> {
    const response = await fetch(`${API_URL}/plans`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      throw new APIError(response.status, 'Failed to fetch plans');
    }

    return response.json();
  },

  async getOne(id: string, token: string): Promise<Plan> {
    const response = await fetch(`${API_URL}/plans/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      throw new APIError(response.status, 'Failed to fetch plan');
    }

    return response.json();
  },

  async create(data: CreatePlanRequest, token: string): Promise<Plan> {
    const response = await fetch(`${API_URL}/plans`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new APIError(response.status, error || 'Failed to create plan');
    }

    return response.json();
  },
};

/**
 * Runs API
 */
export const runs = {
  async getAll(token: string): Promise<Run[]> {
    const response = await fetch(`${API_URL}/runs`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      throw new APIError(response.status, 'Failed to fetch runs');
    }

    return response.json();
  },

  async getForPlan(planId: string, token: string): Promise<Run[]> {
    const response = await fetch(`${API_URL}/plans/${planId}/runs`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      throw new APIError(response.status, 'Failed to fetch runs for plan');
    }

    return response.json();
  },

  async create(planId: string, data: CreateRunRequest, token: string): Promise<Run> {
    const response = await fetch(`${API_URL}/plans/${planId}/runs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new APIError(response.status, error || 'Failed to create run');
    }

    return response.json();
  },
};

/**
 * Workouts API
 */
export const workouts = {
  async getForPlan(planId: string, token: string): Promise<Workout[]> {
    const response = await fetch(`${API_URL}/plans/${planId}/workouts`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      throw new APIError(response.status, 'Failed to fetch workouts');
    }

    return response.json();
  },

  async create(planId: string, data: CreateWorkoutRequest, token: string): Promise<Workout> {
    const response = await fetch(`${API_URL}/plans/${planId}/workouts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new APIError(response.status, error || 'Failed to create workout');
    }

    return response.json();
  },
};

/**
 * PDF Import API
 */
export const pdf = {
  async upload(
    file: File,
    planId: string,
    planStartDate: string,
    token: string
  ): Promise<{ status: string; workouts_created: number; workouts_failed: number; plan_id: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(
      `${API_URL}/import/pdf?plan_id=${encodeURIComponent(planId)}&plan_start_date=${encodeURIComponent(planStartDate)}`,
      {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      }
    );

    if (!response.ok) {
      const error = await response.text();
      throw new APIError(response.status, error || 'Failed to upload PDF');
    }

    return response.json();
  },
};

/**
 * Strava API
 */
export const strava = {
  async getAuthUrl(redirectUri: string): Promise<{ auth_url: string }> {
    const response = await fetch(
      `${API_URL}/strava/auth?redirect_uri=${encodeURIComponent(redirectUri)}`
    );

    if (!response.ok) {
      throw new APIError(response.status, 'Failed to get Strava auth URL');
    }

    return response.json();
  },

  async handleCallback(code: string, userId: string): Promise<{ status: string }> {
    const response = await fetch(
      `${API_URL}/strava/callback?code=${code}&user_id=${userId}`
    );

    if (!response.ok) {
      throw new APIError(response.status, 'Failed to handle Strava callback');
    }

    return response.json();
  },

  async sync(userId: string, planId: number, token: string): Promise<{
    status: string;
    runs_imported: number;
    plan_id: number;
  }> {
    const response = await fetch(
      `${API_URL}/strava/sync?user_id=${userId}&plan_id=${planId}`,
      {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    if (!response.ok) {
      throw new APIError(response.status, 'Failed to sync Strava');
    }

    return response.json();
  },
};
