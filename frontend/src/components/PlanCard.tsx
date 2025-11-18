import { Plan } from '../types';

interface PlanCardProps {
  plan: Plan;
  onClick: () => void;
}

export default function PlanCard({ plan, onClick }: PlanCardProps) {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'planning':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div
      onClick={onClick}
      className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
    >
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-xl font-semibold text-gray-800">{plan.name}</h3>
        <span
          className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
            plan.status
          )}`}
        >
          {plan.status}
        </span>
      </div>

      {plan.description && (
        <p className="text-sm text-gray-600 mb-3 italic line-clamp-2">
          "{plan.description}"
        </p>
      )}

      <div className="text-sm text-gray-600 space-y-1 mb-3">
        <p>
          <span className="font-medium">Duration:</span>{' '}
          {Math.ceil(plan.duration_days / 7)} week{Math.ceil(plan.duration_days / 7) !== 1 ? 's' : ''} ({plan.duration_days} days)
        </p>
        <p>
          <span className="font-medium">Start:</span> {formatDate(plan.start_date)}
        </p>
        <p>
          <span className="font-medium">End:</span> {formatDate(plan.end_date)}
        </p>
      </div>

      <div className="text-xs text-gray-400 pt-3 border-t border-gray-200">
        <p>Created: {formatDate(plan.created_at)}</p>
        {plan.updated_at !== plan.created_at && (
          <p>Updated: {formatDate(plan.updated_at)}</p>
        )}
      </div>

      <div className="mt-4 pt-2 border-t border-gray-200 text-blue-600 text-sm font-medium hover:text-blue-700">
        View details →
      </div>
    </div>
  );
}
