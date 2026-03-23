"""Vehicle Maintenance module for StreetRace Manager."""
from dataclasses import dataclass
from typing import Dict, List

from . import inventory


@dataclass
class RepairJob:
    job_id: int
    car_id: int
    estimated_cost: int
    actual_cost: int | None = None
    completed: bool = False


_jobs: Dict[int, RepairJob] = {}
_next_job_id: int = 1


def schedule_repair(car_id: int, estimated_cost: int) -> RepairJob:
    """Create a new repair job for the given car and mark the car as in_repair."""
    global _next_job_id
    job = RepairJob(job_id=_next_job_id, car_id=car_id, estimated_cost=estimated_cost)
    _jobs[job.job_id] = job
    _next_job_id += 1
    inventory.set_car_status(car_id, "in_repair")
    return job


def complete_repair(job_id: int, actual_cost: int) -> bool:
    """Mark a repair job as completed, deducting the cost and making the car available."""
    job = _jobs.get(job_id)
    if job is None or job.completed:
        return False
    job.actual_cost = actual_cost
    job.completed = True
    inventory.deduct_cash(actual_cost)
    inventory.set_car_status(job.car_id, "available")
    return True


def get_car_service_history(car_id: int) -> List[RepairJob]:
    """Return all repair jobs associated with the given car."""
    return [job for job in _jobs.values() if job.car_id == car_id]
