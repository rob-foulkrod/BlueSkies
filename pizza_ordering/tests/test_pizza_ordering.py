import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from pizza_ordering.cli import (
    _prompt_toppings,
    add_order,
    export_all_orders,
    main,
    print_orders,
)
from pizza_ordering.exporter import export_orders
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

    def test_main_menu_add_print_and_exit(self):
        # 1=Add order -> size 1, crust 2, toppings "1", no more pizzas
        # 2=Print orders, then an invalid option, then 4=Exit
        inputs = iter(["1", "1", "2", "1", "n", "2", "invalid", "4"])
        out = io.StringIO()
        with patch("builtins.input", side_effect=lambda _prompt="": next(inputs)):
            with redirect_stdout(out):
                main()
        output = out.getvalue()
        self.assertIn("Order added!", output)
        self.assertIn("Order #1", output)
        self.assertIn("Invalid option", output)
        self.assertIn("Goodbye!", output)

    def test_prompt_toppings_warns_on_invalid_selection(self):
        with patch("builtins.input", return_value="1,99,abc"):
            out = io.StringIO()
            with redirect_stdout(out):
                toppings = _prompt_toppings()
        self.assertEqual(toppings, [Topping.PEPPERONI])
        self.assertIn("Ignoring invalid topping selection: '99'", out.getvalue())
        self.assertIn("Ignoring invalid topping selection: 'abc'", out.getvalue())

    def test_export_all_orders_prints_generated_paths(self):
        storage = OrderStorage()
        storage.add_order([Pizza(size=Size.SMALL, crust=Crust.REGULAR)])
        paths = (Path("exports/orders.json"), Path("exports/orders.html"))
        out = io.StringIO()
        with patch("pizza_ordering.cli.export_orders", return_value=paths):
            with redirect_stdout(out):
                export_all_orders(storage)
        self.assertIn("Export complete!", out.getvalue())
        self.assertIn("orders.json", out.getvalue())
        self.assertIn("orders.html", out.getvalue())


class ExportTests(unittest.TestCase):
    def test_export_writes_json_and_self_contained_html(self):
        storage = OrderStorage()
        pizza = Pizza(
            size=Size.LARGE,
            crust=Crust.STUFFED,
            toppings=[Topping.PEPPERONI],
        )
        storage.add_order([pizza])
        export_time = datetime(2026, 9, 17, 10, 30)

        with tempfile.TemporaryDirectory() as temp_dir:
            json_path, html_path = export_orders(
                storage.all_orders(), temp_dir, export_time
            )
            data = json.loads(json_path.read_text(encoding="utf-8"))
            html = html_path.read_text(encoding="utf-8")

        self.assertEqual(data["exported_at"], export_time.isoformat())
        self.assertEqual(data["order_count"], 1)
        self.assertEqual(data["grand_total"], pizza.price)
        self.assertEqual(data["orders"][0]["pizzas"][0]["size"], "Large")
        self.assertIn("const DATA =", html)
        self.assertIn("Pepperoni", html)
        self.assertNotIn("<script src=", html)


if __name__ == "__main__":
    unittest.main()
