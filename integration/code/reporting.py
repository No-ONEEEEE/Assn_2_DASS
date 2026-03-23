"""Reporting module for StreetRace Manager.

Provides high-level summaries built from other modules.
"""
from typing import Dict, Any, List

from . import inventory, mission_planning, race_management, results


def generate_race_summary() -> List[Dict[str, Any]]:
    """Return a simple summary list for reporting races.

    Each item may contain race id and winner id.
    """
    summary: List[Dict[str, Any]] = []
    # results module is the single source of truth for completed races
    for race_id, race_result in results.get_all_race_results().items():
        winner = race_result.finishing_order[0] if race_result.finishing_order else None
        summary.append({"race_id": race_id, "winner_id": winner, "prize": race_result.prize_amount})
    return summary


def generate_mission_summary() -> List[Dict[str, Any]]:
    """Return a list of missions with basic outcome data."""
    summary: List[Dict[str, Any]] = []
    for mission in mission_planning.get_all_missions().values():
        summary.append(
            {
                "mission_id": mission.mission_id,
                "type": mission.mission_type,
                "reward": mission.reward_amount,
                "started": mission.started,
                "completed": mission.completed,
            }
        )
    return summary


def generate_financial_report() -> Dict[str, Any]:
    """Return a very simple financial report based on the inventory cash balance."""
    return {"cash_balance": inventory.get_cash_balance()}
