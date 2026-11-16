
import pandas as pd


def optimize_logistics(df):

    data = df.copy()

    data.columns = (
        data.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    required_columns = ["retailer"]

    for column in required_columns:
        if column not in data.columns:
            raise ValueError(f"Missing column: {column}")

    data["retailer"] = data["retailer"].astype(str).str.strip()

    if "distance_km" not in data.columns:
        return {
            "status": "Distance data unavailable",
            "message": (
                "Add a distance_km column to analyze delivery distances."
            ),
            "total_distance": 0,
            "total_delivery_cost": 0,
            "deliveries": []
        }

    data["distance_km"] = pd.to_numeric(
        data["distance_km"], errors="coerce"
    )

    if data["distance_km"].isna().any():
        raise ValueError("Invalid distance_km values.")

    if (data["distance_km"] < 0).any():
        raise ValueError("Distance cannot be negative.")

    if "delivery_cost" in data.columns:
        data["delivery_cost"] = pd.to_numeric(
            data["delivery_cost"], errors="coerce"
        )

        if data["delivery_cost"].isna().any():
            raise ValueError("Invalid delivery_cost values.")

        if (data["delivery_cost"] < 0).any():
            raise ValueError("Delivery cost cannot be negative.")
    else:
        data["delivery_cost"] = 0

    retailer_summary = (
        data.groupby("retailer", as_index=False)
        .agg(
            total_distance=("distance_km", "sum"),
            total_delivery_cost=("delivery_cost", "sum"),
            delivery_count=("retailer", "count")
        )
    )

    retailer_summary["average_distance"] = (
        retailer_summary["total_distance"]
        / retailer_summary["delivery_count"]
    )

    retailer_summary["recommendation"] = retailer_summary[
        "average_distance"
    ].apply(
        lambda distance:
            "Review delivery route" if distance > 20
            else "Delivery distance acceptable"
    )

    return {
        "status": "success",
        "total_distance": round(
            data["distance_km"].sum(), 2
        ),
        "total_delivery_cost": round(
            data["delivery_cost"].sum(), 2
        ),
        "deliveries": retailer_summary.round(2).to_dict(
            orient="records"
        )
    }
