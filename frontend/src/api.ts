/**
 * API client for Running Tracker backend
 */

import {
  // LoginRequest,  // Auth commented out
  // RegisterRequest,  // Auth commented out
  // AuthResponse,  // Auth commented out
  // RegisterResponse,  // Auth commented out
  Plan,
  Run,
  Workout,
  CreatePlanRequest,
  CreateWorkoutRequest,
  CreateRunRequest
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_URL = `${API_BASE_URL}/api/v1`;

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
 * Authentication API - COMMENTED OUT FOR EASIER DEPLOYMENT
 */
// export const auth = {
//   async register(data: RegisterRequest): Promise<RegisterResponse> {
//     const response = await fetch(`${API_URL}/auth/register`, {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({
//         email: data.email,
//         password: data.password,
//       }),
//     });
//
//     if (!response.ok) {
//       const error = await response.text();
//       throw new APIError(response.status, error || 'Registration failed');
//     }
//
//     return response.json();
//   },
//
//   async login(data: LoginRequest): Promise<AuthResponse> {
//     const response = await fetch(`${API_URL}/auth/login`, {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({
//         email: data.email,
//         password: data.password,
//       }),
//     });
//
//     if (!response.ok) {
//       const error = await response.text();
//       throw new APIError(response.status, error || 'Login failed');
//     }
//
//     return response.json();
//   },
// };

/**
 * Plans API - Auth tokens removed for easier deployment
 */
export const plans = {
  async getAll(): Promise<Plan[]> {  // Removed token parameter
    const response = await fetch(`${API_URL}/plans`);  // Removed Authorization header

    if (!response.ok) {
      throw new APIError(response.status, 'Failed to fetch plans');
    }

    return response.json();
  },

  async getOne(id: string): Promise<Plan> {  // Removed token parameter
    const response = await fetch(`${API_URL}/plans/${id}`);  // Removed Authorization header

    if (!response.ok) {
      throw new APIError(response.status, 'Failed to fetch plan');
    }

    return response.json();
  },

  async create(data: CreatePlanRequest): Promise<Plan> {  // Removed token parameter
    const response = await fetch(`${API_URL}/plans`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Authorization header removed
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
 * Runs API - Auth tokens removed for easier deployment
 */
export const runs = {
  async getAll(): Promise<Run[]> {  // Removed token parameter
    const response = await fetch(`${API_URL}/runs`);  // Removed Authorization header

    if (!response.ok) {
      throw new APIError(response.status, 'Failed to fetch runs');
    }

    return response.json();
  },

  async getForPlan(planId: string): Promise<Run[]> {  // Removed token parameter
    const response = await fetch(`${API_URL}/plans/${planId}/runs`);  // Removed Authorization header

    if (!response.ok) {
      throw new APIError(response.status, 'Failed to fetch runs for plan');
    }

    return response.json();
  },

  async create(planId: string, data: CreateRunRequest): Promise<Run> {  // Removed token parameter
    const response = await fetch(`${API_URL}/plans/${planId}/runs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Authorization header removed
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
 * Workouts API - Auth tokens removed for easier deployment
 */
export const workouts = {
  async getForPlan(planId: string): Promise<Workout[]> {  // Removed token parameter
    const response = await fetch(`${API_URL}/plans/${planId}/workouts`);  // Removed Authorization header

    if (!response.ok) {
      throw new APIError(response.status, 'Failed to fetch workouts');
    }

    return response.json();
  },

  async create(planId: string, data: CreateWorkoutRequest): Promise<Workout> {  // Removed token parameter
    const response = await fetch(`${API_URL}/plans/${planId}/workouts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Authorization header removed
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
 * PDF Import API - Auth tokens removed for easier deployment
 */
export const pdf = {
  async upload(
    file: File,
    planId: string,
    planStartDate: string
    // token: string  // Removed token parameter
  ): Promise<{ status: string; workouts_created: number; workouts_failed: number; plan_id: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(
      `${API_URL}/import/pdf?plan_id=${encodeURIComponent(planId)}&plan_start_date=${encodeURIComponent(planStartDate)}`,
      {
        method: 'POST',
        // headers: { Authorization: `Bearer ${token}` },  // Authorization header removed
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

  async sync(userId: string, planId: string): Promise<{  // Removed token parameter
    status: string;
    runs_imported: number;
    plan_id: string;
  }> {
    const response = await fetch(
      `${API_URL}/strava/sync?user_id=${userId}&plan_id=${planId}`,
      {
        method: 'POST',
        // headers: { Authorization: `Bearer ${token}` },  // Authorization header removed
      }
    );

    if (!response.ok) {
      throw new APIError(response.status, 'Failed to sync Strava');
    }

    return response.json();
  },
};
