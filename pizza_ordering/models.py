"""Domain models for the Pizza Ordering System.

Defines the crust, size, and topping options along with their prices,
the ``Pizza`` class that calculates a total price from those choices,
and the ``Order`` class that groups one or more pizzas together.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List


class Crust(Enum):
    """Available crust types and their base price contribution."""

    THIN = ("Thin", 1.00)
    REGULAR = ("Regular", 0.00)
    THICK = ("Thick", 1.50)
    STUFFED = ("Stuffed", 2.50)

    def __init__(self, label: str, price: float) -> None:
        self.label = label
        self.price = price


class Size(Enum):
    """Available pizza sizes and their base price."""

    SMALL = ("Small", 8.00)
    MEDIUM = ("Medium", 10.00)
    LARGE = ("Large", 12.00)
    XLARGE = ("X-Large", 14.00)

    def __init__(self, label: str, price: float) -> None:
        self.label = label
        self.price = price


class Topping(Enum):
    """Available toppings and the price added per topping."""

    PEPPERONI = ("Pepperoni", 1.50)
    MUSHROOM = ("Mushroom", 1.00)
    ONION = ("Onion", 0.75)
    SAUSAGE = ("Sausage", 1.50)
    BACON = ("Bacon", 1.75)
    EXTRA_CHEESE = ("Extra Cheese", 1.25)
    OLIVES = ("Olives", 1.00)
    GREEN_PEPPER = ("Green Pepper", 0.75)
    PINEAPPLE = ("Pineapple", 1.00)

    def __init__(self, label: str, price: float) -> None:
        self.label = label
        self.price = price


@dataclass
class Pizza:
    """A single pizza with a size, crust, and list of toppings."""

    size: Size
    crust: Crust
    toppings: List[Topping] = field(default_factory=list)

    @property
    def price(self) -> float:
        """Total price for this pizza: size + crust + all toppings."""
        toppings_total = sum(topping.price for topping in self.toppings)
        return round(self.size.price + self.crust.price + toppings_total, 2)

    def describe(self) -> str:
        toppings = ", ".join(t.label for t in self.toppings) or "No toppings"
        return (
            f"{self.size.label} pizza, {self.crust.label} crust, "
            f"Toppings: {toppings} - ${self.price:.2f}"
        )


@dataclass
class Order:
    """An order made up of one or more pizzas."""

    order_id: int
    pizzas: List[Pizza] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def total(self) -> float:
        return round(sum(pizza.price for pizza in self.pizzas), 2)

    def describe(self) -> str:
        lines = [
            f"Order #{self.order_id} "
            f"({self.created_at.strftime('%Y-%m-%d %H:%M:%S')})"
        ]
        for index, pizza in enumerate(self.pizzas, start=1):
            lines.append(f"  {index}. {pizza.describe()}")
        lines.append(f"  Total: ${self.total:.2f}")
        return "\n".join(lines)
