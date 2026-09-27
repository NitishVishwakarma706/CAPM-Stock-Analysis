import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import ta
import yfinance as yf
from pages.utils.plotly_figure import (
    MACD,
    RSI,
    Moving_average,
    candlestic,
    close_chart,
    plotly_table,
)

st.set_page_config(page_title="Stock Analysis", page_icon="page_with_curl", layout="wide")

st.title("📈 Stock Analysis Dashboard")

col1, col2, col3 = st.columns(3)
today = datetime.date.today()

with col1:
    tickers = st.multiselect(
        "Choose stock(s) you want to analyze",
        [
            "AAPL", "TSLA", "NFLX", "MSFT", "AMZN", "GOOGL", "META", "NVDA", 
            "JPM", "V", "MA", "DIS", "PYPL", "ADBE", "CRM", "INTC", "CSCO", 
            "ORCL", "IBM", "QCOM", "TXN", "ASML", "NET", "BRK.B", "WMT", 
            "COST", "HD", "PG", "LLY", "UNH", "JNJ", "ABBV", "MRK", "BAC", 
            "GS", "XOM", "CVX"
        ],
        default=["TSLA"],
    )
with col2:
    start_date = st.date_input(
        "Choose Start Date", datetime.date(today.year - 1, today.month, today.day)
    )
with col3:
    end_date = st.date_input(
        "Choose End Date", datetime.date(today.year, today.month, today.day)
    )

if "num_period" not in st.session_state:
    st.session_state.num_period = "1y"

for ticker in tickers:
    st.markdown(f"## 🏢 Financial Profile: **{ticker}**")

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        st.write(f"**Sector:** {info.get('sector', 'N/A')}")
        st.write(
            f"**Full Time Employees:** {info.get('fullTimeEmployees', 'N/A'):,}"
            if isinstance(info.get('fullTimeEmployees'), int)
            else f"**Full Time Employees:** {info.get('fullTimeEmployees', 'N/A')}"
        )
        st.write(f"**Website:** {info.get('website', 'N/A')}")
        with st.expander(f"Click to read Business Summary for {ticker}"):
            st.write(info.get("longBusinessSummary", "No description available."))

        layout_col1, layout_col2 = st.columns(2)

        with layout_col1:
            st.markdown("### Valuation & Risk Metrics")
            metrics_data = [
                info.get("marketCap", "N/A"),
                info.get("beta", "N/A"),
                info.get("trailingEps", "N/A"),
                info.get("trailingPE", "N/A"),
            ]

            df_metrics = pd.DataFrame(
                metrics_data,
                index=["Market Cap", "Beta", "EPS", "PE Ratio"],
                columns=["Value"],
            )

            if isinstance(df_metrics.loc["Market Cap", "Value"], (int, float)):
                df_metrics.loc["Market Cap", "Value"] = (
                    f"{df_metrics.loc['Market Cap', 'Value']:,}"
                )

            fig_metrics = plotly_table(df_metrics)
            st.plotly_chart(fig_metrics, use_container_width=True)

        with layout_col2:
            st.markdown("### Corporate Balance Sheet Ratios")
            ratio_data = [
                info.get("quickRatio", "N/A"),
                info.get("revenuePerShare", "N/A"),
                info.get("profitMargins", "N/A"),
                info.get("debtToEquity", "N/A"),
                info.get("returnOnEquity", "N/A"),
            ]

            df_ratios = pd.DataFrame(
                ratio_data,
                index=[
                    "Quick Ratio",
                    "Revenue per share",
                    "Profit Margins",
                    "Debt to Equity",
                    "Return on Equity",
                ],
                columns=["Value"],
            )

            fig_ratios = plotly_table(df_ratios)
            st.plotly_chart(fig_ratios, use_container_width=True)

        data = yf.download(ticker, start=start_date, end=end_date)

        if not data.empty and len(data) >= 2:
            metric_col1, metric_col2, metric_col3 = st.columns(3)

            if isinstance(data.columns, pd.MultiIndex):
                close_series = data["Close"][ticker] if ticker in data["Close"] else data["Close"].iloc[:, 0]
            else:
                close_series = data["Close"]

            current_close = float(close_series.iloc[-1])
            previous_close = float(close_series.iloc[-2])
            daily_change = current_close - previous_close

            with metric_col1:
                st.metric(
                    label=f"{ticker} Latest Close Price",
                    value=f"${current_close:.2f}",
                    delta=f"{daily_change:.2f}",
                )

            st.write("#### Historical Price Log Data (Last 10 Days)")
            last_10_df = data.tail(10).sort_index(ascending=False).round(3)

            if isinstance(last_10_df.columns, pd.MultiIndex):
                last_10_df.columns = last_10_df.columns.get_level_values(0)

            fig_hist = plotly_table(last_10_df.reset_index())
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.warning(
                f"Insufficient historical context range data returned for {ticker} across chosen boundaries."
            )

        st.markdown("### 📊 Interactive Technical Indicator Charts")

        periods_map = {
            "5D": "5d",
            "1M": "1mo",
            "6M": "6mo",
            "YTD": "ytd",
            "1Y": "1y",
            "5Y": "5y",
            "MAX": "max",
        }

        btn_cols = st.columns(len(periods_map))
        for idx, (label, value) in enumerate(periods_map.items()):
            with btn_cols[idx]:
                if st.button(label, key=f"btn_{ticker}_{label}"):
                    st.session_state.num_period = value

        config_col1, config_col2, config_col3 = st.columns([2, 2, 4])
        with config_col1:
            chart_type = st.selectbox(
                "Select Main Visualization",
                ("Candle", "Line"),
                key=f"chart_type_{ticker}",
            )
        with config_col2:
            if chart_type == "Candle":
                indicators = st.selectbox(
                    "Apply Overlay Indicator",
                    ("RSI", "MACD"),
                    key=f"indicator_{ticker}",
                )
            else:
                indicators = st.selectbox(
                    "Apply Overlay Indicator",
                    ("RSI", "Moving Average", "MACD"),
                    key=f"indicator_{ticker}",
                )

        max_history_data = stock.history(period="max")
        active_period = st.session_state.num_period

        if chart_type == "Candle":
            st.plotly_chart(
                candlestic(max_history_data, active_period), use_container_width=True
            )
            if indicators == "RSI":
                st.plotly_chart(
                    RSI(max_history_data, active_period), use_container_width=True
                )
            elif indicators == "MACD":
                st.plotly_chart(
                    MACD(max_history_data, active_period), use_container_width=True
                )

        elif chart_type == "Line":
            if indicators == "Moving Average":
                st.plotly_chart(
                    Moving_average(max_history_data, active_period),
                    use_container_width=True,
                )
            else:
                st.plotly_chart(
                    close_chart(max_history_data, active_period),
                    use_container_width=True,
                )
                if indicators == "RSI":
                    st.plotly_chart(
                        RSI(max_history_data, active_period), use_container_width=True
                    )
                elif indicators == "MACD":
                    st.plotly_chart(
                        MACD(max_history_data, active_period), use_container_width=True
                    )

    except Exception as general_err:
        st.error(
            f"Unable to cleanly construct dashboard profile views for asset **{ticker}**. Detail log: {general_err}"
        )

    st.divider()
