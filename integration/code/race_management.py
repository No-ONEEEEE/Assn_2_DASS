"""Race Management module for StreetRace Manager.

Creates races, registers drivers and cars, and coordinates results.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from . import crew_management, inventory, registration, results


@dataclass
class Race:
    race_id: str
    name: str
    prize_amount: int
    drivers: List[int] = field(default_factory=list)
    cars_by_driver: Dict[int, int] = field(default_factory=dict)  # driver_id -> car_id
    started: bool = False
    completed: bool = False


_races: Dict[str, Race] = {}


def create_race(race_id: str, name: str, prize_amount: int) -> Race:
    """Create a new race and store it in memory."""
    race = Race(race_id=race_id, name=name, prize_amount=prize_amount)
    _races[race_id] = race
    return race


def register_driver_for_race(race_id: str, driver_id: int) -> bool:
    """Register a driver for a race if they exist and have role 'driver'."""
    race = _races.get(race_id)
    if race is None or race.started:
        return False

    member = registration.get_crew_member(driver_id)
    if member is None or member.role != "driver":
        # only registered drivers can enter races
        return False

    if not crew_management.is_crew_available(driver_id):
        # cannot add unavailable crew
        return False

    if driver_id not in race.drivers:
        race.drivers.append(driver_id)
    return True


def assign_car_to_driver(race_id: str, driver_id: int, car_id: Optional[int] = None) -> bool:
    """Assign a car from inventory to a driver in a race.

    If car_id is None, the first available car will be used.
    """
    race = _races.get(race_id)
    if race is None or race.started:
        return False

    if driver_id not in race.drivers:
        return False

    car = inventory.get_car(car_id) if car_id is not None else inventory.get_available_car()
    if car is None or car.status != "available":
        return False

    race.cars_by_driver[driver_id] = car.car_id
    inventory.set_car_status(car.car_id, "in_race")
    return True


def _race_ready_to_start(race: Race) -> bool:
    if not race.drivers:
        return False
    # every driver must have a car and be available
    for driver_id in race.drivers:
        if driver_id not in race.cars_by_driver:
            return False
        if not crew_management.is_crew_available(driver_id):
            return False
    return True


def start_race(race_id: str) -> bool:
    """Validate that the race can start, then mark it as started."""
    race = _races.get(race_id)
    if race is None or race.started:
        return False
    if not _race_ready_to_start(race):
        return False
    race.started = True
    return True


def complete_race(race_id: str, finishing_order: List[int]) -> bool:
    """Complete a race and send the results to the Results module."""
    race = _races.get(race_id)
    if race is None or not race.started or race.completed:
        return False

    # ensure finishing_order only contains drivers that actually participated
    if set(finishing_order) - set(race.drivers):
        return False

    results.record_race_result(race_id=race_id, finishing_order=finishing_order, prize_amount=race.prize_amount)

    # cars used in the race return to available status
    for car_id in race.cars_by_driver.values():
        inventory.set_car_status(car_id, "available")

    race.completed = True
    return True
