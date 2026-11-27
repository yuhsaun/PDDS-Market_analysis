"""Amelia's view: which products are bought together?
Interaction: when the manager selects a product, show what it is most often bought with."""
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

# 1. DATA: read the database once (works from any folder)
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "sales.db"

PAIRS_SQL = """
SELECT p1.product_name AS product_a,
       p2.product_name AS product_b,
       COUNT(DISTINCT a.transaction_id) AS co_purchase_count
FROM TransactionItem a
JOIN TransactionItem b ON a.transaction_id = b.transaction_id
                      AND a.product_id < b.product_id
JOIN Product p1 ON p1.product_id = a.product_id
JOIN Product p2 ON p2.product_id = b.product_id
GROUP BY a.product_id, b.product_id
"""

with sqlite3.connect(DB_PATH) as conn:
    pairs = pd.read_sql_query(PAIRS_SQL, conn)

ALL = "All products"
options = [ALL] + sorted(set(pairs["product_a"]) | set(pairs["product_b"]))

# 2. THE APP AND ITS LAYOUT (what the user sees)
app = Dash(__name__)
app.layout = html.Div(
    [
        html.H2("What is bought together?"),
        html.P("Select a product to see what it is most often bought with:"),
        dcc.Dropdown(id="product-dropdown", options=options, value=ALL, clearable=False),
        dcc.Graph(id="pairs-chart"),
    ],
    style={"maxWidth": "900px", "margin": "auto", "padding": "20px"},
)


# 3. THE CALLBACK (what happens when the dropdown changes)
@app.callback(Output("pairs-chart", "figure"), Input("product-dropdown", "value"))
def update_chart(selected_product):
    if selected_product == ALL:
        # every pair, labelled "A + B"
        shown = pairs.copy()
        shown["label"] = shown["product_a"] + "  +  " + shown["product_b"]
        title = "Product pairs most often bought in the same transaction"
    else:
        # only pairs containing the selected product, labelled by the OTHER product
        shown = pairs[(pairs["product_a"] == selected_product) | (pairs["product_b"] == selected_product)].copy()
        shown["label"] = shown.apply(
            lambda r: r["product_b"] if r["product_a"] == selected_product else r["product_a"], axis=1)
        title = f"Products most often bought with {selected_product}"

    shown = shown.sort_values("co_purchase_count").tail(10)   # biggest bar on top
    fig = px.bar(shown, x="co_purchase_count", y="label", orientation="h", text="co_purchase_count",
                 title=title,
                 labels={"co_purchase_count": "Transactions containing both products", "label": ""})
    fig.update_layout(plot_bgcolor="white", xaxis=dict(dtick=1))
    return fig


# 4. RUN
if __name__ == "__main__":
    app.run(debug=True)
