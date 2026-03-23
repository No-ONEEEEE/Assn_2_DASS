"""Registration module for StreetRace Manager.

Maintains basic crew member records: id, name, and primary role.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class CrewMember:
    crew_id: int
    name: str
    role: str


_crew_by_id: Dict[int, CrewMember] = {}
_next_id: int = 1


def register_crew_member(name: str, role: str) -> CrewMember:
    """Register a new crew member and return the created record."""
    global _next_id
    crew = CrewMember(crew_id=_next_id, name=name, role=role)
    _crew_by_id[crew.crew_id] = crew
    _next_id += 1
    return crew


def get_crew_member(crew_id: int) -> Optional[CrewMember]:
    """Return a crew member by id, or None if not found."""
    return _crew_by_id.get(crew_id)


def list_crew() -> List[CrewMember]:
    """Return a list of all registered crew members."""
    return list(_crew_by_id.values())


def update_crew_role(crew_id: int, new_role: str) -> bool:
    """Update the stored role for a crew member.

    Returns True if the member exists and the role was updated, False otherwise.
    """
    member = _crew_by_id.get(crew_id)
    if member is None:
        return False
    member.role = new_role
    return True
