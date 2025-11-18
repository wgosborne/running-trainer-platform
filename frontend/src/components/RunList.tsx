import { Run } from '../types';

interface RunListProps {
  runs: Run[];
  formatPace: (seconds: number) => string;
}

export default function RunList({ runs, formatPace }: RunListProps) {
  if (runs.length === 0) {
    return (
      <p className="text-gray-500">
        No runs logged yet. Add your first run or sync from Strava.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b">
            <th className="text-left py-2">Date</th>
            <th className="text-right py-2">Distance</th>
            <th className="text-right py-2">Pace</th>
            <th className="text-left py-2">Source</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr key={run.id} className="border-b hover:bg-gray-50">
              <td className="py-2">{run.date}</td>
              <td className="text-right py-2">
                {run.distance_miles.toFixed(2)} mi
              </td>
              <td className="text-right py-2">
                {formatPace(run.pace_sec_per_mile)}/mi
              </td>
              <td className="py-2">
                {run.source ? (
                  <span
                    className={`px-2 py-1 rounded text-xs ${
                      run.source === 'strava'
                        ? 'bg-orange-100 text-orange-800'
                        : 'bg-blue-100 text-blue-800'
                    }`}
                  >
                    {run.source}
                  </span>
                ) : (
                  <span className="text-gray-400">manual</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
