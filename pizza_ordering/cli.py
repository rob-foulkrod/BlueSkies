"""Console application for the Pizza Ordering System.

Run with:  python -m pizza_ordering
"""
from __future__ import annotations

from typing import List, Type, TypeVar

from .exporter import export_orders
from .models import Crust, Pizza, Size, Topping
from .storage import OrderStorage

E = TypeVar("E")


def _safe_int(text: str) -> int | None:
    """Parse ``text`` as an int, returning None instead of raising on failure."""
    try:
        return int(text)
    except ValueError:
        return None

def _prompt_choice(prompt: str, options: Type[E]) -> E:
    """Prompt the user to choose one value from an Enum type."""
    options_list = list(options)
    while True:
        print(prompt)
        for index, option in enumerate(options_list, start=1):
            print(f"  {index}. {option.label} (${option.price:.2f})")
        choice_num = _safe_int(input("Enter number: ").strip())
        if choice_num is not None and 1 <= choice_num <= len(options_list):
            return options_list[choice_num - 1]
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
        part_num = _safe_int(part)
        if part_num is not None and 1 <= part_num <= len(toppings_list):
            selected.append(toppings_list[part_num - 1])
        else:
            print(f"Ignoring invalid topping selection: '{part}'")
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


def export_all_orders(storage: OrderStorage) -> None:
    """Export all current orders and print the generated file paths."""
    json_path, html_path = export_orders(storage.all_orders())
    print("\nExport complete!")
    print(f"JSON: {json_path.resolve()}")
    print(f"HTML viewer: {html_path.resolve()}")


def main() -> None:
    """Run the interactive menu loop.

    Orders are stored only in memory via ``OrderStorage``, so they are
    lost once the program exits; there is no persistence to disk.
    """
    storage = OrderStorage()
    menu = (
        "\nPizza Ordering System\n"
        "1. Add order\n"
        "2. Print orders\n"
        "3. Export orders\n"
        "4. Exit\n"
    )
    while True:
        print(menu)
        choice = input("Choose an option: ").strip()
        if choice == "1":
            add_order(storage)
        elif choice == "2":
            print_orders(storage)
        elif choice == "3":
            export_all_orders(storage)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    main()
