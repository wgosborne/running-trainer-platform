/**
 * Type definitions for Running Tracker application
 */

export interface User {
  id: number;
  email: string;
  token: string;
}

export interface Plan {
  id: string;  // UUID
  name: string;
  description: string | null;
  start_date: string;
  end_date: string;
  status: string;
  created_at: string;
  updated_at: string;
  duration_days: number;
}

export interface Workout {
  id: string;  // UUID
  plan_id: string;  // UUID
  name: string;
  workout_type: string;
  planned_distance: number;
  target_pace_min_sec: number | null;
  target_pace_max_sec: number | null;
  scheduled_date: string | null;
  notes: string | null;
  pace_range_str: string | null;
  created_at: string;
  updated_at: string;
}

export interface Run {
  id: string;  // UUID
  plan_id: string;  // UUID
  workout_id: string | null;  // UUID
  distance_miles: number;
  pace_sec_per_mile: number;
  date: string;
  source: string;
  notes: string | null;
  pace_str: string;
  created_at: string;
  updated_at: string;
  external_id?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  token: string;
  user_id: string;
}

export interface RegisterResponse {
  user_id: string;
  email: string;
}

export interface CreatePlanRequest {
  name: string;
  description?: string;
  start_date: string;  // Required
  end_date: string;    // Required
}

export interface CreateWorkoutRequest {
  name: string;
  workout_type: string;
  planned_distance: number;
  target_pace_min_sec?: number;
  target_pace_max_sec?: number;
  scheduled_date?: string;
  notes?: string;
}

export interface CreateRunRequest {
  distance_miles: number;
  pace_sec_per_mile: number;
  date: string;
  workout_id?: string;
  notes?: string;
  source?: string;
  external_id?: string;
}
