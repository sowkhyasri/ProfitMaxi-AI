
import pandas as pd


def forecast_demand(df):

    # Create a copy to avoid modifying original data
    data = df.copy()

    # Clean column names
    data.columns = (
        data.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Validate required columns
    required_columns = ["date", "product", "quantity"]

    for column in required_columns:
        if column not in data.columns:
            raise ValueError(
                f"Missing column: {column}. "
                f"Available columns: {list(data.columns)}"
            )

    # Convert date and quantity
    data["date"] = pd.to_datetime(
        data["date"], errors="coerce"
    )

    data["quantity"] = pd.to_numeric(
        data["quantity"], errors="coerce"
    )

    # Remove invalid records
    data = data.dropna(
        subset=["date", "product", "quantity"]
    )

    if data.empty:
        raise ValueError("No valid sales records available.")

    if (data["quantity"] < 0).any():
        raise ValueError("Sales quantity cannot be negative.")

    # Group sales into weekly periods
    data["week"] = (
        data["date"]
        .dt.to_period("W")
        .apply(lambda period: period.start_time)
    )

    weekly_sales = (
        data.groupby(["product", "week"])["quantity"]
        .sum()
        .reset_index()
        .sort_values("week")
    )

    forecasts = []

    # Forecast demand product by product
    for product in weekly_sales["product"].unique():

        product_data = weekly_sales[
            weekly_sales["product"] == product
        ].sort_values("week")

        # Consider the latest three available weeks
        recent_weeks = product_data.tail(3)

        # Calculate average demand
        predicted_demand = recent_weeks["quantity"].mean()

        # Latest recorded weekly sales
        last_week_sales = int(
            product_data.iloc[-1]["quantity"]
        )

        # Forecast next week
        last_week = product_data["week"].max()

        forecast_week = (
            last_week + pd.Timedelta(days=7)
        ).strftime("%d %b %Y")

        forecasts.append({

            "product": product,

            "last_week_sales": last_week_sales,

            "forecast_demand": round(predicted_demand),

            "forecast_week": forecast_week

        })

    return forecasts


    # Continue with your existing forecasting code below