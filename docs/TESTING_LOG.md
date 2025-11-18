# Plain English Testing Log

**Last Test Run:** Successfully passed on 2025-11-16
**Total Tests:** 135
**Status:** ✅ ALL PASSING

---

## Plans Tests

### Integration Tests (test_plans_endpoints.py)

1. **Test Plan Creation with Valid Data** - Verify that creating a training plan with valid name, description, and date range returns status 201 and includes the plan ID
2. **Test Plan Creation Missing Name** - Verify that attempting to create a plan without a name returns validation error status 422
3. **Test Plan Creation Missing Dates** - Verify that attempting to create a plan without start/end dates returns validation error status 422
4. **Test Plan Creation with Invalid Dates** - Verify that attempting to create a plan where end date is before start date returns error status 400
5. **Test Plan Creation with Same Start and End Dates** - Verify that attempting to create a plan with identical start and end dates returns error status 400
6. **Test Listing Plans When None Exist** - Verify that requesting all plans when database is empty returns empty list with status 200
7. **Test Listing Multiple Plans** - Verify that requesting all plans returns correct count of existing plans (3 plans created)
8. **Test Plan Pagination** - Verify that pagination parameters (skip/limit) correctly divide plan list into pages
9. **Test Plan Pagination with Invalid Parameters** - Verify that negative skip or zero limit values return validation error status 422
10. **Test Retrieving Single Plan by ID** - Verify that requesting a specific plan by valid ID returns that plan's data with status 200
11. **Test Retrieving Plan with Invalid ID** - Verify that requesting a non-existent plan ID returns not found error status 404
12. **Test Updating Plan Name** - Verify that updating a plan's name successfully changes the name and updates the updated_at timestamp
13. **Test Updating Plan Status** - Verify that changing a plan's status from DRAFT to ACTIVE successfully updates the status field
14. **Test Updating Plan with Invalid Status** - Verify that attempting to set an invalid status value returns error status 400 or 422
15. **Test Updating Plan with Invalid Date Range** - Verify that updating a plan with end date before start date returns error status 400
16. **Test Updating Non-Existent Plan** - Verify that attempting to update a plan that doesn't exist returns not found error status 404
17. **Test Deleting Plan** - Verify that deleting an existing plan returns status 204 and subsequent retrieval returns 404
18. **Test Plan Deletion Cascades to Workouts** - Verify that deleting a plan also deletes all associated workouts (cascade delete)
19. **Test Deleting Non-Existent Plan** - Verify that attempting to delete a non-existent plan ID returns not found error status 404
20. **Test Creating Plan with Extremely Long Name** - Verify that attempting to create a plan with name exceeding 255 characters returns validation error status 422

### Unit Tests (test_plan_service.py)

21. **Test Plan Date Validation Accepts Valid Dates** - Verify that plan service validates and accepts proper date ranges where end is after start
22. **Test Plan Date Validation Rejects Same Dates** - Verify that plan service raises ValidationError when start and end dates are identical
23. **Test Plan Date Validation Rejects Reversed Dates** - Verify that plan service raises ValidationError when end date is before start date
24. **Test Plan Service Creates Plan Successfully** - Verify that plan service creates plan with correct data and assigns ID and DRAFT status
25. **Test Plan Service Rejects Invalid Date Range** - Verify that plan service raises ValidationError when creating plan with invalid dates
26. **Test Plan Service Rejects Same Start and End Dates** - Verify that plan service raises ValidationError when creating plan with identical dates
27. **Test Plan Service Retrieves Existing Plan** - Verify that plan service successfully retrieves a plan by its ID
28. **Test Plan Service Handles Non-Existent Plan** - Verify that plan service raises NotFoundError when retrieving non-existent plan
29. **Test Plan Service Returns Empty List** - Verify that plan service returns empty list when no plans exist in database
30. **Test Plan Service Returns Multiple Plans** - Verify that plan service retrieves all plans when multiple exist (3 plans tested)
31. **Test Plan Service Pagination** - Verify that plan service correctly implements skip/limit pagination across multiple pages
32. **Test Plan Service Updates Plan Data** - Verify that plan service updates plan name and updates timestamp correctly
33. **Test Plan Service Updates Plan Status** - Verify that plan service changes plan status from DRAFT to ACTIVE successfully
34. **Test Plan Service Rejects Update to Non-Existent Plan** - Verify that plan service raises NotFoundError when updating non-existent plan
35. **Test Plan Service Deletes Plan** - Verify that plan service deletes existing plan and subsequent retrieval raises NotFoundError
36. **Test Plan Service Rejects Delete of Non-Existent Plan** - Verify that plan service raises NotFoundError when deleting non-existent plan
37. **Test Plan Duration Calculation** - Verify that plan model correctly calculates duration in days between start and end dates
38. **Test Plan Status Check for Active** - Verify that plan model's is_active() method returns True only for ACTIVE status
39. **Test Plan Status Check for Draft** - Verify that plan model's is_draft() method returns True only for DRAFT status
40. **Test Plan Status Check for Completed** - Verify that plan model's is_completed() method returns True only for COMPLETED status
41. **Test Plan Status Check for Abandoned** - Verify that plan model's is_abandoned() method returns True only for ABANDONED status

### Unit Tests (test_validators.py - Plan Section)

42. **Test Plan Date Validation with Valid Range** - Verify that plan model validates and accepts proper date range without raising exception
43. **Test Plan Date Validation with Same Dates** - Verify that plan model raises ValueError when start and end dates are identical
44. **Test Plan Date Validation with Reversed Dates** - Verify that plan model raises ValueError when end date is before start date
45. **Test Plan Duration Property** - Verify that plan model's duration_days property correctly calculates 7 days for one-week plan

---

## Runs Tests

### Integration Tests (test_runs_endpoints.py)

46. **Test Run Creation with Valid Data** - Verify that creating a run with valid distance, pace, date, and source returns status 201 with run ID
47. **Test Run Creation with Invalid Distance** - Verify that creating a run with distance over 100 miles returns validation error status 422
48. **Test Run Creation with Invalid Pace** - Verify that creating a run with impossibly fast pace (under 180 sec/mile) returns validation error status 422
49. **Test Run Creation Linked to Workout** - Verify that creating a run with valid workout_id successfully links the run to that workout
50. **Test Run Creation with Invalid Workout ID** - Verify that creating a run with non-existent workout_id returns error status 400 or 404
51. **Test Run Creation Outside Plan Date Range** - Verify that creating a run with date outside plan's date range is allowed (status 201) but logged
52. **Test Listing Runs for Specific Plan** - Verify that requesting all runs for a plan returns only that plan's runs (3 runs tested)
53. **Test Listing All Runs Across Plans** - Verify that requesting all runs returns runs from multiple plans (4 total from 2 plans)
54. **Test Retrieving Single Run by ID** - Verify that requesting a specific run by valid ID returns that run's data with status 200
55. **Test Retrieving Run with Invalid ID** - Verify that requesting a non-existent run ID returns not found error status 404
56. **Test Updating Run Distance** - Verify that updating a run's distance from 5.0 to 6.0 miles successfully changes the distance field
57. **Test Updating Non-Existent Run** - Verify that attempting to update a run that doesn't exist returns not found error status 404
58. **Test Deleting Run** - Verify that deleting an existing run returns status 204 and subsequent retrieval returns 404
59. **Test Deleting Non-Existent Run** - Verify that attempting to delete a non-existent run ID returns not found error status 404
60. **Test Run Creation Missing Required Fields** - Verify that creating a run with only distance but missing pace/date/source returns validation error status 422
61. **Test Run Creation with Invalid Plan ID** - Verify that creating a run for non-existent plan ID returns not found error status 404
62. **Test Creating Duplicate Runs** - Verify that creating two runs with identical data (distance, pace, date, workout) either allows duplicates (201) or rejects appropriately (400/409)

### Unit Tests (test_run_service.py)

63. **Test Run Service Creates Run Successfully** - Verify that run service creates run with correct distance, pace, and MANUAL source
64. **Test Run Service Creates Run Linked to Workout** - Verify that run service creates run with valid workout_id link
65. **Test Run Service Rejects Invalid Plan** - Verify that run service raises NotFoundError when creating run for non-existent plan
66. **Test Run Service Rejects Invalid Workout** - Verify that run service raises NotFoundError when creating run with non-existent workout_id
67. **Test Run Service Retrieves Existing Run** - Verify that run service successfully retrieves a run by its ID
68. **Test Run Service Handles Non-Existent Run** - Verify that run service raises NotFoundError when retrieving non-existent run
69. **Test Run Service Updates Run Data** - Verify that run service updates run distance from 5.0 to 6.0 miles successfully
70. **Test Run Service Deletes Run** - Verify that run service deletes existing run and subsequent retrieval raises NotFoundError
71. **Test Run Pace String Formatting** - Verify that run model formats pace of 600 sec/mile as "10:00/mile" string
72. **Test Run Total Time Calculation** - Verify that run model calculates total time correctly (5 miles at 10 min/mile = 50 minutes)
73. **Test Run Source Detection for Manual** - Verify that run model's is_manual() returns True for MANUAL source and is_from_strava() returns False

### Unit Tests (test_validators.py - Run Section)

74. **Test Run Pace String Formatting** - Verify that run model formats pace of 600 sec/mile as "10:00/mile" in pace_str property
75. **Test Run Pace String with Seconds** - Verify that run model formats pace of 625 sec/mile as "10:25/mile" including seconds
76. **Test Run Total Time Minutes Calculation** - Verify that run model calculates 50 minutes for 5 miles at 10:00/mile pace
77. **Test Run Within Target Pace with No Target** - Verify that run is considered within target when workout has no target pace set
78. **Test Run Within Target Pace Range** - Verify that run with pace of 10:30 is within target range of 10:00-11:00 per mile
79. **Test Run Outside Target Pace Range** - Verify that run with pace of 8:20 (500 sec) is outside target range of 10:00-11:00 per mile
80. **Test Run Within Distance Tolerance** - Verify that run of 9.5 miles is within 10% tolerance of planned 10.0 miles
81. **Test Run Outside Distance Tolerance** - Verify that run of 8.5 miles is outside 10% tolerance of planned 10.0 miles
82. **Test Run Matches Workout Criteria** - Verify that run matching both distance and pace criteria returns True for matches_workout()

---

## Workouts Tests

### Integration Tests (test_workouts_endpoints.py)

83. **Test Workout Creation with Valid Data** - Verify that creating a workout with valid name, type, distance, and pace range returns status 201 with workout ID
84. **Test Workout Creation Missing Required Fields** - Verify that creating a workout with only name but missing type/distance returns validation error status 422
85. **Test Workout Creation with Invalid Plan ID** - Verify that creating a workout for non-existent plan ID returns not found error status 404
86. **Test Workout Creation with Invalid Pace Range** - Verify that creating a workout where min pace is slower than max pace returns validation error status 422
87. **Test Listing Workouts for Specific Plan** - Verify that requesting all workouts for a plan returns only that plan's workouts (3 workouts tested)
88. **Test Listing Workouts with Invalid Plan ID** - Verify that requesting workouts for non-existent plan ID returns not found error status 404
89. **Test Retrieving Single Workout by ID** - Verify that requesting a specific workout by valid ID returns that workout's data with status 200
90. **Test Retrieving Workout with Invalid ID** - Verify that requesting a non-existent workout ID returns not found error status 404
91. **Test Updating Workout Distance** - Verify that updating a workout's planned distance from 5.0 to 6.0 miles successfully changes the distance field
92. **Test Updating Non-Existent Workout** - Verify that attempting to update a workout that doesn't exist returns not found error status 404
93. **Test Deleting Workout** - Verify that deleting an existing workout returns status 204 and subsequent retrieval returns 404
94. **Test Deleting Non-Existent Workout** - Verify that attempting to delete a non-existent workout ID returns not found error status 404
95. **Test Creating All Workout Types** - Verify that creating workouts of all 7 valid types (EASY, TEMPO, LONG, SPEED, RECOVERY, CROSS_TRAINING, REST) succeeds
96. **Test Creating Workout with Impossibly Fast Pace** - Verify that creating a workout with pace below 180 sec/km minimum returns validation error status 422
97. **Test Creating Workout with Impossibly Slow Pace** - Verify that creating a workout with pace above 3000 sec/km maximum returns validation error status 422

### Unit Tests (test_workout_service.py)

98. **Test Workout Service Creates Workout Successfully** - Verify that workout service creates workout with correct name, type, and distance
99. **Test Workout Service Rejects Invalid Plan** - Verify that workout service raises NotFoundError when creating workout for non-existent plan
100. **Test Workout Service Creates All Workout Types** - Verify that workout service successfully creates workouts for all 5 basic types (EASY, TEMPO, LONG, SPEED, RECOVERY)
101. **Test Workout Service Retrieves Existing Workout** - Verify that workout service successfully retrieves a workout by plan_id and workout_id
102. **Test Workout Service Handles Non-Existent Workout** - Verify that workout service raises NotFoundError when retrieving non-existent workout
103. **Test Workout Service Lists Workouts for Plan** - Verify that workout service retrieves all workouts for a plan (3 workouts tested)
104. **Test Workout Service Updates Workout Data** - Verify that workout service updates workout distance from 5.0 to 6.0 miles successfully
105. **Test Workout Service Deletes Workout** - Verify that workout service deletes existing workout and subsequent retrieval raises NotFoundError
106. **Test Workout Pace Range String Formatting** - Verify that workout model formats pace range as "10:00-11:00/mile" string
107. **Test Workout Has Target Pace Detection** - Verify that workout model's has_target_pace() returns True when paces are set, False when None
108. **Test Workout Rest Day Detection** - Verify that workout model's is_rest_day() returns True only for REST type workouts

### Unit Tests (test_validators.py - Workout Section)

109. **Test Workout Pace Validation with Valid Range** - Verify that workout model validates and accepts proper pace range where min <= max
110. **Test Workout Pace Validation with Invalid Range** - Verify that workout model raises ValueError when min pace is slower than max pace
111. **Test Workout Pace Validation with Both None** - Verify that workout model accepts both pace values as None (no target pace)
112. **Test Workout Pace Validation with Only One Set** - Verify that workout model raises ValueError when only one pace value is set
113. **Test Workout Distance Validation with Valid Value** - Verify that workout model validates and accepts positive distance values
114. **Test Workout Distance Validation with Invalid Value** - Verify that workout model raises ValueError for zero or negative distance
115. **Test Workout Pace Range String Formatting** - Verify that workout model formats pace range of 600-660 sec as "10:00-11:00/mile"
116. **Test Workout Pace Range String with Seconds** - Verify that workout model formats pace range of 625-685 sec as "10:25-11:25/mile"
117. **Test Workout Pace Range String When None** - Verify that workout model returns None for pace_range_str when no target pace is set

---

## Analytics Tests

### Integration Tests (test_analytics_endpoints.py)

118. **Test Plan Progress with No Runs** - Verify that plan progress endpoint returns 0% adherence when plan has workouts but no completed runs
119. **Test Plan Progress with Some Runs** - Verify that plan progress endpoint calculates ~66.67% adherence when 2 of 3 workouts are completed
120. **Test Plan Progress with All Runs Completed** - Verify that plan progress endpoint returns 100% adherence when all workouts have completed runs
121. **Test Plan Progress with Invalid Plan ID** - Verify that requesting progress for non-existent plan ID returns not found error status 404
122. **Test Weekly Summary for Specific Week** - Verify that weekly summary endpoint returns correct week number and positive distance for week with runs
123. **Test Weekly Summary Mileage Calculation** - Verify that weekly summary correctly sums mileage (10 + 8 + 12 = 30 miles) for week 1 runs
124. **Test Weekly Summary with Invalid Plan ID** - Verify that requesting weekly summary for non-existent plan ID returns not found error status 404
125. **Test Weekly Summary with Invalid Week Number** - Verify that requesting weekly summary for week 100 (beyond plan duration) returns error status 400
126. **Test Weekly Summary Without Week Parameter** - Verify that weekly summary endpoint handles missing week_number parameter (returns 200, 400, or 422)
127. **Test Plan Progress Ignores Unlinked Runs** - Verify that plan progress calculation excludes runs that are not linked to any workout
128. **Test Weekly Summary for Empty Week** - Verify that weekly summary returns 0.0 miles for a week with no runs logged
129. **Test Weekly Summary Across Multiple Weeks** - Verify that weekly summary correctly separates runs by week (week 1: 10 miles, week 2: 15 miles)

### Unit Tests (test_analytics_service.py)

130. **Test Analytics Service Plan Progress with No Runs** - Verify that analytics service calculates 0% adherence for plan with 3 workouts and no runs
131. **Test Analytics Service Plan Progress with Some Runs** - Verify that analytics service calculates ~66.67% adherence when 2 of 3 workouts are completed
132. **Test Analytics Service Plan Progress with All Runs** - Verify that analytics service calculates 100% adherence when all 3 workouts have runs
133. **Test Analytics Service Weekly Summary** - Verify that analytics service returns correct week number and positive distance for week with runs
134. **Test Analytics Service Weekly Mileage Calculation** - Verify that analytics service correctly sums 30 miles (10 + 8 + 12) for week 1 runs
135. **Test Analytics Service Handles Invalid Plan** - Verify that analytics service raises NotFoundError when calculating progress for non-existent plan

---

## Test Statistics by Area

- **Plans Tests:** 45 tests
  - Integration: 20 tests
  - Unit (Service): 21 tests
  - Unit (Validators): 4 tests

- **Runs Tests:** 37 tests
  - Integration: 17 tests
  - Unit (Service): 11 tests
  - Unit (Validators): 9 tests

- **Workouts Tests:** 35 tests
  - Integration: 15 tests
  - Unit (Service): 11 tests
  - Unit (Validators): 9 tests

- **Analytics Tests:** 18 tests
  - Integration: 12 tests
  - Unit (Service): 6 tests

**Grand Total:** 135 tests across all areas

---

## Edge Cases Covered

✅ **Run Logged Outside Plan Dates** (Test #51) - System allows but logs runs outside plan date range
✅ **Super Long Plan Name** (Test #20) - Plan names exceeding 255 characters are rejected
✅ **Impossible Pace Range** (Tests #96, #97) - Paces faster than 180 sec/km or slower than 3000 sec/km are rejected
✅ **Duplicate Runs** (Test #62) - System handles duplicate run entries appropriately

---

## Test Execution Notes

To run all tests:
```bash
docker-compose exec api pytest
```

To run tests for a specific area:
```bash
docker-compose exec api pytest tests/integration/test_plans_endpoints.py
docker-compose exec api pytest tests/integration/test_runs_endpoints.py
docker-compose exec api pytest tests/integration/test_workouts_endpoints.py
docker-compose exec api pytest tests/integration/test_analytics_endpoints.py
```

To run tests with verbose output:
```bash
docker-compose exec api pytest -v
```

---

## Change Log

### 2025-11-16
- ✅ Added test for extremely long plan names (>255 characters)
- ✅ Added test for impossible workout pace ranges (too fast)
- ✅ Added test for impossible workout pace ranges (too slow)
- ✅ Added test for duplicate run entries
- ✅ All 135 tests passing
- ✅ Created comprehensive testing documentation

---

_This document is maintained as a plain-English reference for all tests in the running tracker application. Update the "Last Test Run" date and status at the top of this file each time tests are executed._
