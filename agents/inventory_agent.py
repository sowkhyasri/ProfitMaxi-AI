
import pandas as pd
import math


def optimize_inventory(df, demand_forecasts):

    data = df.copy()

    # Clean column names
    data.columns = (
        data.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Validate required columns
    required = ["product", "current_stock"]

    for column in required:
        if column not in data.columns:
            raise ValueError(f"Missing column: {column}")

    # Normalize product names
    data["product"] = data["product"].astype(str).str.strip()

    # Convert stock values
    data["current_stock"] = pd.to_numeric(
        data["current_stock"],
        errors="coerce"
    )

    if data["current_stock"].isna().any():
        raise ValueError("Invalid current_stock values.")

    if (data["current_stock"] < 0).any():
        raise ValueError("Current stock cannot be negative.")

    # Get latest stock record for each product
    if "date" in data.columns:

        data["date"] = pd.to_datetime(
            data["date"],
            errors="coerce"
        )

        if data["date"].isna().any():
            raise ValueError("Invalid date values in stock data.")

        latest_stock = (
            data.sort_values("date")
            .groupby("product")
            .tail(1)
        )

    else:

        latest_stock = data.groupby("product").tail(1)

    stock_lookup = dict(zip(
        latest_stock["product"],
        latest_stock["current_stock"]
    ))

    recommendations = []

    # Process demand forecasts
    for item in demand_forecasts:

        product = str(item["product"]).strip()

        forecast = pd.to_numeric(
            item["forecast_demand"],
            errors="coerce"
        )

        if pd.isna(forecast) or forecast < 0:
            raise ValueError(
                f"Invalid demand forecast for {product}"
            )

        forecast = math.ceil(forecast)

        if product not in stock_lookup:
            continue

        current_stock = int(stock_lookup[product])

        # Calculate 20% safety stock
        safety_stock = math.ceil(forecast * 0.20)

        # Calculate reorder quantity
        reorder_quantity = max(
            0,
            forecast + safety_stock - current_stock
        )

        # Generate recommendation
        if reorder_quantity > 0:
            status = "Reorder Required"
        else:
            status = "Stock Sufficient"

        recommendations.append({

            "product": product,

            "current_stock": current_stock,

            "forecast_demand": forecast,

            "safety_stock": safety_stock,

            "reorder_quantity": reorder_quantity,

            "status": status

        })

    return recommendations
