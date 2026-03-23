# Q1.3 White Box Test Cases Report (MoneyPoly)

## Objective

Design white-box test cases based on code structure to cover:
- all important branches (decision paths),
- key variable states affecting behavior,
- relevant edge cases.

Then explain why each test is needed, identify logic errors found, and document fixes with required commit format.

## Scope

- Code under test:
  - `moneypoly/moneypoly/moneypoly/player.py`
  - `moneypoly/moneypoly/moneypoly/property.py`
  - `moneypoly/moneypoly/moneypoly/game.py`
  - `moneypoly/moneypoly/moneypoly/dice.py`
- Test file:
  - `moneypoly/moneypoly/tests/test_white_box_q1_3.py`
- Test evidence:
  - `moneypoly/moneypoly/pytest_q1_1_3.txt`

## White-box Test Design

### T1: Dice upper-face boundary is reachable
- Test: `test_dice_roll_can_reach_six`
- Why needed:
  - Ensures dice simulation includes highest valid face value.
  - Covers edge value branch at upper boundary.
- Decision/State covered:
  - Random draw range includes max face.

### T2: GO salary when crossing board start
- Test: `test_player_move_awards_go_salary_when_passing_go`
- Why needed:
  - Movement logic has a branch for salary award; crossing without landing exactly on 0 must still pay salary.
- Decision/State covered:
  - `old_position`, new position wrap-around, salary increment path.

### T3: Full color group ownership requires all properties
- Test: `test_property_group_requires_all_properties_owned_by_same_player`
- Why needed:
  - Rent multiplier depends on complete group ownership.
  - Partial ownership must not trigger multiplier branch.
- Decision/State covered:
  - Group ownership aggregation over all properties.

### T4: Exact-balance property purchase boundary
- Test: `test_buy_property_allows_exact_balance_purchase`
- Why needed:
  - Boundary condition for purchase affordability (`balance == price`) is critical.
- Decision/State covered:
  - Affordability check true/false branch at equality edge.

### T5: Rent transfer updates both players
- Test: `test_pay_rent_transfers_amount_to_owner`
- Why needed:
  - Financial transfer path should debit tenant and credit owner.
- Decision/State covered:
  - Owner not null, rent calculation, two-balance state update.

### T6: Winner selection uses highest net worth
- Test: `test_find_winner_returns_highest_net_worth_player`
- Why needed:
  - End-game correctness depends on choosing maximum net worth.
- Decision/State covered:
  - Aggregate selection path across multiple players.

## Errors Found and Fixes

### Error #1: GO salary not awarded when passing start square
- Failing behavior:
  - Player moving from 39 to 1 did not receive GO salary.
- Root cause:
  - Salary logic checked only `position == 0`.
- Fix:
  - Detect wrap-around using old/new position and positive step.
- Commit:
  - `a545f03` - `Error #1: fix GO salary when passing start`

### Error #2: Property group ownership check used partial ownership
- Failing behavior:
  - Group ownership returned true when only one property in group matched owner.
- Root cause:
  - Used `any(...)` instead of all-properties check.
- Fix:
  - Require non-empty group and `all(p.owner == player ...)`.
- Commit:
  - `a78021a` - `Error #2: correct full-set ownership logic for property groups`

### Error #3: Exact-balance purchase was rejected
- Failing behavior:
  - Player with balance exactly equal to property price could not buy.
- Root cause:
  - Affordability branch used `<=` reject condition.
- Fix:
  - Changed check to `<` so equality is allowed.
- Commit:
  - `2cc419b` - `Error #3: allow buying property with exact available balance`

### Error #4: Rent was not credited to property owner
- Failing behavior:
  - Tenant balance decreased, owner balance unchanged.
- Root cause:
  - Missing owner credit operation in rent flow.
- Fix:
  - Added `prop.owner.add_money(rent)`.
- Commit:
  - `5c09312` - `Error #4: transfer rent to owner when tenant pays`

### Error #5: Winner selection returned lowest net worth player
- Failing behavior:
  - End-game winner chosen using minimum wealth.
- Root cause:
  - Used `min(...)` instead of `max(...)`.
- Fix:
  - Changed selection to `max(self.players, key=lambda p: p.net_worth())`.
- Commit:
  - `d6a35d7` - `Error #5: choose winner by highest net worth`

## Execution Summary

Run command:

```powershell
Set-Location moneypoly/moneypoly
$env:PYTHONPATH=(Get-Location).Path
python -m pytest tests/test_white_box_q1_3.py -q
```

Result:
- `6 passed`

## Branch and Push Status

- `part-1` merged into `main`.
- Section 1.3 work committed on branch `part-1.3` using required commit message format for fixes.

## Conclusion

The white-box suite now covers branch decisions, key state transitions, and boundary conditions for core game mechanics. Five real logic errors were identified and fixed through isolated commits, and all designed tests pass.
