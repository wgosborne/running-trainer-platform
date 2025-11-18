/**
 * Global state management using Zustand
 */

import { create } from 'zustand';
import { User, Plan, Run } from './types';

interface AppState {
  user: User | null;
  plans: Plan[];
  runs: Run[];
  currentPlan: Plan | null;
  setUser: (user: User | null) => void;
  setPlans: (plans: Plan[]) => void;
  setRuns: (runs: Run[]) => void;
  setCurrentPlan: (plan: Plan | null) => void;
  logout: () => void;
}

export const useStore = create<AppState>((set) => ({
  user: null,
  plans: [],
  runs: [],
  currentPlan: null,

  setUser: (user) => set({ user }),

  setPlans: (plans) => set({ plans }),

  setRuns: (runs) => set({ runs }),

  setCurrentPlan: (plan) => set({ currentPlan: plan }),

  logout: () => set({
    user: null,
    plans: [],
    runs: [],
    currentPlan: null
  }),
}));
