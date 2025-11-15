"""
Test fixtures package.

Exports all fixture factory functions for easy import in tests.
"""

from tests.fixtures.plans import (
    create_test_plan,
    create_active_plan,
    create_completed_plan,
    create_abandoned_plan,
    create_plans_multiple
)

from tests.fixtures.workouts import (
    create_test_workout,
    create_tempo_workout,
    create_long_run_workout,
    create_speed_workout,
    create_recovery_workout,
    create_workouts_for_plan
)

from tests.fixtures.runs import (
    create_test_run,
    create_runs_for_plan,
    create_slow_run,
    create_fast_run,
    create_strava_run,
    create_long_run,
    create_short_run,
    create_runs_with_workout
)

__all__ = [
    # Plan fixtures
    "create_test_plan",
    "create_active_plan",
    "create_completed_plan",
    "create_abandoned_plan",
    "create_plans_multiple",
    # Workout fixtures
    "create_test_workout",
    "create_tempo_workout",
    "create_long_run_workout",
    "create_speed_workout",
    "create_recovery_workout",
    "create_workouts_for_plan",
    # Run fixtures
    "create_test_run",
    "create_runs_for_plan",
    "create_slow_run",
    "create_fast_run",
    "create_strava_run",
    "create_long_run",
    "create_short_run",
    "create_runs_with_workout",
]
