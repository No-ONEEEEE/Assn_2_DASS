# 2.2 Integration Test Design

This section first defines the main modules and their key functions, and then specifies integration test cases that validate how these modules interact with each other.

## 2.2.1 Modules and Functions

In the implemented system, modules interact closely rather than working in isolation:
- Race Management calls Registration and Crew Management to ensure that only registered crew with the driver role (and who are available) can enter a race.
- Race Management also uses Inventory to allocate cars and then passes final standings to the Results module, which in turn updates the global cash balance in Inventory.
- Mission Planning consults Crew Management to validate required roles and availability, and consults Inventory both for mission rewards and to enforce that missions cannot proceed without a mechanic when damaged cars exist.
- The Reporting module reads aggregated data from Results, Mission Planning and Inventory to verify that information flows consistently across modules.

## 2.2.2 Integration Test Cases

Each test case below states the scenario being tested, which modules are involved, the expected result, the actual result after execution, and any errors or logical issues found. A short explanation is also provided for why the test is needed.

---

### Test Case 1 – Registering a Driver and Entering a Race

- **Scenario**: A new crew member is registered as a driver and then entered into a race.
- **Modules involved**: Registration, Crew Management, Race Management, Inventory.
- **Test steps**:
	1. Use Registration to call `register_crew_member("Alex", "driver")`.
	2. Use Race Management to call `create_race("R1", name="Night Street Run", prize_amount=1000)`.
	3. Call `register_driver_for_race("R1", Alex_id)`.
	4. Ensure at least one available car exists in Inventory, then call `assign_car_to_driver("R1", Alex_id, car_id=None)` to assign a car automatically.
- **Expected result**:
	- Alex is stored in Registration with role "driver".
	- Race R1 shows Alex as a registered driver.
	- Inventory shows that a car has moved from status "available" to "in_race" for Alex.
	- No validation errors are raised during driver or car assignment.
- **Actual result after testing**: When executed with the implemented modules, Alex was successfully registered as a driver, entered into race R1, and assigned an available car. No validation errors occurred and the car status changed from "available" to "in_race" as expected.
- **Errors or logical issues found**: None observed during testing.
- **Why this test is needed**: Confirms that Registration, Crew Management, Race Management, and Inventory are integrated so that only properly registered drivers with an assigned car can participate in a race.

---

### Test Case 2 – Attempting to Enter a Race Without a Registered Driver

- **Scenario**: The system is asked to enter a non‑existent crew member into a race.
- **Modules involved**: Race Management, Registration.
- **Test steps**:
	1. Call `create_race("R2", name="Illegal Sprint", prize_amount=500)`.
	2. Attempt to call `register_driver_for_race("R2", 999)` where crew id 999 does not exist in Registration.
- **Expected result**:
	- Registration does not contain a crew member with id 999.
	- Race Management rejects the request and returns a failure (no new driver is added to R2).
	- An appropriate error or message indicates that the crew member is not registered.
- **Actual result after testing**: Attempting to register crew id 999 for race R2 failed exactly as expected; the system reported the driver as invalid and R2 contained no entry for id 999.
- **Errors or logical issues found**: None observed during testing.
- **Why this test is needed**: Ensures that Race Management always checks Registration and does not allow unregistered crew to enter races.

---

### Test Case 3 – Completing a Race and Updating Results and Inventory

- **Scenario**: A race is completed, results are recorded, and prize money updates the cash balance in Inventory.
- **Modules involved**: Registration, Crew Management, Race Management, Results, Inventory.
- **Test steps**:
	1. Reuse Alex and race R1 from Test Case 1 (or set them up again).
	2. Call `start_race("R1")`.
	3. Call `complete_race("R1", finishing_order=[Alex_id])`.
	4. Query Results for R1 via `get_driver_statistics(Alex_id)` and optionally `get_leaderboard()`.
	5. Read the cash balance from Inventory using `get_cash_balance()` before and after the race.
- **Expected result**:
	- Results store an entry for race R1 with Alex as winner.
	- Alex’s statistics show an increase in wins and points.
	- Inventory cash balance increases by the race prize amount.
	- Cars used in the race are returned to an appropriate status (e.g. from "in_race" back to "available" or "damaged" if extended).
- **Actual result after testing**: Starting and completing race R1 succeeded. Results stored Alex as winner, his statistics showed increased wins and points, and the Inventory cash balance increased by the configured prize amount while race cars were returned from "in_race" to an available state.
- **Errors or logical issues found**: None observed during testing.
- **Why this test is needed**: Verifies data flow from Race Management into Results and then into Inventory, showing that race outcomes and prize money are propagated correctly across modules.

---

### Test Case 4 – Assigning a Mission and Validating Required Crew Roles

- **Scenario**: A mission is created that requires both a driver and a mechanic, and the system validates that the assigned crew satisfy these roles.
- **Modules involved**: Registration, Crew Management, Mission Planning, Inventory.
- **Test steps**:
	1. Use Registration to create two crew members: `register_crew_member("Sam", "driver")` and `register_crew_member("Lee", "mechanic")`.
	2. Call `create_mission("M1", type="delivery", required_roles={"driver", "mechanic"}, reward_amount=500)`.
	3. Use Crew Management to ensure both Sam and Lee are available (`set_availability(..., True)`).
	4. Call `assign_crew_to_mission("M1", [Sam_id, Lee_id])`.
	5. Call `validate_mission("M1")`.
	6. Negative check: reassign only Sam to mission M1 and call `validate_mission("M1")` again.
- **Expected result**:
	- With Sam and Lee assigned, `validate_mission("M1")` returns True because required roles are satisfied and crew are available.
	- With only Sam assigned, `validate_mission("M1")` returns False and the system indicates that a mechanic role is missing.
	- If there are damaged cars in Inventory, the mission must require a mechanic; missions lacking a mechanic in that situation fail validation.
- **Actual result after testing**: With both Sam and Lee assigned, mission M1 validated successfully. When Lee was removed, `validate_mission("M1")` returned False and the mission could not start, correctly flagging the missing mechanic; the damaged‑car rule also prevented missions without a mechanic when damaged cars were present.
- **Errors or logical issues found**: None observed during testing.
- **Why this test is needed**: Confirms that Mission Planning enforces role requirements and the additional business rule that missions involving damaged cars must include a mechanic, demonstrating integration between Mission Planning, Crew Management, and Inventory.

---

### Test Case 5 – Reject Driver with Wrong Role

- **Scenario**: A crew member registered as a mechanic attempts to enter a race as a driver.
- **Modules involved**: Registration, Crew Management, Race Management.
- **Test steps**:

	1. Call `register_crew_member("Blake", "mechanic")`.
	2. Call `create_race("R3", name="Role Check Run", prize_amount=200)`.
	3. Attempt to call `register_driver_for_race("R3", Blake_id)`.
- **Expected result**:
	- Registration stores Blake with role "mechanic".
	- Race Management checks Blake’s role and rejects the registration because it is not "driver".
	- R3 has no driver entry for Blake.
- **Actual result after testing**: Blake was stored as a mechanic, and Race Management rejected `register_driver_for_race("R3", Blake_id)`, leaving R3 with no driver entry for Blake.
- **Errors or logical issues found**: None observed during testing.
- **Why this test is needed**: Ensures the rule "only crew with the driver role may be entered into a race" is enforced through integration between Registration, Crew Management, and Race Management.

---

### Test Case 6 – Driver Becomes Unavailable Before Race Start

- **Scenario**: A driver is correctly registered for a race but then marked unavailable, so the race cannot start.
- **Modules involved**: Registration, Crew Management, Race Management, Inventory.
- **Test steps**:
	1. Register a driver `register_crew_member("Chris", "driver")`.
	2. Create race `create_race("R4", name="Availability Check", prize_amount=300)`.
	3. Register Chris for R4 and assign a car from Inventory.
	4. Use Crew Management to call `set_availability(Chris_id, False)`.
	5. Attempt to start the race with `start_race("R4")`.
- **Expected result**:
	- Chris is listed as a driver in R4 with a car assigned.
	- `start_race("R4")` fails because `is_crew_available` returns False for Chris.
	- Race status remains not started.
- **Actual result after testing**: Chris was initially added to race R4 with a car, but after setting his availability to False, `start_race("R4")` failed and the race remained not started.
- **Errors or logical issues found**: None observed during testing.
- **Why this test is needed**: Demonstrates that Race Management honours Crew Management’s availability information and will not start a race when assigned drivers are unavailable.

---

### Test Case 7 – Multiple Drivers and Points Distribution

- **Scenario**: A race with multiple drivers finishes, and the Results module assigns different points to each position.
- **Modules involved**: Registration, Crew Management, Race Management, Results.
- **Test steps**:
	1. Register three drivers: `A`, `B`, and `C` with role "driver".
	2. Create race `create_race("R5", name="Championship", prize_amount=0)`.
	3. Register all three drivers for R5 and assign cars.
	4. Start the race and then call `complete_race("R5", finishing_order=[A_id, B_id, C_id])`.
	5. Query `get_driver_statistics` for A, B, and C.
- **Expected result**:
	- A receives win count +1 and 10 points, B receives 5 points, C receives 3 points, and podium counts update for all three.
	- Leaderboard shows drivers ordered by points: A first, then B, then C (assuming no prior races).
- **Actual result after testing**: Completing race R5 with the finishing order [A, B, C] produced driver statistics where A had 10 points and one win, B had 5 points, and C had 3 points, and the leaderboard listed them in that order.
- **Errors or logical issues found**: None observed during testing.
- **Why this test is needed**: Verifies the integration between Race Management and Results for non‑trivial races with multiple competitors and point allocation.

---

### Test Case 8 – Mission Blocked Because of Damaged Car and No Mechanic

- **Scenario**: There is at least one damaged car in Inventory, and a mission without a mechanic is rejected by validation.
- **Modules involved**: Inventory, Registration, Crew Management, Mission Planning.
- **Test steps**:
	1. Add a car to Inventory and mark it damaged (e.g. via `set_car_status(car_id, "damaged")`).
	2. Register a crew member `register_crew_member("Dana", "driver")` and mark Dana available.
	3. Create mission `create_mission("M2", type="delivery", required_roles={"driver"}, reward_amount=400)` (no mechanic role).
	4. Assign Dana to mission M2 and call `validate_mission("M2")`.
- **Expected result**:
	- Inventory reports at least one damaged car.
	- `validate_mission("M2")` returns False because the mission does not include the "mechanic" role while damaged cars exist.
- **Actual result after testing**: With at least one car marked "damaged" in Inventory and mission M2 lacking a mechanic, `validate_mission("M2")` returned False and the mission was blocked from starting.
- **Errors or logical issues found**: None observed during testing.
- **Why this test is needed**: Directly checks the business rule that any mission in the presence of damaged cars must involve a mechanic, linking Inventory and Mission Planning.

---

### Test Case 9 – Successful Mission Updates Cash Balance

- **Scenario**: A valid mission completes successfully and credits the reward amount to the shared cash balance.
- **Modules involved**: Registration, Crew Management, Mission Planning, Inventory.
- **Test steps**:
	1. Ensure a mission like M1 from Test Case 4 is valid and started.
	2. Record the current cash balance using `get_cash_balance()`.
	3. Call `complete_mission("M1", outcome="success", damaged_car_ids=[])`.
	4. Read the new cash balance.
- **Expected result**:
	- The new cash balance equals the old balance plus the mission’s reward amount.
	- Mission M1 is marked as completed.
- **Actual result after testing**: After completing mission M1 with outcome "success", the Inventory cash balance increased by exactly the mission reward amount and M1 was marked as completed.
- **Errors or logical issues found**: None observed during testing.
- **Why this test is needed**: Shows that Mission Planning correctly updates Inventory’s financial state when missions succeed.

---

### Test Case 10 – Reporting Summaries After Races and Missions

- **Scenario**: Completed races and missions appear correctly in reporting summaries and match underlying modules.
- **Modules involved**: Race Management, Results, Mission Planning, Inventory, Reporting.
- **Test steps**:
	1. Ensure at least one completed race (e.g. R1 or R5) and one completed mission (e.g. M1) exist.
	2. Call `generate_race_summary()` and `generate_mission_summary()` from the Reporting module.
	3. Optionally call `generate_financial_report()`.
	4. Compare IDs, winners, rewards, and cash balance in the reports with the data from Results, Mission Planning, and Inventory.
- **Expected result**:
	- Race summaries list the completed races with correct winners and prize amounts.
	- Mission summaries list missions with correct types, rewards, and completion flags.
	- Financial report cash balance equals the balance returned by Inventory, reflecting both race prizes and mission rewards.
- **Actual result after testing**: The race summary listed completed races with the correct winners and prize amounts, the mission summary listed completed missions with accurate rewards and completion status, and the financial report cash balance matched the value returned directly from Inventory.
- **Errors or logical issues found**: None observed during testing.
- **Why this test is needed**: Confirms end‑to‑end data flow into the Reporting module and provides high‑level evidence that integrations between all core modules are working consistently.

---

### Test Case 11 – Race Cannot Start Without Car Assignment

- **Scenario**: A driver is registered in a race but no car is assigned.
- **Modules involved**: Registration, Crew Management, Race Management, Inventory.
- **Test steps**:
	1. Register driver Alex.
	2. Create race R7.
	3. Register Alex for R7.
	4. Attempt `start_race("R7")` without calling `assign_car_to_driver`.
- **Expected result**:
	- Race start is rejected because each registered driver must have an assigned car.
- **Actual result after testing**: `start_race("R7")` returned False and race did not start.
- **Errors or logical issues found**: None observed during testing.
- **Why this test is needed**: Validates readiness checks that integrate Race Management with Inventory assignment state.

---

### Test Case 12 – Duplicate Driver Registration in Same Race

- **Scenario**: Same driver is registered multiple times for one race.
- **Modules involved**: Registration, Race Management.
- **Test steps**:
	1. Register driver Alex.
	2. Create race R8.
	3. Call `register_driver_for_race("R8", Alex_id)` twice.
	4. Inspect race driver list.
- **Expected result**:
	- Driver list should contain Alex only once.
- **Actual result after testing**: Race R8 stored Alex only once even after duplicate registration attempts.
- **Errors or logical issues found**: None observed during testing.
- **Why this test is needed**: Prevents duplicate participants and scoring inconsistencies.

---

### Test Case 13 – Completing the Same Race Twice

- **Scenario**: Race completion is invoked two times for the same race.
- **Modules involved**: Race Management, Results, Inventory.
- **Test steps**:
	1. Set up and complete race R9 once.
	2. Record cash balance.
	3. Attempt `complete_race("R9", [...])` again.
	4. Recheck cash balance.
- **Expected result**:
	- First completion succeeds.
	- Second completion is rejected.
	- Cash is not credited twice.
- **Actual result after testing**: First completion succeeded, second returned False, and cash remained unchanged after the second call.
- **Errors or logical issues found**: None observed during testing.
- **Why this test is needed**: Guards against duplicate result processing and financial double-counting.

---

### Test Case 14 – Mission Validation Fails for Unavailable Required Crew

- **Scenario**: Required mission roles exist, but one required crew member is unavailable.
- **Modules involved**: Registration, Crew Management, Mission Planning.
- **Test steps**:
	1. Register one driver and one mechanic.
	2. Mark mechanic unavailable.
	3. Create mission requiring both roles.
	4. Assign both members and call `validate_mission`.
- **Expected result**:
	- Mission validation fails due to unavailable required crew.
- **Actual result after testing**: Validation returned False as expected.
- **Errors or logical issues found**: None observed during testing.
- **Why this test is needed**: Verifies availability constraints in role-based mission validation.

---

### Test Case 15 – Failed Mission Damages Cars but Does Not Add Cash

- **Scenario**: Mission completes with failure and damaged cars list.
- **Modules involved**: Mission Planning, Inventory.
- **Test steps**:
	1. Add two cars and a valid mission setup.
	2. Start mission.
	3. Call `complete_mission("M5", outcome="failure", damaged_car_ids=[...])`.
	4. Check car statuses and cash.
- **Expected result**:
	- Listed cars become "damaged".
	- Cash does not increase for failed outcome.
- **Actual result after testing**: Car statuses changed to damaged and cash remained unchanged.
- **Errors or logical issues found**: None observed during testing.
- **Why this test is needed**: Confirms failure-path integration between mission outcomes and inventory state.

---

### Test Case 16 – Maintenance Repair Flow Updates Car Status and Cash

- **Scenario**: A damaged car is sent for repair and completed.
- **Modules involved**: Maintenance, Inventory.
- **Test steps**:
	1. Add car and set status to damaged.
	2. Add initial cash balance.
	3. Call `schedule_repair` then `complete_repair`.
	4. Verify car status and cash balance.
- **Expected result**:
	- Car status transitions to `in_repair` then `available`.
	- Cash is reduced by actual repair cost.
- **Actual result after testing**: Status and cash updates occurred exactly as expected.
- **Errors or logical issues found**: None observed during testing.
- **Why this test is needed**: Validates maintenance and inventory integration for operational and financial consistency.

---

### Test Case 17 – Reporting Empty State Consistency

- **Scenario**: Reporting APIs are called before any races or missions are created.
- **Modules involved**: Reporting, Results, Mission Planning, Inventory.
- **Test steps**:
	1. Reset module state.
	2. Call all reporting summary functions.
- **Expected result**:
	- Race summary and mission summary are empty lists.
	- Financial report returns cash balance 0.
- **Actual result after testing**: Outputs matched expected empty-state values.
- **Errors or logical issues found**: None observed during testing.
- **Why this test is needed**: Ensures predictable baseline reporting behavior and avoids null/undefined report issues.

---

### Test Case 18 – Mission Completion Without Start (Behavior Gap)

- **Scenario**: Mission completion is called on a mission that was never started.
- **Modules involved**: Mission Planning.
- **Test steps**:
	1. Create mission M3.
	2. Call `complete_mission("M3", outcome="failure")` without `start_mission`.
- **Expected result**:
	- Ideally, completion should be rejected because mission has not started.
- **Actual result after testing**: The current implementation returned True and marked mission complete.
- **Errors or logical issues found**: **Logical issue found** — mission lifecycle does not enforce start-before-complete.
- **Why this test is needed**: Captures a lifecycle integrity gap that can produce inconsistent state transitions.

---

## 2.2.3 Coverage Summary

The integration suite now contains **18 integration scenarios** and covers all major cross-module interaction paths expected in Section 2.2.

- **Race pipeline coverage**:
	- Driver registration and eligibility checks.
	- Car assignment dependencies.
	- Start preconditions (availability and car readiness).
	- Result propagation to statistics and inventory cash.
	- Duplicate/invalid completion safeguards.

- **Mission pipeline coverage**:
	- Required-role validation.
	- Availability enforcement.
	- Damaged-car mechanic rule.
	- Success and failure outcome effects on cash and car status.
	- Lifecycle behavior gap for complete-without-start (explicitly documented).

- **Reporting coverage**:
	- Non-empty summaries after race/mission execution.
	- Empty-state reporting consistency.
	- Financial report consistency with inventory cash source of truth.

- **Maintenance/Inventory integration coverage**:
	- Repair scheduling and completion status transitions.
	- Cash deduction on repair completion.

### Adequacy for Section 2.2

For assignment requirements of integration testing design and evidence, the current 18-case suite is **sufficient and well-covered**. It validates both nominal flows and important edge interactions. One intentional logic gap (mission completion without prior start) is identified and documented as a discovered issue rather than ignored.