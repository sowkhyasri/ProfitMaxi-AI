
from flask import Flask, render_template, request
import pandas as pd
import os

# Import all six agents
from agents.sales_agent import analyze_sales
from agents.profit_agent import calculate_profit
from agents.demand_agent import forecast_demand
from agents.inventory_agent import optimize_inventory
from agents.logistics_agent import optimize_logistics
from agents.advisor_agent import generate_business_advice

# Import database function
from database import save_upload

app = Flask(__name__)

# Upload configuration
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def clean_columns(df):
    """Clean and normalize dataset column names."""

    df.columns = (
        df.columns.astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    return df


@app.route("/")
def home():
    return render_template("dashboard.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    if "file" not in request.files:
        return "Error: No file uploaded"

    file = request.files["file"]

    if file.filename == "":
        return "Error: Please select a file"

    try:

        filename = file.filename.lower()

        # --------------------------------
        # 1. READ CSV OR EXCEL FILE
        # --------------------------------

        if filename.endswith(".csv"):

            try:
                df = pd.read_csv(
                    file,
                    encoding="utf-8-sig",
                    sep=","
                )

            except UnicodeDecodeError:
                file.stream.seek(0)

                df = pd.read_csv(
                    file,
                    encoding="latin1",
                    sep=","
                )

        elif filename.endswith((".xlsx", ".xls")):

            df = pd.read_excel(file)

        else:
            return "Error: Upload only CSV or Excel files"

        if df.empty:
            return "Error: Uploaded dataset is empty"

        # --------------------------------
        # 2. CLEAN COLUMN NAMES
        # --------------------------------

        df = clean_columns(df)

        print("\n========== UPLOAD DEBUG ==========")
        print("Uploaded file:", file.filename)
        print("Detected columns:", df.columns.tolist())
        print(df.head())
        print("==================================\n")

        # --------------------------------
        # 3. VALIDATE REQUIRED COLUMNS
        # --------------------------------

        required_columns = [
            "date",
            "product",
            "quantity",
            "selling_price",
            "purchase_cost",
            "retailer",
            "current_stock"
        ]

        missing_columns = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            return (
                "Missing columns: "
                + ", ".join(missing_columns)
                + ". Detected columns: "
                + ", ".join(df.columns.astype(str))
            )

        # --------------------------------
        # 4. VALIDATE TEXT DATA
        # --------------------------------

        df["product"] = df["product"].astype(str).str.strip()
        df["retailer"] = df["retailer"].astype(str).str.strip()

        if df["product"].isin(["", "nan", "None"]).any():
            return "Error: Product names cannot be empty"

        if df["retailer"].isin(["", "nan", "None"]).any():
            return "Error: Retailer names cannot be empty"

        # --------------------------------
        # 5. VALIDATE DATE
        # --------------------------------

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

        if df["date"].isna().any():
            return "Error: Invalid date values in dataset"

        # --------------------------------
        # 6. VALIDATE NUMERIC COLUMNS
        # --------------------------------

        numeric_columns = [
            "quantity",
            "selling_price",
            "purchase_cost",
            "current_stock"
        ]

        for col in numeric_columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

        if df[numeric_columns].isna().any().any():
            return "Error: Invalid numeric values in dataset"

        if (df[numeric_columns] < 0).any().any():
            return "Error: Negative values are not allowed"

        # --------------------------------
        # 7. VALIDATE LOGISTICS DATA
        # --------------------------------

        for col in ["distance_km", "delivery_cost"]:

            if col in df.columns:

                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

                if df[col].isna().any():
                    return f"Error: Invalid values in {col}"

                if (df[col] < 0).any():
                    return f"Error: Negative values in {col}"

        # --------------------------------
        # 8. EXECUTE AGENT 1 - SALES
        # --------------------------------

        print("Running Sales Agent...")

        sales_data = analyze_sales(df)

        # --------------------------------
        # 9. EXECUTE AGENT 2 - PROFIT
        # --------------------------------

        print("Running Profit Agent...")

        profit_data = calculate_profit(df)

        # --------------------------------
        # 10. EXECUTE AGENT 3 - DEMAND
        # --------------------------------

        print("Running Demand Forecasting Agent...")

        demand_forecasts = forecast_demand(df)

        # --------------------------------
        # 11. EXECUTE AGENT 4 - INVENTORY
        # --------------------------------

        print("Running Inventory Agent...")

        inventory_recommendations = optimize_inventory(
            df,
            demand_forecasts
        )

        # --------------------------------
        # 12. EXECUTE AGENT 5 - LOGISTICS
        # --------------------------------

        print("Running Logistics Agent...")

        logistics_data = optimize_logistics(df)

        # --------------------------------
        # 13. EXECUTE AGENT 6 - BUSINESS ADVISOR
        # --------------------------------

        print("Running Business Advisor Agent...")

        advisor_data = generate_business_advice(
            profit_data,
            demand_forecasts,
            inventory_recommendations,
            logistics_data
        )

        # --------------------------------
        # 14. SAVE SUMMARY TO DATABASE
        # --------------------------------

        save_upload(
            filename=file.filename,
            total_records=len(df),
            total_revenue=profit_data["total_revenue"],
            total_profit=profit_data["total_profit"]
        )

        print("\nAll six agents executed successfully.")
        print("Upload summary saved to SQLite database.")

        # --------------------------------
        # 15. DISPLAY RESULTS ON DASHBOARD
        # --------------------------------

        return render_template(
            "dashboard.html",

            revenue=profit_data["total_revenue"],
            profit=profit_data["total_profit"],
            purchase=profit_data["total_purchase"],
            margin=profit_data["average_margin"],

            quantity=int(df["quantity"].sum()),

            products=profit_data["products"],

            sales_data=sales_data,

            demand_forecasts=demand_forecasts,

            inventory_recommendations=inventory_recommendations,

            logistics_data=logistics_data,

            advisor_data=advisor_data
        )

    except Exception as error:

        app.logger.exception(
            "Error processing uploaded dataset"
        )

        return f"Error processing file: {str(error)}", 500


# --------------------------------
# RUN FLASK APPLICATION
# --------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )


