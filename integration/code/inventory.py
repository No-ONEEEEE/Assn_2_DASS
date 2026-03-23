"""Inventory module for StreetRace Manager.

Tracks cars, tools, and the global cash balance.
"""
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Car:
    car_id: int
    model: str
    status: str  # e.g. "available", "in_race", "damaged", "in_repair"


@dataclass
class Tool:
    tool_id: int
    name: str
    quantity: int


_cars: Dict[int, Car] = {}
_tools: Dict[int, Tool] = {}
_cash_balance: int = 0


def add_car(car_id: int, model: str, status: str = "available") -> Car:
    """Add a car to the inventory.

    If the id already exists, the existing car is overwritten.
    """
    car = Car(car_id=car_id, model=model, status=status)
    _cars[car_id] = car
    return car


def get_car(car_id: int) -> Optional[Car]:
    """Return a car by id, or None if not found."""
    return _cars.get(car_id)


def get_available_car() -> Optional[Car]:
    """Return the first available car, or None if none are available."""
    for car in _cars.values():
        if car.status == "available":
            return car
    return None


def set_car_status(car_id: int, status: str) -> bool:
    """Update the status of a car; returns True if car exists."""
    car = _cars.get(car_id)
    if car is None:
        return False
    car.status = status
    return True


def add_tool(tool_id: int, name: str, quantity: int) -> Tool:
    """Add a tool or spare part to the inventory."""
    tool = _tools.get(tool_id)
    if tool is None:
        tool = Tool(tool_id=tool_id, name=name, quantity=max(quantity, 0))
        _tools[tool_id] = tool
    else:
        tool.name = name
        tool.quantity += quantity
    return tool


def update_tool_quantity(tool_id: int, delta_quantity: int) -> bool:
    """Adjust the quantity of a tool, creating it with quantity 0 if needed."""
    tool = _tools.get(tool_id)
    if tool is None:
        tool = Tool(tool_id=tool_id, name=str(tool_id), quantity=0)
        _tools[tool_id] = tool
    tool.quantity = max(0, tool.quantity + delta_quantity)
    return True


def add_cash(amount: int) -> None:
    """Increase the global cash balance by the given amount."""
    global _cash_balance
    _cash_balance += amount


def deduct_cash(amount: int) -> None:
    """Decrease the global cash balance by the given amount (not below zero)."""
    global _cash_balance
    _cash_balance = max(0, _cash_balance - amount)


def get_cash_balance() -> int:
    """Return the current cash balance."""
    return _cash_balance


def has_damaged_car() -> bool:
    """Return True if at least one car is currently marked as damaged.

    This is used by Mission Planning to enforce the rule that missions must
    involve a mechanic whenever there is a damaged car in the system.
    """
    return any(car.status == "damaged" for car in _cars.values())
