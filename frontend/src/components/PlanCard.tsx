import { Plan } from '../types';

interface PlanCardProps {
  plan: Plan;
  onClick: () => void;
}

export default function PlanCard({ plan, onClick }: PlanCardProps) {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-spring-100 text-spring-800 border-spring-300';
      case 'completed':
        return 'bg-sky-100 text-sky-800 border-sky-300';
      case 'planning':
        return 'bg-sunshine-100 text-sunshine-800 border-sunshine-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
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
      className="bg-white p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer border-2 border-spring-200 hover:border-spring-400 hover:scale-105"
    >
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-bold text-gray-800">{plan.name}</h3>
        <span
          className={`px-3 py-1 rounded-full text-xs font-semibold border-2 ${getStatusColor(
            plan.status
          )}`}
        >
          {plan.status}
        </span>
      </div>

      {plan.description && (
        <p className="text-sm text-gray-600 mb-4 italic line-clamp-2 bg-spring-50 p-3 rounded-lg border-l-4 border-spring-400">
          "{plan.description}"
        </p>
      )}

      <div className="text-sm text-gray-700 space-y-2 mb-4">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-spring-700">📅 Duration:</span>
          <span>{Math.ceil(plan.duration_days / 7)} week{Math.ceil(plan.duration_days / 7) !== 1 ? 's' : ''} ({plan.duration_days} days)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-semibold text-spring-700">🏁 Start:</span>
          <span>{formatDate(plan.start_date)}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-semibold text-spring-700">🎯 End:</span>
          <span>{formatDate(plan.end_date)}</span>
        </div>
      </div>

      <div className="text-xs text-gray-500 pt-3 border-t border-spring-200 space-y-1">
        <p>Created: {formatDate(plan.created_at)}</p>
        {plan.updated_at !== plan.created_at && (
          <p>Updated: {formatDate(plan.updated_at)}</p>
        )}
      </div>

      <div className="mt-4 pt-3 border-t border-spring-200 text-spring-600 text-sm font-bold hover:text-spring-700 flex items-center justify-between">
        <span>View details</span>
        <span className="text-lg">→</span>
      </div>
    </div>
  );
}
