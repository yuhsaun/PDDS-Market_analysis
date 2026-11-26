"""Prototype: product pairs most often bought in the same transaction."""
import sqlite3
import pandas as pd
import plotly.express as px

DB_PATH = "data/sales.db"   # change if your database file has a different name
TOP_N = 10                  # how many pairs to show

QUERY = """
SELECT p1.product_name AS product_a,
       p2.product_name AS product_b,
       COUNT(DISTINCT a.transaction_id) AS co_purchase_count
FROM TransactionItem a
JOIN TransactionItem b ON a.transaction_id = b.transaction_id
                      AND a.product_id < b.product_id
JOIN Product p1 ON p1.product_id = a.product_id
JOIN Product p2 ON p2.product_id = b.product_id
GROUP BY a.product_id, b.product_id
ORDER BY co_purchase_count DESC, product_a
LIMIT ?
"""

with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql_query(QUERY, conn, params=(TOP_N,))

df["pair"] = df["product_a"] + "  +  " + df["product_b"]
df = df.sort_values("co_purchase_count")   # biggest bar ends up on top

fig = px.bar(df, x="co_purchase_count", y="pair", orientation="h",
             text="co_purchase_count",
             labels={"co_purchase_count": "Transactions containing both products",
                     "pair": ""},
             title="Product pairs most often bought in the same transaction")
fig.update_traces(marker_color="#3B6FB6", textposition="outside")
fig.update_layout(plot_bgcolor="white", xaxis=dict(dtick=1))

fig.show()
