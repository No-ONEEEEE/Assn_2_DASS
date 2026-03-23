# Q1.3 White Box Test Cases Report (MoneyPoly)

## Objective

Design white-box test cases from internal code structure so they cover:
- all important branches (decision paths),
- key variable states that can affect program behavior,
- relevant edge cases (zero values, boundaries, unexpected actions).

## Scope

- Code modules covered:
  - `moneypoly/moneypoly/moneypoly/player.py`
  - `moneypoly/moneypoly/moneypoly/property.py`
  - `moneypoly/moneypoly/moneypoly/board.py`
  - `moneypoly/moneypoly/moneypoly/bank.py`
  - `moneypoly/moneypoly/moneypoly/cards.py`
  - `moneypoly/moneypoly/moneypoly/dice.py`
  - `moneypoly/moneypoly/moneypoly/game.py`
  - `moneypoly/moneypoly/moneypoly/ui.py`
- White-box test file:
  - `moneypoly/moneypoly/tests/test_white_box_q1_3.py`
- Evidence output:
  - `moneypoly/moneypoly/pytest_q1_1_3.txt`

## Test Suite Size

Total executed test cases: **167**

Execution result:
- **167 passed**
- **0 failed**

## Coverage Breakdown (Why these tests were needed)

1. Player state and movement logic (60 tests)
- Money add/deduct positive and negative paths
- Bankruptcy states (`balance < 0`, `= 0`, `> 0`)
- Movement with and without board wrap
- GO salary branch when crossing start
- Zero/negative move edge behavior
- Property add/remove and status string state markers

2. Property and group ownership logic (11 tests)
- Full-group ownership branch (`all` vs partial ownership)
- Rent branches: normal, doubled, mortgaged
- Mortgage/unmortgage edge paths
- Availability matrix from owner/mortgage states
- Owner-count aggregation

3. Board tile classification and purchase logic (39 tests)
- All special-tile mapping branches
- Property vs blank tile detection
- Purchasable branch matrix (unowned/owned/mortgaged/non-property)
- Owned/unowned partition consistency

4. Bank behavior and monetary edge cases (17 tests)
- Collection with positive, zero, and negative values
- Payout for non-positive values
- Insufficient-funds exception path
- Loan issue path and loan-stat aggregation

5. Card deck state-machine logic (9 tests)
- Draw cycling behavior
- Empty-deck branches
- cards_remaining boundary cycle checks
- Reshuffle state reset behavior

6. Game core decision paths (20 tests)
- buy_property boundary (`balance == price`)
- pay_rent branch cases (owner none, mortgaged, normal)
- mortgage/unmortgage branch flow
- trade success/failure branches
- bankruptcy elimination path
- winner selection path
- card action branches (`collect`, `pay`, `jail`, `jail_free`, `move_to`, `birthday`, `collect_from_all`)
- jail handling branches (card use, fine pay, mandatory release)
- turn-level branches and interactive menu dispatch

7. UI helper validation (11 tests)
- Currency formatter
- safe_int_input valid/invalid input paths
- confirm input normalization paths
- print helper emission checks

## Errors Found and Fixes (with required commit format)

### Error #1: GO salary not awarded when passing start square
- Root cause: salary logic only checked `position == 0`.
- Fix commit: `a545f03` — `Error #1: fix GO salary when passing start`

### Error #2: Property-group ownership accepted partial ownership
- Root cause: used `any(...)` instead of requiring all properties in group.
- Fix commit: `a78021a` — `Error #2: correct full-set ownership logic for property groups`

### Error #3: Exact-balance purchase was rejected
- Root cause: affordability check used `<=` rejection.
- Fix commit: `2cc419b` — `Error #3: allow buying property with exact available balance`

### Error #4: Rent was not credited to owner
- Root cause: transfer step to owner was missing in `pay_rent`.
- Fix commit: `5c09312` — `Error #4: transfer rent to owner when tenant pays`

### Error #5: Winner selection returned lowest net worth
- Root cause: used `min(...)` instead of `max(...)`.
- Fix commit: `d6a35d7` — `Error #5: choose winner by highest net worth`

### Error #6: CardDeck empty state crashed in cards_remaining
- Root cause: modulo by zero when deck is empty.
- Fix commit: `15766ab` — `Error #6: handle empty deck in cards_remaining`

### Error #7: Unmortgage could clear mortgage state before affordability validation
- Root cause: `unmortgage()` was called before checking player balance.
- Fix commit: `5ccaa98` — `Error #7: prevent unmortgage state loss on insufficient funds`

## Execution Command

```powershell
Set-Location moneypoly/moneypoly
$env:PYTHONPATH=(Get-Location).Path
python -m pytest tests/test_white_box_q1_3.py -q
```

## Conclusion

Section 1.3 now has a large white-box suite (167 cases) that covers major branches, key variable-state transitions, and relevant edge conditions across core MoneyPoly modules. All tests pass, and identified logic defects were corrected with traceable `Error #` commits.
