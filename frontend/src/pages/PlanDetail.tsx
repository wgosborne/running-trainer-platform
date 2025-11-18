import { useEffect, useState } from 'react';
import { plans as plansApi, runs as runsApi, workouts as workoutsApi } from '../api';
import { useStore } from '../store';
import { Plan, Run, Workout } from '../types';
import Header from '../components/Header';
import RunList from '../components/RunList';

interface PlanDetailProps {
  planId: number;
  onNavigate: (page: string, planId?: number) => void;
}

export default function PlanDetail({ planId, onNavigate }: PlanDetailProps) {
  const user = useStore((state) => state.user);

  const [plan, setPlan] = useState<Plan | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showAddRun, setShowAddRun] = useState(false);
  const [newRun, setNewRun] = useState({
    distance_miles: '',
    pace_sec_per_mile: '',
    date: new Date().toISOString().split('T')[0],
  });

  useEffect(() => {
    loadPlanData();
  }, [planId]);

  const loadPlanData = async () => {
    if (!user?.token) return;

    setLoading(true);
    setError('');

    try {
      const [planData, runsData, workoutsData] = await Promise.all([
        plansApi.getOne(planId, user.token),
        runsApi.getForPlan(planId, user.token),
        workoutsApi.getForPlan(planId, user.token),
      ]);

      setPlan(planData);
      setRuns(runsData);
      setWorkouts(workoutsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load plan data');
    } finally {
      setLoading(false);
    }
  };

  const handleAddRun = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user?.token) return;

    setLoading(true);
    setError('');

    try {
      await runsApi.create(
        {
          plan_id: planId,
          distance_miles: parseFloat(newRun.distance_miles),
          pace_sec_per_mile: parseInt(newRun.pace_sec_per_mile),
          date: newRun.date,
        },
        user.token
      );

      await loadPlanData();
      setShowAddRun(false);
      setNewRun({
        distance_miles: '',
        pace_sec_per_mile: '',
        date: new Date().toISOString().split('T')[0],
      });
    } catch (err: any) {
      setError(err.message || 'Failed to add run');
    } finally {
      setLoading(false);
    }
  };

  const formatPace = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const calculateProgress = () => {
    if (workouts.length === 0) return 0;
    const completedWorkouts = workouts.filter((workout) =>
      runs.some((run) => run.date === workout.planned_date)
    );
    return Math.round((completedWorkouts.length / workouts.length) * 100);
  };

  if (loading && !plan) {
    return (
      <div className="min-h-screen bg-gray-100">
        <Header onNavigate={onNavigate} />
        <div className="max-w-6xl mx-auto p-6 text-center">
          Loading plan...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header onNavigate={onNavigate} />

      <div className="max-w-6xl mx-auto p-6">
        <button
          onClick={() => onNavigate('dashboard')}
          className="text-blue-600 hover:underline mb-4"
        >
          ← Back to Dashboard
        </button>

        {plan && (
          <>
            <div className="bg-white p-6 rounded-lg shadow mb-6">
              <h1 className="text-3xl font-bold text-gray-800 mb-2">
                {plan.name}
              </h1>
              <div className="text-gray-600 space-y-1">
                <p>Status: {plan.status}</p>
                <p>Start Date: {plan.start_date}</p>
                <p>End Date: {plan.end_date}</p>
                <p>Progress: {calculateProgress()}% complete</p>
              </div>
              <div className="mt-4 bg-gray-200 rounded-full h-4">
                <div
                  className="bg-blue-600 h-4 rounded-full"
                  style={{ width: `${calculateProgress()}%` }}
                ></div>
              </div>
            </div>

            {error && (
              <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
                {error}
              </div>
            )}

            <div className="mb-6 flex gap-3">
              <button
                onClick={() => setShowAddRun(!showAddRun)}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                {showAddRun ? 'Cancel' : '+ Log Run'}
              </button>

              <button
                onClick={() => onNavigate('import-pdf')}
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
              >
                Import Workouts
              </button>
            </div>

            {showAddRun && (
              <div className="bg-white p-6 rounded-lg shadow mb-6">
                <h2 className="text-xl font-semibold mb-4">Log a Run</h2>
                <form onSubmit={handleAddRun} className="space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Distance (miles)
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        value={newRun.distance_miles}
                        onChange={(e) =>
                          setNewRun({ ...newRun, distance_miles: e.target.value })
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Pace (sec/mile)
                      </label>
                      <input
                        type="number"
                        value={newRun.pace_sec_per_mile}
                        onChange={(e) =>
                          setNewRun({ ...newRun, pace_sec_per_mile: e.target.value })
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., 480 for 8:00/mi"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Date
                      </label>
                      <input
                        type="date"
                        value={newRun.date}
                        onChange={(e) =>
                          setNewRun({ ...newRun, date: e.target.value })
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
                    {loading ? 'Adding...' : 'Add Run'}
                  </button>
                </form>
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-2xl font-semibold mb-4">
                  Workouts ({workouts.length})
                </h2>
                {workouts.length === 0 ? (
                  <p className="text-gray-500">
                    No workouts yet. Import a PDF to add workouts.
                  </p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2">Date</th>
                          <th className="text-left py-2">Type</th>
                          <th className="text-right py-2">Distance</th>
                        </tr>
                      </thead>
                      <tbody>
                        {workouts.slice(0, 10).map((workout) => {
                          const hasRun = runs.some(
                            (run) => run.date === workout.planned_date
                          );
                          return (
                            <tr
                              key={workout.id}
                              className={`border-b ${
                                hasRun ? 'bg-green-50' : ''
                              }`}
                            >
                              <td className="py-2">
                                {workout.planned_date || '-'}
                              </td>
                              <td className="py-2">{workout.workout_type}</td>
                              <td className="text-right py-2">
                                {workout.planned_distance} mi
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                    {workouts.length > 10 && (
                      <p className="text-sm text-gray-500 mt-2">
                        Showing 10 of {workouts.length} workouts
                      </p>
                    )}
                  </div>
                )}
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-2xl font-semibold mb-4">
                  Runs ({runs.length})
                </h2>
                <RunList runs={runs} formatPace={formatPace} />
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
