import { useEffect, useState } from 'react';
import { plans as plansApi, runs as runsApi, workouts as workoutsApi } from '../api';
// import { useStore } from '../store';  // Auth removed
import { Plan, Run, Workout } from '../types';
import Header from '../components/Header';
import RunList from '../components/RunList';
import Calendar from '../components/Calendar';
import WorkoutDetailModal from '../components/WorkoutDetailModal';

interface PlanDetailProps {
  planId: string;
  onNavigate: (page: string, planId?: string) => void;
}

export default function PlanDetail({ planId, onNavigate }: PlanDetailProps) {
  // const user = useStore((state) => state.user);  // Auth removed

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
  const [selectedWorkout, setSelectedWorkout] = useState<Workout | null>(null);

  useEffect(() => {
    loadPlanData();
  }, [planId]);

  const loadPlanData = async () => {
    // if (!user?.token) return;  // Auth removed for easier deployment

    setLoading(true);
    setError('');

    try {
      const [planData, runsData, workoutsData] = await Promise.all([
        plansApi.getOne(planId),  // Removed token parameter
        runsApi.getForPlan(planId),  // Removed token parameter
        workoutsApi.getForPlan(planId),  // Removed token parameter
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
    // if (!user?.token) return;  // Auth removed for easier deployment

    setLoading(true);
    setError('');

    try {
      await runsApi.create(
        planId,
        {
          distance_miles: parseFloat(newRun.distance_miles),
          pace_sec_per_mile: parseInt(newRun.pace_sec_per_mile),
          date: newRun.date,
        }
        // user.token  // Removed token parameter
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
      runs.some((run) => run.date === workout.scheduled_date)
    );
    return Math.round((completedWorkouts.length / workouts.length) * 100);
  };

  const handleWorkoutClick = (workout: Workout) => {
    setSelectedWorkout(workout);
  };

  const getRunForWorkout = (workout: Workout): Run | undefined => {
    return runs.find((run) => run.date === workout.scheduled_date);
  };

  if (loading && !plan) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header onNavigate={onNavigate} />
        <div className="max-w-6xl mx-auto p-6 text-center">
          <div className="text-gray-600 text-lg">Loading plan...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header onNavigate={onNavigate} />

      <div className="max-w-7xl mx-auto p-6">
        <button
          onClick={() => onNavigate('dashboard')}
          className="text-primary-600 hover:text-primary-700 font-medium mb-4 flex items-center gap-2 transition-colors"
        >
          <span>←</span> Back to Dashboard
        </button>

        {plan && (
          <>
            <div className="bg-white p-8 rounded-lg shadow-sm mb-6 border border-gray-200">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                {plan.name}
              </h1>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div>
                  <span className="text-sm font-medium text-gray-600">Status</span>
                  <div className="text-lg font-semibold text-gray-900 capitalize">
                    {plan.status}
                  </div>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-600">Start Date</span>
                  <div className="text-lg font-semibold text-gray-900">
                    {new Date(plan.start_date).toLocaleDateString()}
                  </div>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-600">End Date</span>
                  <div className="text-lg font-semibold text-gray-900">
                    {new Date(plan.end_date).toLocaleDateString()}
                  </div>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-600">Progress</span>
                  <div className="text-lg font-semibold text-primary-600">
                    {calculateProgress()}%
                  </div>
                </div>
              </div>
              <div className="mt-4 bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-primary-600 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${calculateProgress()}%` }}
                />
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-6">
                {error}
              </div>
            )}

            <div className="mb-6 flex flex-wrap gap-3">
              <button
                onClick={() => setShowAddRun(!showAddRun)}
                className="bg-primary-600 text-white px-5 py-2.5 rounded-md text-sm font-medium hover:bg-primary-700 transition-colors"
              >
                {showAddRun ? 'Cancel' : 'Log Run'}
              </button>

              <button
                onClick={() => onNavigate('import-pdf')}
                className="bg-white text-gray-700 border border-gray-300 px-5 py-2.5 rounded-md text-sm font-medium hover:bg-gray-50 hover:border-primary-500 transition-colors"
              >
                Import Workouts
              </button>
            </div>

            {showAddRun && (
              <div className="bg-white p-6 rounded-lg shadow-sm mb-6 border border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Log a Run</h2>
                <form onSubmit={handleAddRun} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Distance (miles)
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        value={newRun.distance_miles}
                        onChange={(e) =>
                          setNewRun({ ...newRun, distance_miles: e.target.value })
                        }
                        className="w-full px-4 py-2.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Pace (sec/mile)
                      </label>
                      <input
                        type="number"
                        value={newRun.pace_sec_per_mile}
                        onChange={(e) =>
                          setNewRun({ ...newRun, pace_sec_per_mile: e.target.value })
                        }
                        className="w-full px-4 py-2.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                        placeholder="e.g., 480 for 8:00/mi"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Date
                      </label>
                      <input
                        type="date"
                        value={newRun.date}
                        onChange={(e) =>
                          setNewRun({ ...newRun, date: e.target.value })
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
                    {loading ? 'Adding...' : 'Add Run'}
                  </button>
                </form>
              </div>
            )}

            {/* Calendar View */}
            <div className="mb-8">
              {workouts.length === 0 ? (
                <div className="bg-white p-12 rounded-lg shadow-sm text-center border border-gray-200">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    No Workouts Yet
                  </h3>
                  <p className="text-gray-600 mb-6">
                    Import a PDF to add workouts to your training plan
                  </p>
                  <button
                    onClick={() => onNavigate('import-pdf')}
                    className="bg-primary-600 text-white px-5 py-2.5 rounded-md text-sm font-medium hover:bg-primary-700 transition-colors"
                  >
                    Import Workouts
                  </button>
                </div>
              ) : (
                <Calendar
                  workouts={workouts}
                  runs={runs}
                  startDate={plan.start_date}
                  endDate={plan.end_date}
                  onWorkoutClick={handleWorkoutClick}
                />
              )}
            </div>

            {/* Runs Summary */}
            {runs.length > 0 && (
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Recent Runs ({runs.length})
                </h2>
                <RunList runs={runs} formatPace={formatPace} />
              </div>
            )}
          </>
        )}

        {/* Workout Detail Modal */}
        {selectedWorkout && (
          <WorkoutDetailModal
            workout={selectedWorkout}
            run={getRunForWorkout(selectedWorkout)}
            onClose={() => setSelectedWorkout(null)}
            formatPace={formatPace}
          />
        )}
      </div>
    </div>
  );
}
