
document.addEventListener("DOMContentLoaded", function () {

    // Read chart data from dashboard HTML
    const chartDataElement = document.getElementById("chart-data");

    if (!chartDataElement) {
        return;
    }

    const chartData = JSON.parse(chartDataElement.textContent);

    const products = chartData.products || [];
    const demand = chartData.demand || [];
    const inventory = chartData.inventory || [];
    const logistics = chartData.logistics || [];

    // Reusable chart configuration
    function createChart(canvasId, type, labels, datasets, title) {

        const canvas = document.getElementById(canvasId);

        if (!canvas) {
            return;
        }

        new Chart(canvas, {
            type: type,

            data: {
                labels: labels,
                datasets: datasets
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: true,
                        position: "bottom"
                    },

                    title: {
                        display: true,
                        text: title
                    }
                },

                scales: type === "pie" || type === "doughnut"
                    ? {}
                    : {
                        y: {
                            beginAtZero: true
                        }
                    }
            }
        });
    }

    // 1. Product-wise Sales Quantity
    createChart(
        "salesChart",
        "bar",
        products.map(p => p.product),
        [{
            label: "Units Sold",
            data: products.map(p => p.quantity),
            backgroundColor: "#3B82F6"
        }],
        "Product-wise Sales Quantity"
    );

    // 2. Product-wise Revenue
    createChart(
        "revenueChart",
        "bar",
        products.map(p => p.product),
        [{
            label: "Revenue (₹)",
            data: products.map(p => p.revenue),
            backgroundColor: "#10B981"
        }],
        "Product-wise Revenue"
    );

    // 3. Product-wise Gross Profit
    createChart(
        "profitChart",
        "doughnut",
        products.map(p => p.product),
        [{
            label: "Gross Profit",
            data: products.map(p => p.gross_profit)
        }],
        "Product-wise Gross Profit"
    );

    // 4. Demand Forecast
    createChart(
        "demandChart",
        "bar",
        demand.map(p => p.product),
        [{
            label: "Forecast Demand",
            data: demand.map(p => p.forecast_demand),
            backgroundColor: "#8B5CF6"
        }],
        "Product Demand Forecast"
    );

    // 5. Inventory Analysis
    createChart(
        "inventoryChart",
        "bar",
        inventory.map(p => p.product),
        [
            {
                label: "Current Stock",
                data: inventory.map(p => p.current_stock),
                backgroundColor: "#0EA5E9"
            },
            {
                label: "Reorder Quantity",
                data: inventory.map(p => p.reorder_quantity),
                backgroundColor: "#F59E0B"
            }
        ],
        "Inventory Stock vs Reorder"
    );

    // 6. Retailer-wise Delivery Distance
    createChart(
        "logisticsChart",
        "bar",
        logistics.map(p => p.retailer),
        [{
            label: "Total Distance (km)",
            data: logistics.map(p => p.total_distance),
            backgroundColor: "#F97316"
        }],
        "Retailer-wise Delivery Distance"
    );

});
