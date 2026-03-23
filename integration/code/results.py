"""Results module for StreetRace Manager.

Stores race outcomes and maintains driver rankings.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from . import inventory


@dataclass
class RaceResult:
    race_id: str
    finishing_order: List[int]  # list of driver ids in order
    prize_amount: int


@dataclass
class DriverStats:
    driver_id: int
    wins: int = 0
    podiums: int = 0
    points: int = 0


_race_results: Dict[str, RaceResult] = {}
_driver_stats: Dict[int, DriverStats] = {}


def _ensure_driver(driver_id: int) -> DriverStats:
    stats = _driver_stats.get(driver_id)
    if stats is None:
        stats = DriverStats(driver_id=driver_id)
        _driver_stats[driver_id] = stats
    return stats


def record_race_result(race_id: str, finishing_order: List[int], prize_amount: int) -> None:
    """Record the result of a race and distribute prize money/points.

    Simple scoring scheme:
    - 1st place: 10 points and a win
    - 2nd place: 5 points
    - 3rd place: 3 points
    """
    result = RaceResult(race_id=race_id, finishing_order=list(finishing_order), prize_amount=prize_amount)
    _race_results[race_id] = result

    # distribute prize money to the global cash balance
    if prize_amount > 0:
        inventory.add_cash(prize_amount)

    for position, driver_id in enumerate(finishing_order, start=1):
        stats = _ensure_driver(driver_id)
        if position == 1:
            stats.wins += 1
            stats.points += 10
        elif position == 2:
            stats.points += 5
        elif position == 3:
            stats.points += 3

        if position <= 3:
            stats.podiums += 1


def update_driver_ranking(driver_id: int, points_delta: int) -> None:
    """Manually adjust ranking points for a driver."""
    stats = _ensure_driver(driver_id)
    stats.points = max(0, stats.points + points_delta)


def get_driver_statistics(driver_id: int) -> DriverStats:
    """Return statistics for the given driver (defaults to zeros)."""
    return _ensure_driver(driver_id)


def get_leaderboard() -> List[Tuple[int, int]]:
    """Return a leaderboard as a list of (driver_id, points) sorted by points."""
    return sorted(((s.driver_id, s.points) for s in _driver_stats.values()), key=lambda x: x[1], reverse=True)


def get_all_race_results() -> Dict[str, RaceResult]:
    """Return a shallow copy of all recorded race results.

    Provided for reporting so callers do not reach into module internals.
    """
    return dict(_race_results)
