import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from pizza_ordering.cli import add_order, print_orders
from pizza_ordering.models import Crust, Pizza, Size, Topping
from pizza_ordering.storage import OrderStorage


class PizzaPriceTests(unittest.TestCase):
    def test_price_with_no_toppings(self):
        pizza = Pizza(size=Size.MEDIUM, crust=Crust.REGULAR, toppings=[])
        self.assertEqual(pizza.price, 10.00)

    def test_price_with_crust_and_toppings(self):
        pizza = Pizza(
            size=Size.LARGE,
            crust=Crust.STUFFED,
            toppings=[Topping.PEPPERONI, Topping.MUSHROOM],
        )
        # 12.00 (large) + 2.50 (stuffed) + 1.50 (pepperoni) + 1.00 (mushroom)
        self.assertEqual(pizza.price, 17.00)

    def test_describe_contains_price_and_toppings(self):
        pizza = Pizza(size=Size.SMALL, crust=Crust.THIN, toppings=[Topping.ONION])
        description = pizza.describe()
        self.assertIn("Small", description)
        self.assertIn("Thin", description)
        self.assertIn("Onion", description)
        self.assertIn(f"${pizza.price:.2f}", description)


class OrderStorageTests(unittest.TestCase):
    def test_add_order_assigns_sequential_ids(self):
        storage = OrderStorage()
        pizza = Pizza(size=Size.SMALL, crust=Crust.REGULAR, toppings=[])
        order1 = storage.add_order([pizza])
        order2 = storage.add_order([pizza])
        self.assertEqual(order1.order_id, 1)
        self.assertEqual(order2.order_id, 2)
        self.assertEqual(len(storage), 2)

    def test_get_order_returns_none_when_missing(self):
        storage = OrderStorage()
        self.assertIsNone(storage.get_order(99))

    def test_order_total_sums_all_pizzas(self):
        storage = OrderStorage()
        pizza_a = Pizza(size=Size.SMALL, crust=Crust.REGULAR, toppings=[])
        pizza_b = Pizza(size=Size.MEDIUM, crust=Crust.THIN, toppings=[Topping.BACON])
        order = storage.add_order([pizza_a, pizza_b])
        expected_total = pizza_a.price + pizza_b.price
        self.assertEqual(order.total, round(expected_total, 2))


class CliTests(unittest.TestCase):
    def test_add_order_and_print_orders(self):
        storage = OrderStorage()
        # Size choice 1 (Small), Crust choice 2 (Regular), toppings "1,2",
        # then decline to add another pizza to the order.
        inputs = iter(["1", "2", "1,2", "n"])
        out = io.StringIO()
        with patch("builtins.input", side_effect=lambda _prompt="": next(inputs)):
            with redirect_stdout(out):
                add_order(storage)

        self.assertEqual(len(storage), 1)

        out2 = io.StringIO()
        with redirect_stdout(out2):
            print_orders(storage)
        self.assertIn("Order #1", out2.getvalue())


if __name__ == "__main__":
    unittest.main()
