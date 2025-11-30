import { Run } from '../types';

interface RunListProps {
  runs: Run[];
  formatPace: (seconds: number) => string;
}

export default function RunList({ runs, formatPace }: RunListProps) {
  if (runs.length === 0) {
    return (
      <div className="text-center py-8 bg-spring-50 rounded-lg border-2 border-spring-200">
        <div className="text-4xl mb-2">🏃</div>
        <p className="text-gray-600">
          No runs logged yet. Add your first run or sync from Strava.
        </p>
      </div>
    );
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b-2 border-spring-300 bg-spring-50">
            <th className="text-left py-3 px-2 font-semibold text-spring-800">Date</th>
            <th className="text-right py-3 px-2 font-semibold text-spring-800">Distance</th>
            <th className="text-right py-3 px-2 font-semibold text-spring-800">Pace</th>
            <th className="text-left py-3 px-2 font-semibold text-spring-800">Source</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr key={run.id} className="border-b border-spring-200 hover:bg-spring-50 transition-colors">
              <td className="py-3 px-2 font-medium text-gray-700">
                {formatDate(run.date)}
              </td>
              <td className="text-right py-3 px-2 font-semibold text-gray-800">
                {run.distance_miles.toFixed(2)} mi
              </td>
              <td className="text-right py-3 px-2 font-mono font-semibold text-spring-700">
                {formatPace(run.pace_sec_per_mile)}/mi
              </td>
              <td className="py-3 px-2">
                {run.source ? (
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold border-2 ${
                      run.source === 'strava'
                        ? 'bg-peach-100 text-peach-800 border-peach-300'
                        : 'bg-sky-100 text-sky-800 border-sky-300'
                    }`}
                  >
                    {run.source === 'strava' ? '🏃 Strava' : '✍️ Manual'}
                  </span>
                ) : (
                  <span className="px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-600 border-2 border-gray-300">
                    ✍️ Manual
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
