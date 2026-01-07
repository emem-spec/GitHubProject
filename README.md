# Financial Quantitative Analysis Dashboard

## Description
This project is a comprehensive financial dashboard built with **Python** and **Streamlit**. It is designed to simulate a professional quantitative research environment, enabling collaboration via Git and deployment on a Linux server.

The platform is divided into two distinct modules:
1.  **Quant A (Single Asset):** Focuses on technical analysis, backtesting trading strategies (Momentum, RSI), and risk metrics for individual assets.
2.  **Quant B (Portfolio):** Focuses on portfolio construction, diversification analysis, correlation matrices, and risk management (VaR, CVaR).

The project includes automated daily reporting via Linux cron jobs and is designed to be deployed on a cloud server.

## Features

### Module Quant A: Single Asset Analysis
* **Real-time Data:** Fetches live data using `yfinance`.
* **Backtesting Engine:**
    * **Buy & Hold:** Benchmark strategy.
    * **Momentum:** Moving Average Crossover (configurable windows).
    * **RSI:** Mean reversion strategy with overbought/oversold thresholds.
* **Performance Metrics:** Sharpe Ratio, Sortino Ratio, Max Drawdown, Annualized Return.
* **Visualizations:** Interactive charts with Buy/Sell signals, Drawdown analysis, and Rolling Sharpe Ratio.

### Module Quant B: Portfolio Management
* **Multi-Asset Simulation:** Construct portfolios with custom weights.
* **Risk Analysis:** Value at Risk (VaR), Conditional VaR (CVaR), Volatility analysis and other ratios
* **Diversification:** Correlation matrix heatmap and diversification benefit calculation.
* **Intraday Monitor:** Live tracking of portfolio performance over the last 24 hours.

### Automation & Linux
* **Daily Reports:** Automated script (`scripts/daily_reports.sh`) generates performance summaries at 8:00 PM.
* **Service Management:** Scripts to keep the application running 24/7.

## Project Structure

```text
├── config/
│   └── settings.py           # Global configuration (Assets, Constants)
├── data/
│   ├── __init__.py
│   └── fetcher.py            # Data retrieval logic
├── logs/                     # Application and Cron logs
├── reports/                  # Generated daily text reports
├── scripts/
│   ├── daily_reports.sh      # Bash script for Cron jobs
│   └── generate_report.py    # Python script for report generation
├── strategies/
│   ├── __init__.py
│   ├── base_strategy.py      # Abstract base class
│   ├── buy_hold.py           # Buy & Hold logic
│   └── momentum.py           # Momentum & RSI logic
├── utils/
│   ├── backtester.py         # Backtesting engine
│   └── metrics.py            # Financial calculations (Sharpe, Drawdown, etc.)
├── visualization/
│   └── charts.py             # Plotly charting functions
├── app.py                    # Main Streamlit application entry point
├── data_manager.py           # Data handling utilities
├── portfolio_analytics.py    # Specific logic for portfolio calculations
├── quant_a_module.py         # Main logic for Module A
├── quant_b_module.py         # Main logic for Module B
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
