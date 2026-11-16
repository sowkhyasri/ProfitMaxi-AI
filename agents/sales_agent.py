
import pandas as pd

def analyze_sales(df):
    required_columns = [
        "product",
        "quantity",
        "selling_price",
        "purchase_cost",
        "retailer"
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing column: {column}")

    df = df.copy()

    for column in ["quantity", "selling_price", "purchase_cost"]:
        df[column] = pd.to_numeric(df[column], errors="raise")

    if (df[["quantity", "selling_price", "purchase_cost"]] < 0).any().any():
        raise ValueError("Negative values are not allowed.")

    df["revenue"] = df["quantity"] * df["selling_price"]

    df["gross_profit"] = (
        df["quantity"] *
        (df["selling_price"] - df["purchase_cost"])
    )

    result = df.groupby("product", as_index=False).agg(
        quantity_sold=("quantity", "sum"),
        revenue=("revenue", "sum"),
        gross_profit=("gross_profit", "sum")
    )

    return result.sort_values(
        by="quantity_sold",
        ascending=False
    )
