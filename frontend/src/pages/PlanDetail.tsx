import { useEffect, useState } from 'react';
import { plans as plansApi, runs as runsApi, workouts as workoutsApi } from '../api';
import { useStore } from '../store';
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
  const [selectedWorkout, setSelectedWorkout] = useState<Workout | null>(null);

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
        planId,
        {
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
      <div className="min-h-screen bg-gradient-to-br from-spring-50 to-sky-50">
        <Header onNavigate={onNavigate} />
        <div className="max-w-6xl mx-auto p-6 text-center">
          <div className="text-spring-600 text-lg">Loading plan...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-spring-50 to-sky-50">
      <Header onNavigate={onNavigate} />

      <div className="max-w-7xl mx-auto p-6">
        <button
          onClick={() => onNavigate('dashboard')}
          className="text-spring-600 hover:text-spring-700 font-semibold mb-4 flex items-center gap-2 transition-colors"
        >
          <span>←</span> Back to Dashboard
        </button>

        {plan && (
          <>
            <div className="bg-white p-8 rounded-2xl shadow-lg mb-6 border-2 border-spring-200">
              <h1 className="text-4xl font-bold text-gray-800 mb-4">
                {plan.name}
              </h1>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div>
                  <span className="text-sm font-medium text-gray-600">Status</span>
                  <div className="text-lg font-semibold text-spring-700 capitalize">
                    {plan.status}
                  </div>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-600">Start Date</span>
                  <div className="text-lg font-semibold text-gray-800">
                    {new Date(plan.start_date).toLocaleDateString()}
                  </div>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-600">End Date</span>
                  <div className="text-lg font-semibold text-gray-800">
                    {new Date(plan.end_date).toLocaleDateString()}
                  </div>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-600">Progress</span>
                  <div className="text-lg font-semibold text-spring-600">
                    {calculateProgress()}% complete
                  </div>
                </div>
              </div>
              <div className="mt-4 bg-spring-100 rounded-full h-6 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-spring-500 to-spring-600 h-6 rounded-full transition-all duration-500 flex items-center justify-end pr-3"
                  style={{ width: `${calculateProgress()}%` }}
                >
                  {calculateProgress() > 10 && (
                    <span className="text-white text-xs font-bold">
                      {calculateProgress()}%
                    </span>
                  )}
                </div>
              </div>
            </div>

            {error && (
              <div className="bg-coral-50 border-2 border-coral-400 text-coral-700 p-4 rounded-lg mb-6">
                {error}
              </div>
            )}

            <div className="mb-6 flex flex-wrap gap-3">
              <button
                onClick={() => setShowAddRun(!showAddRun)}
                className="bg-spring-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-spring-600 transition-colors shadow-md hover:shadow-lg"
              >
                {showAddRun ? '✕ Cancel' : '+ Log Run'}
              </button>

              <button
                onClick={() => onNavigate('import-pdf')}
                className="bg-sky-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-sky-600 transition-colors shadow-md hover:shadow-lg"
              >
                📄 Import Workouts
              </button>
            </div>

            {showAddRun && (
              <div className="bg-white p-6 rounded-2xl shadow-lg mb-6 border-2 border-spring-200">
                <h2 className="text-2xl font-bold text-spring-700 mb-4">Log a Run</h2>
                <form onSubmit={handleAddRun} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Distance (miles)
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        value={newRun.distance_miles}
                        onChange={(e) =>
                          setNewRun({ ...newRun, distance_miles: e.target.value })
                        }
                        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-spring-500 focus:border-spring-500"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Pace (sec/mile)
                      </label>
                      <input
                        type="number"
                        value={newRun.pace_sec_per_mile}
                        onChange={(e) =>
                          setNewRun({ ...newRun, pace_sec_per_mile: e.target.value })
                        }
                        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-spring-500 focus:border-spring-500"
                        placeholder="e.g., 480 for 8:00/mi"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Date
                      </label>
                      <input
                        type="date"
                        value={newRun.date}
                        onChange={(e) =>
                          setNewRun({ ...newRun, date: e.target.value })
                        }
                        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-spring-500 focus:border-spring-500"
                        required
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="bg-spring-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-spring-600 disabled:bg-gray-400 transition-colors shadow-md"
                  >
                    {loading ? 'Adding...' : 'Add Run'}
                  </button>
                </form>
              </div>
            )}

            {/* Calendar View */}
            <div className="mb-8">
              {workouts.length === 0 ? (
                <div className="bg-white p-12 rounded-2xl shadow-lg text-center border-2 border-spring-200">
                  <div className="text-6xl mb-4">📅</div>
                  <h3 className="text-2xl font-bold text-gray-700 mb-2">
                    No Workouts Yet
                  </h3>
                  <p className="text-gray-600 mb-6">
                    Import a PDF to add workouts to your training plan.
                  </p>
                  <button
                    onClick={() => onNavigate('import-pdf')}
                    className="bg-spring-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-spring-600 transition-colors shadow-md"
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
              <div className="bg-white p-6 rounded-2xl shadow-lg border-2 border-spring-200">
                <h2 className="text-2xl font-bold text-spring-700 mb-4">
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
