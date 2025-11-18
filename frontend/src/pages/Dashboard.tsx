import { useEffect, useState } from 'react';
import { plans as plansApi, strava } from '../api';
import { useStore } from '../store';
import PlanCard from '../components/PlanCard';
import Header from '../components/Header';
import { CreatePlanRequest } from '../types';

interface DashboardProps {
  onNavigate: (page: string, planId?: number) => void;
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
    if (!user?.token) return;

    setLoading(true);
    setError('');

    try {
      const data = await plansApi.getAll(user.token);
      setPlans(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load plans');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user?.token) return;

    setLoading(true);
    setError('');

    try {
      await plansApi.create(newPlan, user.token);
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
    if (!user?.token || plans.length === 0) {
      setSyncMessage('Please create a plan first');
      return;
    }

    setSyncing(true);
    setSyncMessage('');

    try {
      const result = await strava.sync(
        user.id.toString(),
        plans[0].id,
        user.token
      );
      setSyncMessage(`✓ Synced ${result.runs_imported} runs from Strava`);
    } catch (err: any) {
      setSyncMessage(`Error: ${err.message}`);
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header onNavigate={onNavigate} />

      <div className="max-w-6xl mx-auto p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800">
            Welcome, {user?.email}
          </h1>
          <p className="text-gray-600 mt-1">Manage your training plans</p>
        </div>

        {error && (
          <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
            {error}
          </div>
        )}

        {syncMessage && (
          <div className={`p-3 rounded mb-4 ${
            syncMessage.includes('✓')
              ? 'bg-green-100 text-green-700'
              : 'bg-red-100 text-red-700'
          }`}>
            {syncMessage}
          </div>
        )}

        <div className="mb-6 flex gap-3">
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            {showCreateForm ? 'Cancel' : '+ Create Plan'}
          </button>

          <button
            onClick={() => onNavigate('import-pdf')}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Import PDF
          </button>

          <button
            onClick={() => onNavigate('strava-auth')}
            className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
          >
            Strava Settings
          </button>

          <button
            onClick={handleStravaSync}
            disabled={syncing || plans.length === 0}
            className="bg-orange-600 text-white px-4 py-2 rounded hover:bg-orange-700 disabled:bg-gray-400"
          >
            {syncing ? 'Syncing...' : 'Sync Strava'}
          </button>
        </div>

        {showCreateForm && (
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h2 className="text-xl font-semibold mb-4">Create New Plan</h2>
            <form onSubmit={handleCreatePlan} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  Plan Name
                </label>
                <input
                  type="text"
                  value={newPlan.name}
                  onChange={(e) =>
                    setNewPlan({ ...newPlan, name: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Marathon Training"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  Description (Optional)
                </label>
                <textarea
                  value={newPlan.description}
                  onChange={(e) =>
                    setNewPlan({ ...newPlan, description: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Training for Boston Marathon qualification"
                  rows={2}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={newPlan.start_date}
                    onChange={(e) =>
                      setNewPlan({ ...newPlan, start_date: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={newPlan.end_date}
                    onChange={(e) =>
                      setNewPlan({ ...newPlan, end_date: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
              >
                {loading ? 'Creating...' : 'Create Plan'}
              </button>
            </form>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {loading && plans.length === 0 ? (
            <div className="col-span-full text-center py-12 text-gray-500">
              Loading plans...
            </div>
          ) : plans.length === 0 ? (
            <div className="col-span-full text-center py-12 text-gray-500">
              No plans yet. Create your first training plan!
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
