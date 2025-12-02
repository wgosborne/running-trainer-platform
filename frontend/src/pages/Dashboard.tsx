import { useEffect, useState } from 'react';
import { plans as plansApi, strava } from '../api';
import { useStore } from '../store';
import PlanCard from '../components/PlanCard';
import Header from '../components/Header';
import { CreatePlanRequest } from '../types';

interface DashboardProps {
  onNavigate: (page: string, planId?: string) => void;
}

export default function Dashboard({ onNavigate }: DashboardProps) {
  const user = useStore((state) => state.user);
  const plans = useStore((state) => state.plans);
  const setPlans = useStore((state) => state.setPlans);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newPlan, setNewPlan] = useState<CreatePlanRequest>({
    name: '',
    description: '',
    start_date: '',
    end_date: '',
  });
  const [syncing, setSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState('');

  useEffect(() => {
    loadPlans();
  }, []);

  const loadPlans = async () => {
    // if (!user?.token) return;  // Auth removed for easier deployment

    setLoading(true);
    setError('');

    try {
      const data = await plansApi.getAll();  // Removed token parameter
      setPlans(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load plans');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    // if (!user?.token) return;  // Auth removed for easier deployment

    setLoading(true);
    setError('');

    try {
      await plansApi.create(newPlan);  // Removed token parameter
      await loadPlans();
      setShowCreateForm(false);
      setNewPlan({ name: '', description: '', start_date: '', end_date: '' });
    } catch (err: any) {
      setError(err.message || 'Failed to create plan');
    } finally {
      setLoading(false);
    }
  };

  const handleStravaSync = async () => {
    if (plans.length === 0) {  // Removed user?.token check
      setSyncMessage('Please create a plan first');
      return;
    }

    setSyncing(true);
    setSyncMessage('');

    try {
      const result = await strava.sync(
        user?.id.toString() || '1',  // Default user ID if not available
        plans[0].id
        // user.token  // Removed token parameter
      );
      setSyncMessage(`✓ Synced ${result.runs_imported} runs from Strava`);
    } catch (err: any) {
      setSyncMessage(`Error: ${err.message}`);
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header onNavigate={onNavigate} />

      <div className="max-w-7xl mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            {user?.email ? `Welcome, ${user.email}` : 'Welcome'}
          </h1>
          <p className="text-gray-600 mt-1">Manage your training plans and track your progress</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {syncMessage && (
          <div className={`p-4 rounded-lg mb-6 border ${
            syncMessage.includes('✓') || syncMessage.includes('Synced')
              ? 'bg-primary-50 border-primary-200 text-primary-700'
              : 'bg-red-50 border-red-200 text-red-700'
          }`}>
            {syncMessage}
          </div>
        )}

        <div className="mb-6 flex flex-wrap gap-3">
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="bg-primary-600 text-white px-5 py-2.5 rounded-md text-sm font-medium hover:bg-primary-700 transition-colors"
          >
            {showCreateForm ? 'Cancel' : 'Create Plan'}
          </button>

          <button
            onClick={() => onNavigate('import-pdf')}
            className="bg-white text-gray-700 border border-gray-300 px-5 py-2.5 rounded-md text-sm font-medium hover:bg-gray-50 hover:border-primary-500 transition-colors"
          >
            Import PDF
          </button>

          <button
            onClick={() => onNavigate('strava-auth')}
            className="bg-white text-gray-700 border border-gray-300 px-5 py-2.5 rounded-md text-sm font-medium hover:bg-gray-50 hover:border-primary-500 transition-colors"
          >
            Strava Settings
          </button>

          <button
            onClick={handleStravaSync}
            disabled={syncing || plans.length === 0}
            className="bg-white text-gray-700 border border-gray-300 px-5 py-2.5 rounded-md text-sm font-medium hover:bg-gray-50 hover:border-primary-500 disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {syncing ? 'Syncing...' : 'Sync Strava'}
          </button>
        </div>

        {showCreateForm && (
          <div className="bg-white p-6 rounded-lg shadow-sm mb-6 border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Create New Plan</h2>
            <form onSubmit={handleCreatePlan} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Plan Name
                </label>
                <input
                  type="text"
                  value={newPlan.name}
                  onChange={(e) =>
                    setNewPlan({ ...newPlan, name: e.target.value })
                  }
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="e.g., Marathon Training"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description (Optional)
                </label>
                <textarea
                  value={newPlan.description}
                  onChange={(e) =>
                    setNewPlan({ ...newPlan, description: e.target.value })
                  }
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="e.g., Training for Boston Marathon qualification"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={newPlan.start_date}
                    onChange={(e) =>
                      setNewPlan({ ...newPlan, start_date: e.target.value })
                    }
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={newPlan.end_date}
                    onChange={(e) =>
                      setNewPlan({ ...newPlan, end_date: e.target.value })
                    }
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="bg-primary-600 text-white px-5 py-2.5 rounded-md text-sm font-medium hover:bg-primary-700 disabled:bg-gray-400 transition-colors"
              >
                {loading ? 'Creating...' : 'Create Plan'}
              </button>
            </form>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading && plans.length === 0 ? (
            <div className="col-span-full text-center py-16">
              <div className="text-gray-600 text-lg">Loading plans...</div>
            </div>
          ) : plans.length === 0 ? (
            <div className="col-span-full">
              <div className="bg-white rounded-lg shadow-sm p-12 text-center border border-gray-200">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  No Plans Yet
                </h3>
                <p className="text-gray-600 mb-6">
                  Create your first training plan to get started
                </p>
                <button
                  onClick={() => setShowCreateForm(true)}
                  className="bg-primary-600 text-white px-5 py-2.5 rounded-md text-sm font-medium hover:bg-primary-700 transition-colors"
                >
                  Create Your First Plan
                </button>
              </div>
            </div>
          ) : (
            plans.map((plan) => (
              <PlanCard
                key={plan.id}
                plan={plan}
                onClick={() => onNavigate('plan-detail', plan.id)}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
