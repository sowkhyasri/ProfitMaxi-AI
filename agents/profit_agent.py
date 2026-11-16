
def calculate_profit(df):
    df = df.copy()

    df["revenue"] = df["quantity"] * df["selling_price"]

    df["purchase_amount"] = (
        df["quantity"] * df["purchase_cost"]
    )

    df["gross_profit"] = (
        df["revenue"] - df["purchase_amount"]
    )

    df["gross_margin"] = (
        df["gross_profit"] /
        df["revenue"].replace(0, 1)
    ) * 100

    product_profit = df.groupby(
        "product", as_index=False
    ).agg(
        quantity=("quantity", "sum"),
        revenue=("revenue", "sum"),
        purchase_amount=("purchase_amount", "sum"),
        gross_profit=("gross_profit", "sum")
    )

    product_profit["gross_margin"] = (
        product_profit["gross_profit"] /
        product_profit["revenue"].replace(0, 1)
    ) * 100

    return {
        "total_revenue": round(df["revenue"].sum(), 2),
        "total_purchase": round(df["purchase_amount"].sum(), 2),
        "total_profit": round(df["gross_profit"].sum(), 2),
        "average_margin": round(
            df["gross_profit"].sum() /
            max(df["revenue"].sum(), 1) * 100, 2
        ),
        "products": product_profit.round(2).to_dict(
            orient="records"
        )
    }
