# BlueSkies
Sample Project

## Pizza Ordering System

A Python 3.13 console application for placing pizza orders. Requires no
external dependencies (standard library only).

Each pizza's price is calculated from its size, crust type, and toppings.
Orders are kept in memory for the lifetime of the program.

### Run

```bash
python3 -m pizza_ordering
```

You will be presented with a menu to add an order (choosing size, crust,
and toppings for one or more pizzas), print all orders placed so far, or
export them. Export creates a timestamped JSON file and a self-contained
HTML viewer in the `exports/` directory. Open the HTML file in a browser
to browse the exported orders and totals.

### Run tests

```bash
python3 -m unittest discover -s pizza_ordering/tests -v
```
