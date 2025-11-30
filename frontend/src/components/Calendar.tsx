import { Workout, Run } from '../types';

interface CalendarProps {
  workouts: Workout[];
  runs: Run[];
  startDate: string;
  endDate: string;
  onWorkoutClick: (workout: Workout) => void;
}

interface CalendarDay {
  date: Date;
  isCurrentMonth: boolean;
  workout?: Workout;
  hasRun: boolean;
}

export default function Calendar({
  workouts,
  runs,
  startDate,
  endDate,
  onWorkoutClick,
}: CalendarProps) {
  const start = new Date(startDate);
  const end = new Date(endDate);

  // Generate months between start and end date
  const generateMonths = () => {
    const months: Date[] = [];
    const current = new Date(start);
    current.setDate(1); // Start from first day of month

    while (current <= end) {
      months.push(new Date(current));
      current.setMonth(current.getMonth() + 1);
    }

    return months;
  };

  // Generate calendar days for a specific month
  const generateCalendarDays = (monthDate: Date): CalendarDay[] => {
    const year = monthDate.getFullYear();
    const month = monthDate.getMonth();

    // Get first day of month and its weekday
    const firstDay = new Date(year, month, 1);
    const firstDayWeekday = firstDay.getDay();

    // Get last day of month
    const lastDay = new Date(year, month + 1, 0);
    const lastDate = lastDay.getDate();

    const days: CalendarDay[] = [];

    // Add previous month's days to fill the first week
    const prevMonthLastDay = new Date(year, month, 0);
    for (let i = firstDayWeekday - 1; i >= 0; i--) {
      const date = new Date(year, month - 1, prevMonthLastDay.getDate() - i);
      days.push({
        date,
        isCurrentMonth: false,
        hasRun: false,
      });
    }

    // Add current month's days
    for (let date = 1; date <= lastDate; date++) {
      const currentDate = new Date(year, month, date);
      const dateStr = currentDate.toISOString().split('T')[0];

      // Find workout for this date
      const workout = workouts.find(
        (w) => w.scheduled_date === dateStr
      );

      // Check if there's a run for this date
      const hasRun = runs.some((r) => r.date === dateStr);

      days.push({
        date: currentDate,
        isCurrentMonth: true,
        workout,
        hasRun,
      });
    }

    // Add next month's days to complete the last week
    const remainingDays = 7 - (days.length % 7);
    if (remainingDays < 7) {
      for (let date = 1; date <= remainingDays; date++) {
        const nextMonthDate = new Date(year, month + 1, date);
        days.push({
          date: nextMonthDate,
          isCurrentMonth: false,
          hasRun: false,
        });
      }
    }

    return days;
  };

  const months = generateMonths();

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  };

  const getWorkoutColorClass = (workout: Workout, hasRun: boolean) => {
    if (hasRun) {
      return 'bg-spring-500 text-white border-spring-600';
    }

    // Color by workout type
    const type = workout.workout_type.toLowerCase();
    if (type.includes('long')) {
      return 'bg-sky-200 text-sky-900 border-sky-300';
    } else if (type.includes('tempo') || type.includes('threshold')) {
      return 'bg-peach-200 text-peach-900 border-peach-300';
    } else if (type.includes('interval') || type.includes('speed')) {
      return 'bg-coral-200 text-coral-900 border-coral-300';
    } else if (type.includes('easy') || type.includes('recovery')) {
      return 'bg-spring-100 text-spring-800 border-spring-200';
    } else {
      return 'bg-sunshine-100 text-sunshine-900 border-sunshine-200';
    }
  };

  return (
    <div className="space-y-8">
      {months.map((monthDate) => {
        const calendarDays = generateCalendarDays(monthDate);

        return (
          <div key={monthDate.toISOString()} className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-spring-500 to-spring-600 px-6 py-4">
              <h3 className="text-2xl font-bold text-white">
                {formatDate(monthDate)}
              </h3>
            </div>

            <div className="p-4">
              {/* Weekday headers */}
              <div className="grid grid-cols-7 gap-2 mb-2">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
                  <div
                    key={day}
                    className="text-center text-sm font-semibold text-spring-700 py-2"
                  >
                    {day}
                  </div>
                ))}
              </div>

              {/* Calendar grid */}
              <div className="grid grid-cols-7 gap-2">
                {calendarDays.map((day, index) => {
                  const isToday =
                    day.date.toDateString() === new Date().toDateString();

                  return (
                    <div
                      key={index}
                      className={`
                        min-h-[100px] p-2 rounded-lg border-2
                        ${day.isCurrentMonth ? 'bg-spring-50' : 'bg-gray-50'}
                        ${isToday ? 'border-peach-400' : 'border-gray-200'}
                        transition-all duration-200
                      `}
                    >
                      <div
                        className={`
                          text-sm font-medium mb-1
                          ${day.isCurrentMonth ? 'text-gray-700' : 'text-gray-400'}
                          ${isToday ? 'text-peach-600 font-bold' : ''}
                        `}
                      >
                        {day.date.getDate()}
                      </div>

                      {day.workout && (
                        <button
                          onClick={() => onWorkoutClick(day.workout!)}
                          className={`
                            w-full text-left p-2 rounded border-2
                            transition-all duration-200
                            hover:scale-105 hover:shadow-md
                            ${getWorkoutColorClass(day.workout, day.hasRun)}
                          `}
                        >
                          <div className="text-xs font-semibold mb-1">
                            {day.workout.workout_type}
                          </div>
                          <div className="text-xs">
                            {day.workout.planned_distance} mi
                          </div>
                          {day.hasRun && (
                            <div className="text-xs mt-1 font-bold">
                              ✓ Completed
                            </div>
                          )}
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        );
      })}

      {/* Legend */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h4 className="text-lg font-semibold text-gray-800 mb-4">
          Workout Types
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-spring-500 border-2 border-spring-600"></div>
            <span className="text-sm">Completed</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-spring-100 border-2 border-spring-200"></div>
            <span className="text-sm">Easy/Recovery</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-sky-200 border-2 border-sky-300"></div>
            <span className="text-sm">Long Run</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-peach-200 border-2 border-peach-300"></div>
            <span className="text-sm">Tempo</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-coral-200 border-2 border-coral-300"></div>
            <span className="text-sm">Intervals</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-sunshine-100 border-2 border-sunshine-200"></div>
            <span className="text-sm">Other</span>
          </div>
        </div>
      </div>
    </div>
  );
}
