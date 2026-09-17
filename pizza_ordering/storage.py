"""In-memory storage for pizza orders."""
from __future__ import annotations

from typing import List, Optional

from .models import Order, Pizza


class OrderStorage:
    """Keeps track of orders in memory for the lifetime of the process."""

    def __init__(self) -> None:
        self._orders: List[Order] = []
        self._next_id: int = 1

    def add_order(self, pizzas: List[Pizza]) -> Order:
        """Create a new order from the given pizzas and store it."""
        order = Order(order_id=self._next_id, pizzas=list(pizzas))
        self._orders.append(order)
        self._next_id += 1
        return order

    def get_order(self, order_id: int) -> Optional[Order]:
        for order in self._orders:
            if order.order_id == order_id:
                return order
        return None

    def all_orders(self) -> List[Order]:
        return list(self._orders)

    def __len__(self) -> int:
        return len(self._orders)
