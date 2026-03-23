"""Crew Management module for StreetRace Manager.

Adds skills and availability on top of the basic registration data.
"""
from typing import Dict, List, Optional

from . import registration


# skill levels per crew member: crew_id -> {skill_name: level}
_skills: Dict[int, Dict[str, int]] = {}
# availability per crew member: crew_id -> bool
_availability: Dict[int, bool] = {}


def assign_role(crew_id: int, role: str) -> bool:
    """Assign or change the primary role of a crew member.

    Returns True on success, False if the crew member does not exist.
    """
    member = registration.get_crew_member(crew_id)
    if member is None:
        return False
    member.role = role
    return True


def set_skill(crew_id: int, skill_name: str, level: int) -> bool:
    """Set a skill level for the given crew member.

    Returns True on success, False if the crew member does not exist.
    """
    if registration.get_crew_member(crew_id) is None:
        return False
    person_skills = _skills.setdefault(crew_id, {})
    person_skills[skill_name] = level
    return True


def get_crew_role(crew_id: int) -> Optional[str]:
    """Return the current role for the crew member, or None if unknown."""
    member = registration.get_crew_member(crew_id)
    return member.role if member is not None else None


def get_crew_by_role(role: str) -> List[int]:
    """Return a list of crew ids who currently have the given role."""
    return [m.crew_id for m in registration.list_crew() if m.role == role]


def set_availability(crew_id: int, is_available: bool) -> bool:
    """Mark a crew member as available or unavailable for assignments."""
    if registration.get_crew_member(crew_id) is None:
        return False
    _availability[crew_id] = is_available
    return True


def is_crew_available(crew_id: int) -> bool:
    """Return True if the crew member is considered available.

    By default, crew are treated as available unless explicitly marked otherwise
    and they exist in the registration module.
    """
    if registration.get_crew_member(crew_id) is None:
        return False
    return _availability.get(crew_id, True)
