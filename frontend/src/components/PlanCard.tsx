import { Plan } from '../types';

interface PlanCardProps {
  plan: Plan;
  onClick: () => void;
}

export default function PlanCard({ plan, onClick }: PlanCardProps) {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-primary-50 text-primary-700 border-primary-200';
      case 'completed':
        return 'bg-gray-100 text-gray-700 border-gray-200';
      case 'planning':
        return 'bg-gray-50 text-gray-600 border-gray-200';
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
      className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer border border-gray-200 hover:border-primary-500"
    >
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-gray-900">{plan.name}</h3>
        <span
          className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(
            plan.status
          )}`}
        >
          {plan.status}
        </span>
      </div>

      {plan.description && (
        <p className="text-sm text-gray-600 mb-4 line-clamp-2">
          {plan.description}
        </p>
      )}

      <div className="text-sm text-gray-600 space-y-1.5 mb-4">
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-700">Duration:</span>
          <span>{Math.ceil(plan.duration_days / 7)} week{Math.ceil(plan.duration_days / 7) !== 1 ? 's' : ''}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-700">Start:</span>
          <span>{formatDate(plan.start_date)}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-700">End:</span>
          <span>{formatDate(plan.end_date)}</span>
        </div>
      </div>

      <div className="text-xs text-gray-500 pt-3 border-t border-gray-100">
        <p>Created {formatDate(plan.created_at)}</p>
      </div>

      <div className="mt-4 pt-3 border-t border-gray-100 text-primary-600 text-sm font-medium hover:text-primary-700 flex items-center justify-between">
        <span>View details</span>
        <span className="text-lg">→</span>
      </div>
    </div>
  );
}
