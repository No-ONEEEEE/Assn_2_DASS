"""Quick script to exercise StreetRace Manager integration scenarios.

This is only for manually checking behaviour to match the written test cases
in integration_test_design_2_2.md.
"""
from street_race_manager import (
    registration,
    crew_management,
    inventory,
    race_management,
    results,
    mission_planning,
    reporting,
)


def reset_state() -> None:
    """Best-effort reset of module globals between runs.

    This clears known dictionaries in each module. It is not intended for
    production use, only for this demo script.
    """

    # registration
    registration._crew_by_id.clear()  # type: ignore[attr-defined]
    registration._next_id = 1  # type: ignore[attr-defined]

    # crew_management
    crew_management._skills.clear()  # type: ignore[attr-defined]
    crew_management._availability.clear()  # type: ignore[attr-defined]

    # inventory
    inventory._cars.clear()  # type: ignore[attr-defined]
    inventory._tools.clear()  # type: ignore[attr-defined]
    inventory._cash_balance = 0  # type: ignore[attr-defined]

    # race_management
    race_management._races.clear()  # type: ignore[attr-defined]

    # results
    results._race_results.clear()  # type: ignore[attr-defined]
    results._driver_stats.clear()  # type: ignore[attr-defined]

    # mission_planning
    mission_planning._missions.clear()  # type: ignore[attr-defined]


def main() -> None:
    reset_state()

    print("--- Test 1: register driver + enter race ---")
    alex = registration.register_crew_member("Alex", "driver")
    inventory.add_car(1, "Car A")
    race_management.create_race("R1", name="Night Street Run", prize_amount=1000)
    print("register_driver_for_race(R1, Alex) ->", race_management.register_driver_for_race("R1", alex.crew_id))
    print("assign_car_to_driver(R1, Alex) ->", race_management.assign_car_to_driver("R1", alex.crew_id))

    print("\n--- Test 2: unregistered driver ---")
    race_management.create_race("R2", name="Illegal Sprint", prize_amount=500)
    print("register_driver_for_race(R2, 999) ->", race_management.register_driver_for_race("R2", 999))

    print("\n--- Test 3: complete race, update results + inventory ---")
    start_cash = inventory.get_cash_balance()
    print("start cash:", start_cash)
    print("start_race(R1) ->", race_management.start_race("R1"))
    print("complete_race(R1) ->", race_management.complete_race("R1", [alex.crew_id]))
    print("Alex stats ->", results.get_driver_statistics(alex.crew_id))
    print("end cash:", inventory.get_cash_balance())

    print("\n--- Test 4: mission roles + validation ---")
    sam = registration.register_crew_member("Sam", "driver")
    lee = registration.register_crew_member("Lee", "mechanic")
    crew_management.set_availability(sam.crew_id, True)
    crew_management.set_availability(lee.crew_id, True)
    mission_planning.create_mission(
        "M1",
        mission_type="delivery",
        required_roles={"driver", "mechanic"},
        reward_amount=500,
    )
    mission_planning.assign_crew_to_mission("M1", [sam.crew_id, lee.crew_id])
    print("validate_mission(M1) [Sam+Lee] ->", mission_planning.validate_mission("M1"))
    mission_planning.assign_crew_to_mission("M1", [sam.crew_id])
    print("validate_mission(M1) [Sam only] ->", mission_planning.validate_mission("M1"))

    print("\n--- Test 5: wrong-role driver ---")
    blake = registration.register_crew_member("Blake", "mechanic")
    race_management.create_race("R3", name="Role Check Run", prize_amount=200)
    print(
        "register_driver_for_race(R3, Blake(mechanic)) ->",
        race_management.register_driver_for_race("R3", blake.crew_id),
    )

    print("\n--- Test 6: unavailable driver blocks start ---")
    chris = registration.register_crew_member("Chris", "driver")
    crew_management.set_availability(chris.crew_id, True)
    inventory.add_car(2, "Car B")
    race_management.create_race("R4", name="Availability Check", prize_amount=300)
    print("register_driver_for_race(R4, Chris) ->", race_management.register_driver_for_race("R4", chris.crew_id))
    print("assign_car_to_driver(R4, Chris) ->", race_management.assign_car_to_driver("R4", chris.crew_id))
    crew_management.set_availability(chris.crew_id, False)
    print("start_race(R4) with Chris unavailable ->", race_management.start_race("R4"))

    print("\n--- Test 7: multi-driver race points ---")
    A = registration.register_crew_member("A", "driver")
    B = registration.register_crew_member("B", "driver")
    C = registration.register_crew_member("C", "driver")
    for d in (A, B, C):
        crew_management.set_availability(d.crew_id, True)
    inventory.add_car(3, "Car C")
    inventory.add_car(4, "Car D")
    inventory.add_car(5, "Car E")
    race_management.create_race("R5", name="Championship", prize_amount=0)
    for d in (A, B, C):
        race_management.register_driver_for_race("R5", d.crew_id)
        race_management.assign_car_to_driver("R5", d.crew_id)
    print("start_race(R5) ->", race_management.start_race("R5"))
    print(
        "complete_race(R5) ->",
        race_management.complete_race("R5", [A.crew_id, B.crew_id, C.crew_id]),
    )
    print("stats A,B,C ->", results.get_driver_statistics(A.crew_id),
          results.get_driver_statistics(B.crew_id),
          results.get_driver_statistics(C.crew_id))

    print("\n--- Test 8: damaged car without mechanic ---")
    inventory.add_car(6, "Car F")
    inventory.set_car_status(6, "damaged")
    dana = registration.register_crew_member("Dana", "driver")
    crew_management.set_availability(dana.crew_id, True)
    mission_planning.create_mission(
        "M2",
        mission_type="delivery",
        required_roles={"driver"},
        reward_amount=400,
    )
    mission_planning.assign_crew_to_mission("M2", [dana.crew_id])
    print("validate_mission(M2) [damaged car, no mechanic] ->", mission_planning.validate_mission("M2"))

    print("\n--- Test 9: successful mission updates cash ---")
    start_cash = inventory.get_cash_balance()
    mission_planning.assign_crew_to_mission("M1", [sam.crew_id, lee.crew_id])
    print("re-validate M1 ->", mission_planning.validate_mission("M1"))
    mission_planning.start_mission("M1")
    mission_planning.complete_mission("M1", outcome="success", damaged_car_ids=[])
    print("cash before M1:", start_cash, "after M1:", inventory.get_cash_balance())

    print("\n--- Test 10: reporting summaries ---")
    print("race summary ->", reporting.generate_race_summary())
    print("mission summary ->", reporting.generate_mission_summary())
    print("financial report ->", reporting.generate_financial_report())


if __name__ == "__main__":
    main()
