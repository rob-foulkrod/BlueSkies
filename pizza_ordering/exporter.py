"""Export pizza orders as JSON with a self-contained HTML viewer."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .models import Order


def _order_data(order: Order) -> dict:
    return {
        "order_id": order.order_id,
        "created_at": order.created_at.isoformat(),
        "total": order.total,
        "pizzas": [
            {
                "size": pizza.size.label,
                "crust": pizza.crust.label,
                "toppings": [topping.label for topping in pizza.toppings],
                "price": pizza.price,
            }
            for pizza in order.pizzas
        ],
    }


def _html_viewer(data: dict) -> str:
    embedded_data = json.dumps(data).replace("<", "\\u003c").replace(">", "\\u003e")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pizza Order Export</title>
  <script>
    (() => {{
      const param = new URLSearchParams(window.location.search).get("scoutTheme");
      const theme =
        param || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      document.documentElement.setAttribute("data-theme", theme);
    }})();
  </script>
  <style>
    :root {{
      color-scheme: light;
      --cp-bg: #f7f4ef;
      --cp-bg-elevated: #fcfbf8;
      --cp-surface: #ffffff;
      --cp-surface-soft: #f5f5f5;
      --cp-border: #dedede;
      --cp-border-strong: #919191;
      --cp-text: #242424;
      --cp-text-muted: #5c5c5c;
      --cp-text-soft: #6f6f6f;
      --cp-accent: #b11f4b;
      --cp-accent-hover: #9a1a41;
      --cp-accent-soft: rgba(177, 31, 75, 0.08);
      --cp-accent-fg: #ffffff;
      --cp-success: #16a34a;
      --cp-danger: #dc2626;
      --cp-warning: #f59e0b;
      --cp-link: #0078d4;
      --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.12);
      --cp-overlay: rgba(255, 255, 255, 0.8);
      --cp-panel: rgba(255, 255, 255, 0.86);
      --cp-panel-strong: rgba(255, 255, 255, 0.96);
      --cp-sheen: rgba(255, 255, 255, 0.55);
      --cp-highlight: rgba(177, 31, 75, 0.12);
    }}
    html[data-theme="dark"] {{
      color-scheme: dark;
      --cp-bg: #3d3b3a;
      --cp-bg-elevated: #343231;
      --cp-surface: #292929;
      --cp-surface-soft: #2e2e2e;
      --cp-border: #474747;
      --cp-border-strong: #5f5f5f;
      --cp-text: #dedede;
      --cp-text-muted: #919191;
      --cp-text-soft: #b0b0b0;
      --cp-accent: #fd8ea1;
      --cp-accent-hover: #fb7b91;
      --cp-accent-soft: rgba(253, 142, 161, 0.14);
      --cp-accent-fg: #1a1a1a;
      --cp-success: #4ade80;
      --cp-danger: #f87171;
      --cp-warning: #fbbf24;
      --cp-link: #4da6ff;
      --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.32);
      --cp-overlay: rgba(41, 41, 41, 0.88);
      --cp-panel: rgba(41, 41, 41, 0.72);
      --cp-panel-strong: rgba(41, 41, 41, 0.96);
      --cp-sheen: rgba(255, 255, 255, 0.04);
      --cp-highlight: rgba(253, 142, 161, 0.12);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--cp-bg);
      color: var(--cp-text);
      font-family: "Segoe UI", Aptos, Calibri, -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    main {{ width: min(960px, calc(100% - 32px)); margin: 48px auto; }}
    header {{ display: flex; justify-content: space-between; gap: 24px; align-items: end; margin-bottom: 24px; }}
    h1, h2, p {{ margin-top: 0; }}
    h1 {{ margin-bottom: 8px; font-size: 2rem; letter-spacing: 0; }}
    .muted {{ color: var(--cp-text-muted); margin-bottom: 0; }}
    .summary {{ display: flex; gap: 24px; flex-wrap: wrap; }}
    .summary strong {{ display: block; font-size: 1.4rem; }}
    .order {{
      background: var(--cp-surface);
      border: 1px solid var(--cp-border);
      border-radius: 16px;
      box-shadow: 0 0 2px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.14);
      margin-bottom: 16px;
      padding: 24px;
    }}
    .order-heading {{ display: flex; justify-content: space-between; gap: 16px; align-items: baseline; }}
    .order h2 {{ font-size: 1.15rem; margin-bottom: 4px; }}
    .total {{ color: var(--cp-accent); font-size: 1.15rem; font-weight: 700; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
    th, td {{ border-top: 1px solid var(--cp-border); padding: 12px 8px; text-align: left; vertical-align: top; }}
    th {{ color: var(--cp-text-muted); font-size: 0.8rem; text-transform: uppercase; }}
    th:last-child, td:last-child {{ text-align: right; }}
    .empty {{ background: var(--cp-surface); border: 1px solid var(--cp-border); border-radius: 16px; padding: 32px; }}
    @media (max-width: 640px) {{
      main {{ margin: 24px auto; }}
      header, .order-heading {{ align-items: start; flex-direction: column; }}
      .order {{ padding: 16px; overflow-x: auto; }}
      th, td {{ min-width: 96px; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Pizza Orders</h1>
        <p class="muted" id="exported-at"></p>
      </div>
      <div class="summary">
        <div><span class="muted">Orders</span><strong id="order-count"></strong></div>
        <div><span class="muted">Grand total</span><strong id="grand-total"></strong></div>
      </div>
    </header>
    <section id="orders"></section>
  </main>
  <script>
    const DATA = {embedded_data};
    const money = value => new Intl.NumberFormat("en-US", {{ style: "currency", currency: "USD" }}).format(value);
    const dateTime = value => new Intl.DateTimeFormat(undefined, {{ dateStyle: "medium", timeStyle: "short" }}).format(new Date(value));
    document.getElementById("exported-at").textContent = `Exported ${{dateTime(DATA.exported_at)}}`;
    document.getElementById("order-count").textContent = DATA.order_count;
    document.getElementById("grand-total").textContent = money(DATA.grand_total);
    const orders = document.getElementById("orders");
    if (!DATA.orders.length) {{
      const empty = document.createElement("p");
      empty.className = "empty";
      empty.textContent = "No orders were available when this export was created.";
      orders.appendChild(empty);
    }}
    for (const order of DATA.orders) {{
      const article = document.createElement("article");
      article.className = "order";
      const heading = document.createElement("div");
      heading.className = "order-heading";
      heading.innerHTML = `<div><h2>Order #${{order.order_id}}</h2><p class="muted">${{dateTime(order.created_at)}}</p></div><span class="total">${{money(order.total)}}</span>`;
      const table = document.createElement("table");
      table.innerHTML = "<thead><tr><th>Pizza</th><th>Size</th><th>Crust</th><th>Toppings</th><th>Price</th></tr></thead>";
      const body = document.createElement("tbody");
      order.pizzas.forEach((pizza, index) => {{
        const row = document.createElement("tr");
        for (const value of [index + 1, pizza.size, pizza.crust, pizza.toppings.join(", ") || "None", money(pizza.price)]) {{
          const cell = document.createElement("td");
          cell.textContent = value;
          row.appendChild(cell);
        }}
        body.appendChild(row);
      }});
      table.appendChild(body);
      article.append(heading, table);
      orders.appendChild(article);
    }}
  </script>
</body>
</html>
"""


def export_orders(
    orders: Iterable[Order],
    output_dir: Path | str = "exports",
    exported_at: datetime | None = None,
) -> tuple[Path, Path]:
    """Write all supplied orders to JSON and a self-contained HTML viewer."""
    export_time = exported_at or datetime.now()
    order_list = list(orders)
    data = {
        "exported_at": export_time.isoformat(),
        "order_count": len(order_list),
        "grand_total": round(sum(order.total for order in order_list), 2),
        "orders": [_order_data(order) for order in order_list],
    }
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    base_name = f"pizza-orders-{export_time.strftime('%Y%m%d-%H%M%S-%f')}"
    json_path = destination / f"{base_name}.json"
    html_path = destination / f"{base_name}.html"
    json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    html_path.write_text(_html_viewer(data), encoding="utf-8")
    return json_path, html_path