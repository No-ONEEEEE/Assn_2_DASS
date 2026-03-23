"""Mission Planning module for StreetRace Manager.

Creates missions, assigns crew, validates required roles, and completes missions.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Set

from . import crew_management, inventory


@dataclass
class Mission:
    mission_id: str
    mission_type: str
    required_roles: Set[str]
    reward_amount: int
    assigned_crew: List[int] = field(default_factory=list)
    started: bool = False
    completed: bool = False


_missions: Dict[str, Mission] = {}


def create_mission(mission_id: str, mission_type: str, required_roles: Set[str], reward_amount: int) -> Mission:
    """Create a new mission definition."""
    mission = Mission(
        mission_id=mission_id,
        mission_type=mission_type,
        required_roles=set(required_roles),
        reward_amount=reward_amount,
    )
    _missions[mission_id] = mission
    return mission


def get_all_missions() -> Dict[str, Mission]:
    """Return a shallow copy of all missions for reporting and inspection."""
    return dict(_missions)


def assign_crew_to_mission(mission_id: str, crew_ids: List[int]) -> bool:
    """Assign a list of crew ids to the mission.

    Returns True on success, False if the mission does not exist.
    """
    mission = _missions.get(mission_id)
    if mission is None:
        return False
    mission.assigned_crew = list(crew_ids)
    return True


def validate_mission(mission_id: str) -> bool:
    """Check that required roles are covered and crew are available.

    Returns True if the mission can proceed.
    """
    mission = _missions.get(mission_id)
    if mission is None:
        return False

    if not mission.assigned_crew:
        return False

    # Business rule: if there is any damaged car in the inventory, then any
    # mission must explicitly require a mechanic role before it can proceed.
    if inventory.has_damaged_car() and "mechanic" not in mission.required_roles:
        return False

    # Track which roles are satisfied by the current assignments
    satisfied_roles: Set[str] = set()

    for crew_id in mission.assigned_crew:
        role = crew_management.get_crew_role(crew_id)
        if role is None:
            continue
        if not crew_management.is_crew_available(crew_id):
            # unavailable crew means mission cannot start
            return False
        if role in mission.required_roles:
            satisfied_roles.add(role)

    return satisfied_roles == mission.required_roles


def start_mission(mission_id: str) -> bool:
    """Start a mission after validating requirements."""
    mission = _missions.get(mission_id)
    if mission is None or mission.started:
        return False
    if not validate_mission(mission_id):
        return False
    mission.started = True
    return True


def complete_mission(mission_id: str, outcome: str, damaged_car_ids: List[int] | None = None) -> bool:
    """Complete a mission and update inventory based on the outcome.

    If outcome is "success", the reward amount is added to cash.
    Any damaged cars are marked as damaged in the inventory.
    """
    mission = _missions.get(mission_id)
    if mission is None or mission.completed is True:
        return False

    if outcome == "success":
        inventory.add_cash(mission.reward_amount)

    for car_id in damaged_car_ids or []:
        inventory.set_car_status(car_id, "damaged")

    mission.completed = True
    return True
