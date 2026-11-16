
def generate_business_advice(
    profit_data,
    demand_forecasts,
    inventory_recommendations,
    logistics_data
):
    insights = []

    # 1. Profit analysis
    total_revenue = profit_data.get("total_revenue", 0)
    total_profit = profit_data.get("total_profit", 0)
    average_margin = profit_data.get("average_margin", 0)

    if total_revenue > 0:
        insights.append(
            f"Your total revenue is Rs. {total_revenue:,.2f} "
            f"and gross profit is Rs. {total_profit:,.2f}."
        )

    if average_margin < 10:
        insights.append(
            "Your average gross profit margin is below 10%. "
            "Review purchase costs, selling prices and discounts."
        )
    else:
        insights.append(
            f"Your average gross profit margin is {average_margin:.2f}%."
        )

    # 2. Identify the most profitable product
    products = profit_data.get("products", [])

    if products:
        best_product = max(
            products,
            key=lambda item: item.get("gross_profit", 0)
        )

        insights.append(
            f"{best_product.get('product')} is your highest "
            f"gross-profit contributor with Rs. "
            f"{best_product.get('gross_profit', 0):,.2f} gross profit."
        )

    # 3. Demand analysis
    if demand_forecasts:
        highest_demand = max(
            demand_forecasts,
            key=lambda item: item.get("forecast_demand", 0)
        )

        insights.append(
            f"{highest_demand.get('product')} has the highest "
            f"forecast demand of "
            f"{highest_demand.get('forecast_demand', 0)} units."
        )

    # 4. Inventory recommendations
    reorder_items = [
        item for item in inventory_recommendations
        if item.get("reorder_quantity", 0) > 0
    ]

    if reorder_items:
        insights.append(
            f"{len(reorder_items)} product(s) require replenishment. "
            "Review the recommended reorder quantities before purchasing."
        )
    else:
        insights.append(
            "Current stock is sufficient for the forecast demand "
            "according to the inventory calculation."
        )

    # 5. Logistics analysis
    if logistics_data.get("status") == "success":
        total_distance = logistics_data.get("total_distance", 0)
        total_delivery_cost = logistics_data.get(
            "total_delivery_cost", 0
        )

        insights.append(
            f"Recorded delivery distance is {total_distance} km "
            f"and recorded delivery cost is Rs. "
            f"{total_delivery_cost:,.2f}."
        )

        deliveries = logistics_data.get("deliveries", [])

        long_distance = [
            item for item in deliveries
            if item.get("average_distance", 0) > 20
        ]

        if long_distance:
            names = ", ".join(
                item["retailer"] for item in long_distance
            )

            insights.append(
                f"Review delivery routes for: {names}."
            )
        else:
            insights.append(
                "No retailer exceeds the 20 km average-distance "
                "review threshold."
            )

    else:
        insights.append(
            "Logistics recommendations are limited because "
            "distance data is unavailable."
        )

    return {
        "status": "success",
        "total_insights": len(insights),
        "insights": insights
    }
