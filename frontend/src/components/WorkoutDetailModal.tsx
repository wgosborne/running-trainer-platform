import { Workout, Run } from '../types';

interface WorkoutDetailModalProps {
  workout: Workout;
  run?: Run;
  onClose: () => void;
  formatPace: (seconds: number) => string;
}

export default function WorkoutDetailModal({
  workout,
  run,
  onClose,
  formatPace,
}: WorkoutDetailModalProps) {
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-spring-500 to-spring-600 px-6 py-6 rounded-t-2xl">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">
                {workout.name}
              </h2>
              <div className="text-spring-100 text-sm">
                {workout.scheduled_date && formatDate(workout.scheduled_date)}
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-spring-100 text-3xl font-bold leading-none transition-colors"
            >
              ×
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6">
          {/* Completion Status */}
          {run ? (
            <div className="bg-spring-50 border-2 border-spring-500 rounded-xl p-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 bg-spring-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xl font-bold">✓</span>
                </div>
                <h3 className="text-lg font-semibold text-spring-800">
                  Completed
                </h3>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Date:</span>
                  <div className="font-semibold text-gray-800">{formatDate(run.date)}</div>
                </div>
                <div>
                  <span className="text-gray-600">Source:</span>
                  <div className="font-semibold text-gray-800 capitalize">{run.source}</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-sunshine-50 border-2 border-sunshine-300 rounded-xl p-4">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-sunshine-400 rounded-full flex items-center justify-center">
                  <span className="text-white text-xl">⏱</span>
                </div>
                <h3 className="text-lg font-semibold text-sunshine-800">
                  Planned - Not Yet Completed
                </h3>
              </div>
            </div>
          )}

          {/* Full Workout Description from PDF */}
          {workout.notes && (
            <div className="bg-spring-50 rounded-xl p-5 border-2 border-spring-300">
              <h3 className="text-xl font-semibold text-spring-800 mb-3 flex items-center gap-2">
                <span>📋</span> Full Description
              </h3>
              <div className="bg-white p-4 rounded-lg border border-spring-200 text-gray-800 font-mono text-sm whitespace-pre-wrap leading-relaxed">
                {workout.notes}
              </div>
            </div>
          )}

          {/* Workout Details */}
          <div className="bg-gray-50 rounded-xl p-5 space-y-4">
            <h3 className="text-xl font-semibold text-gray-800 border-b-2 border-spring-300 pb-2">
              Workout Summary
            </h3>

            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="text-sm font-medium text-gray-600">Type</label>
                <div className="text-lg font-semibold text-gray-800 mt-1">
                  {workout.workout_type}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-600">Planned Distance</label>
                <div className="text-lg font-semibold text-gray-800 mt-1">
                  {workout.planned_distance} miles
                </div>
              </div>

              {workout.target_pace_min_sec !== null && workout.target_pace_max_sec !== null && (
                <div className="col-span-2">
                  <label className="text-sm font-medium text-gray-600">Target Pace Range</label>
                  <div className="text-lg font-semibold text-gray-800 mt-1">
                    {formatPace(workout.target_pace_min_sec)} - {formatPace(workout.target_pace_max_sec)} per mile
                  </div>
                </div>
              )}

              {workout.pace_range_str && (
                <div className="col-span-2">
                  <label className="text-sm font-medium text-gray-600">Pace Description</label>
                  <div className="text-lg font-semibold text-gray-800 mt-1">
                    {workout.pace_range_str}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Run Details (if completed) */}
          {run && (
            <div className="bg-spring-50 rounded-xl p-5 space-y-4">
              <h3 className="text-xl font-semibold text-spring-800 border-b-2 border-spring-300 pb-2">
                Actual Run Data
              </h3>

              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="text-sm font-medium text-spring-700">Distance</label>
                  <div className="text-lg font-semibold text-spring-900 mt-1">
                    {run.distance_miles} miles
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-spring-700">Actual Pace</label>
                  <div className="text-lg font-semibold text-spring-900 mt-1">
                    {formatPace(run.pace_sec_per_mile)} per mile
                  </div>
                </div>

                {run.external_id && (
                  <div className="col-span-2">
                    <label className="text-sm font-medium text-spring-700">Strava Activity ID</label>
                    <div className="text-sm text-spring-800 mt-1 font-mono">
                      {run.external_id}
                    </div>
                  </div>
                )}
              </div>

              {run.notes && (
                <div>
                  <label className="text-sm font-medium text-spring-700">Run Notes</label>
                  <div className="mt-1 p-3 bg-white rounded border border-spring-300 text-spring-900">
                    {run.notes}
                  </div>
                </div>
              )}

              {/* Comparison */}
              {workout.planned_distance && (
                <div className="bg-white rounded-lg p-4 border-2 border-spring-300">
                  <h4 className="font-semibold text-spring-800 mb-3">Performance Comparison</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Distance Variance:</span>
                      <span className={`font-semibold ${
                        Math.abs(run.distance_miles - workout.planned_distance) < 0.5
                          ? 'text-spring-600'
                          : 'text-peach-600'
                      }`}>
                        {(run.distance_miles - workout.planned_distance).toFixed(2)} mi
                      </span>
                    </div>

                    {workout.target_pace_min_sec !== null && workout.target_pace_max_sec !== null && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Pace Status:</span>
                        <span className={`font-semibold ${
                          run.pace_sec_per_mile >= workout.target_pace_min_sec &&
                          run.pace_sec_per_mile <= workout.target_pace_max_sec
                            ? 'text-spring-600'
                            : run.pace_sec_per_mile < workout.target_pace_min_sec
                            ? 'text-sky-600'
                            : 'text-coral-600'
                        }`}>
                          {run.pace_sec_per_mile >= workout.target_pace_min_sec &&
                          run.pace_sec_per_mile <= workout.target_pace_max_sec
                            ? '✓ On Target'
                            : run.pace_sec_per_mile < workout.target_pace_min_sec
                            ? '↑ Faster'
                            : '↓ Slower'}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Metadata */}
          <div className="text-xs text-gray-500 pt-4 border-t border-gray-200 space-y-1">
            <div>Workout ID: {workout.id}</div>
            <div>Created: {new Date(workout.created_at).toLocaleString()}</div>
            <div>Updated: {new Date(workout.updated_at).toLocaleString()}</div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 rounded-b-2xl border-t border-gray-200">
          <button
            onClick={onClose}
            className="w-full bg-spring-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-spring-600 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
