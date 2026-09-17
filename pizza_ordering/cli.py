"""Console application for the Pizza Ordering System.

Run with:  python -m pizza_ordering
"""
from __future__ import annotations

from typing import List, Type, TypeVar

from .models import Crust, Pizza, Size, Topping
from .storage import OrderStorage

E = TypeVar("E")


def _prompt_choice(prompt: str, options: Type[E]) -> E:
    """Prompt the user to choose one value from an Enum type."""
    options_list = list(options)
    while True:
        print(prompt)
        for index, option in enumerate(options_list, start=1):
            print(f"  {index}. {option.label} (${option.price:.2f})")
        choice = input("Enter number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options_list):
            return options_list[int(choice) - 1]
        print("Invalid choice, please try again.\n")


def _prompt_toppings() -> List[Topping]:
    """Prompt the user to choose zero or more toppings."""
    toppings_list = list(Topping)
    print("Available toppings:")
    for index, topping in enumerate(toppings_list, start=1):
        print(f"  {index}. {topping.label} (${topping.price:.2f})")
    raw = input(
        "Enter topping numbers separated by commas (or leave blank for none): "
    ).strip()
    if not raw:
        return []
    selected: List[Topping] = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit() and 1 <= int(part) <= len(toppings_list):
            selected.append(toppings_list[int(part) - 1])
    return selected


def build_pizza() -> Pizza:
    """Interactively build a single Pizza from user input."""
    size = _prompt_choice("Choose a size:", Size)
    crust = _prompt_choice("Choose a crust:", Crust)
    toppings = _prompt_toppings()
    return Pizza(size=size, crust=crust, toppings=toppings)


def add_order(storage: OrderStorage) -> None:
    """Prompt the user for one or more pizzas and store the order."""
    pizzas: List[Pizza] = [build_pizza()]
    while input("Add another pizza to this order? (y/N): ").strip().lower() == "y":
        pizzas.append(build_pizza())
    order = storage.add_order(pizzas)
    print("\nOrder added!")
    print(order.describe())


def print_orders(storage: OrderStorage) -> None:
    """Print all orders currently stored in memory."""
    orders = storage.all_orders()
    if not orders:
        print("No orders yet.")
        return
    for order in orders:
        print(order.describe())
        print()


def main() -> None:
    storage = OrderStorage()
    menu = (
        "\nPizza Ordering System\n"
        "1. Add order\n"
        "2. Print orders\n"
        "3. Exit\n"
    )
    while True:
        print(menu)
        choice = input("Choose an option: ").strip()
        if choice == "1":
            add_order(storage)
        elif choice == "2":
            print_orders(storage)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option, please try again.")


if __name__ == "__main__":
    main()
