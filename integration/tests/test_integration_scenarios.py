import pytest

from street_race_manager import (
    crew_management,
    inventory,
    maintenance,
    mission_planning,
    race_management,
    registration,
    reporting,
    results,
)


@pytest.fixture(autouse=True)
def reset_state():
    registration._crew_by_id.clear()  # type: ignore[attr-defined]
    registration._next_id = 1  # type: ignore[attr-defined]

    crew_management._skills.clear()  # type: ignore[attr-defined]
    crew_management._availability.clear()  # type: ignore[attr-defined]

    inventory._cars.clear()  # type: ignore[attr-defined]
    inventory._tools.clear()  # type: ignore[attr-defined]
    inventory._cash_balance = 0  # type: ignore[attr-defined]

    race_management._races.clear()  # type: ignore[attr-defined]
    results._race_results.clear()  # type: ignore[attr-defined]
    results._driver_stats.clear()  # type: ignore[attr-defined]
    mission_planning._missions.clear()  # type: ignore[attr-defined]


# Test Case 1

def test_register_driver_and_enter_race_success():
    alex = registration.register_crew_member("Alex", "driver")
    race_management.create_race("R1", "Night Street Run", 1000)
    inventory.add_car(1, "Car A")

    assert race_management.register_driver_for_race("R1", alex.crew_id) is True
    assert race_management.assign_car_to_driver("R1", alex.crew_id) is True

    race = race_management._races["R1"]  # type: ignore[attr-defined]
    assert alex.crew_id in race.drivers
    assert race.cars_by_driver[alex.crew_id] == 1
    assert inventory.get_car(1).status == "in_race"


# Test Case 2

def test_enter_race_without_registered_driver_fails():
    race_management.create_race("R2", "Illegal Sprint", 500)
    assert race_management.register_driver_for_race("R2", 999) is False
    assert race_management._races["R2"].drivers == []  # type: ignore[attr-defined]


# Test Case 3

def test_complete_race_updates_results_and_cash():
    alex = registration.register_crew_member("Alex", "driver")
    race_management.create_race("R1", "Night Street Run", 1000)
    inventory.add_car(1, "Car A")
    race_management.register_driver_for_race("R1", alex.crew_id)
    race_management.assign_car_to_driver("R1", alex.crew_id)

    before_cash = inventory.get_cash_balance()
    assert race_management.start_race("R1") is True
    assert race_management.complete_race("R1", [alex.crew_id]) is True

    stats = results.get_driver_statistics(alex.crew_id)
    assert stats.wins == 1
    assert stats.points == 10
    assert inventory.get_cash_balance() == before_cash + 1000
    assert inventory.get_car(1).status == "available"


# Test Case 4

def test_mission_role_validation_and_missing_mechanic_case():
    sam = registration.register_crew_member("Sam", "driver")
    lee = registration.register_crew_member("Lee", "mechanic")
    crew_management.set_availability(sam.crew_id, True)
    crew_management.set_availability(lee.crew_id, True)

    mission_planning.create_mission("M1", "delivery", {"driver", "mechanic"}, 500)
    mission_planning.assign_crew_to_mission("M1", [sam.crew_id, lee.crew_id])
    assert mission_planning.validate_mission("M1") is True

    mission_planning.assign_crew_to_mission("M1", [sam.crew_id])
    assert mission_planning.validate_mission("M1") is False


# Test Case 5

def test_mechanic_cannot_register_as_driver():
    blake = registration.register_crew_member("Blake", "mechanic")
    race_management.create_race("R3", "Role Check Run", 200)

    assert race_management.register_driver_for_race("R3", blake.crew_id) is False
    assert race_management._races["R3"].drivers == []  # type: ignore[attr-defined]


# Test Case 6

def test_unavailable_driver_blocks_race_start():
    chris = registration.register_crew_member("Chris", "driver")
    race_management.create_race("R4", "Availability Check", 300)
    inventory.add_car(2, "Car B")

    assert race_management.register_driver_for_race("R4", chris.crew_id) is True
    assert race_management.assign_car_to_driver("R4", chris.crew_id) is True
    assert crew_management.set_availability(chris.crew_id, False) is True

    assert race_management.start_race("R4") is False


# Test Case 7

def test_multiple_drivers_points_distribution_and_leaderboard():
    a = registration.register_crew_member("A", "driver")
    b = registration.register_crew_member("B", "driver")
    c = registration.register_crew_member("C", "driver")
    for driver in (a, b, c):
        crew_management.set_availability(driver.crew_id, True)

    inventory.add_car(3, "Car C")
    inventory.add_car(4, "Car D")
    inventory.add_car(5, "Car E")
    race_management.create_race("R5", "Championship", 0)

    for driver in (a, b, c):
        assert race_management.register_driver_for_race("R5", driver.crew_id)
        assert race_management.assign_car_to_driver("R5", driver.crew_id)

    assert race_management.start_race("R5") is True
    assert race_management.complete_race("R5", [a.crew_id, b.crew_id, c.crew_id]) is True

    a_stats = results.get_driver_statistics(a.crew_id)
    b_stats = results.get_driver_statistics(b.crew_id)
    c_stats = results.get_driver_statistics(c.crew_id)
    assert (a_stats.points, b_stats.points, c_stats.points) == (10, 5, 3)
    assert (a_stats.wins, b_stats.wins, c_stats.wins) == (1, 0, 0)

    leaderboard = results.get_leaderboard()
    assert [x[0] for x in leaderboard[:3]] == [a.crew_id, b.crew_id, c.crew_id]


# Test Case 8

def test_mission_blocked_when_damaged_car_exists_without_mechanic_requirement():
    inventory.add_car(6, "Car F", status="damaged")
    dana = registration.register_crew_member("Dana", "driver")
    crew_management.set_availability(dana.crew_id, True)

    mission_planning.create_mission("M2", "delivery", {"driver"}, 400)
    mission_planning.assign_crew_to_mission("M2", [dana.crew_id])
    assert mission_planning.validate_mission("M2") is False


# Test Case 9

def test_successful_mission_increases_cash_balance():
    sam = registration.register_crew_member("Sam", "driver")
    lee = registration.register_crew_member("Lee", "mechanic")
    crew_management.set_availability(sam.crew_id, True)
    crew_management.set_availability(lee.crew_id, True)

    mission_planning.create_mission("M1", "delivery", {"driver", "mechanic"}, 500)
    mission_planning.assign_crew_to_mission("M1", [sam.crew_id, lee.crew_id])
    assert mission_planning.start_mission("M1") is True

    before_cash = inventory.get_cash_balance()
    assert mission_planning.complete_mission("M1", outcome="success", damaged_car_ids=[]) is True
    assert inventory.get_cash_balance() == before_cash + 500
    assert mission_planning.get_all_missions()["M1"].completed is True


# Test Case 10

def test_reporting_summaries_match_underlying_modules():
    alex = registration.register_crew_member("Alex", "driver")
    inventory.add_car(1, "Car A")
    race_management.create_race("R1", "Night Street Run", 1000)
    race_management.register_driver_for_race("R1", alex.crew_id)
    race_management.assign_car_to_driver("R1", alex.crew_id)
    race_management.start_race("R1")
    race_management.complete_race("R1", [alex.crew_id])

    sam = registration.register_crew_member("Sam", "driver")
    lee = registration.register_crew_member("Lee", "mechanic")
    crew_management.set_availability(sam.crew_id, True)
    crew_management.set_availability(lee.crew_id, True)
    mission_planning.create_mission("M1", "delivery", {"driver", "mechanic"}, 500)
    mission_planning.assign_crew_to_mission("M1", [sam.crew_id, lee.crew_id])
    mission_planning.start_mission("M1")
    mission_planning.complete_mission("M1", outcome="success", damaged_car_ids=[])

    race_summary = reporting.generate_race_summary()
    mission_summary = reporting.generate_mission_summary()
    financial = reporting.generate_financial_report()

    assert any(row.get("race_id") == "R1" and row.get("winner_id") == alex.crew_id for row in race_summary)
    assert any(row.get("mission_id") == "M1" and row.get("completed") is True for row in mission_summary)
    assert financial["cash_balance"] == inventory.get_cash_balance()


# Additional coverage gaps beyond design doc

def test_complete_race_rejects_non_participating_finisher():
    alex = registration.register_crew_member("Alex", "driver")
    bob = registration.register_crew_member("Bob", "driver")
    inventory.add_car(1, "Car A")
    race_management.create_race("R6", "Invalid Finishers", 100)
    race_management.register_driver_for_race("R6", alex.crew_id)
    race_management.assign_car_to_driver("R6", alex.crew_id)
    race_management.start_race("R6")

    assert race_management.complete_race("R6", [bob.crew_id]) is False


def test_complete_mission_without_start_currently_allowed_documented_behavior_gap():
    mission_planning.create_mission("M3", "delivery", {"driver"}, 100)
    # This currently returns True by implementation even when mission was never started.
    assert mission_planning.complete_mission("M3", outcome="failure", damaged_car_ids=[]) is True


def test_schedule_repair_for_missing_car_returns_job_but_no_car_status_change():
    job = inventory.get_car(999)
    assert job is None
    repair = maintenance.schedule_repair(999, 200)
    assert repair.car_id == 999
    # No car exists to update, so still None.
    assert inventory.get_car(999) is None


def test_race_cannot_start_when_driver_has_no_assigned_car():
    alex = registration.register_crew_member("Alex", "driver")
    race_management.create_race("R7", "No Car Start", 100)
    assert race_management.register_driver_for_race("R7", alex.crew_id) is True
    # No car assigned for Alex
    assert race_management.start_race("R7") is False


def test_duplicate_driver_registration_not_duplicated_in_same_race():
    alex = registration.register_crew_member("Alex", "driver")
    race_management.create_race("R8", "Duplicate Driver Check", 100)
    assert race_management.register_driver_for_race("R8", alex.crew_id) is True
    assert race_management.register_driver_for_race("R8", alex.crew_id) is True
    race = race_management._races["R8"]  # type: ignore[attr-defined]
    assert race.drivers.count(alex.crew_id) == 1


def test_complete_race_twice_is_rejected_and_does_not_double_pay_cash():
    alex = registration.register_crew_member("Alex", "driver")
    inventory.add_car(10, "Car X")
    race_management.create_race("R9", "Double Complete", 700)
    race_management.register_driver_for_race("R9", alex.crew_id)
    race_management.assign_car_to_driver("R9", alex.crew_id)
    race_management.start_race("R9")

    assert race_management.complete_race("R9", [alex.crew_id]) is True
    after_first = inventory.get_cash_balance()
    assert race_management.complete_race("R9", [alex.crew_id]) is False
    assert inventory.get_cash_balance() == after_first


def test_mission_validation_fails_when_required_crew_unavailable():
    driver = registration.register_crew_member("Driver", "driver")
    mech = registration.register_crew_member("Mech", "mechanic")
    crew_management.set_availability(driver.crew_id, True)
    crew_management.set_availability(mech.crew_id, False)

    mission_planning.create_mission("M4", "delivery", {"driver", "mechanic"}, 200)
    mission_planning.assign_crew_to_mission("M4", [driver.crew_id, mech.crew_id])
    assert mission_planning.validate_mission("M4") is False


def test_failed_mission_marks_cars_damaged_and_does_not_add_cash():
    inventory.add_car(21, "Car Y")
    inventory.add_car(22, "Car Z")
    d = registration.register_crew_member("D", "driver")
    m = registration.register_crew_member("M", "mechanic")
    crew_management.set_availability(d.crew_id, True)
    crew_management.set_availability(m.crew_id, True)
    mission_planning.create_mission("M5", "delivery", {"driver", "mechanic"}, 900)
    mission_planning.assign_crew_to_mission("M5", [d.crew_id, m.crew_id])
    mission_planning.start_mission("M5")
    before = inventory.get_cash_balance()

    assert mission_planning.complete_mission("M5", outcome="failure", damaged_car_ids=[21, 22]) is True
    assert inventory.get_car(21).status == "damaged"
    assert inventory.get_car(22).status == "damaged"
    assert inventory.get_cash_balance() == before


def test_maintenance_repair_flow_changes_status_and_cash():
    inventory.add_car(31, "Car Repair")
    inventory.set_car_status(31, "damaged")
    inventory.add_cash(1000)

    job = maintenance.schedule_repair(31, estimated_cost=300)
    assert inventory.get_car(31).status == "in_repair"

    assert maintenance.complete_repair(job.job_id, actual_cost=250) is True
    assert inventory.get_car(31).status == "available"
    assert inventory.get_cash_balance() == 750


def test_reporting_empty_state_is_consistent():
    assert reporting.generate_race_summary() == []
    assert reporting.generate_mission_summary() == []
    assert reporting.generate_financial_report() == {"cash_balance": 0}
