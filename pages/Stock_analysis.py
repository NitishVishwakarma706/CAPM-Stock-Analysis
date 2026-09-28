import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

from pages.utils.plotly_figure import (
    MACD,
    RSI,
    Moving_average,
    candlestic,
    close_chart,
    plotly_table,
)


st.set_page_config(
    page_title="Stock Analysis",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Stock Analysis Dashboard")

def safe_value(value, default="N/A"):
    """
    Return a safe value for missing/NaN data.
    """
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
        pass

    return value


def format_number(value, decimals=2):
    """
    Format numeric values safely.
    """
    value = safe_value(value)

    if value == "N/A":
        return "N/A"

    try:
        return f"{float(value):,.{decimals}f}"
    except (ValueError, TypeError):
        return "N/A"


def format_integer(value):
    """
    Format large integer values such as Market Cap.
    """
    value = safe_value(value)

    if value == "N/A":
        return "N/A"

    try:
        return f"{float(value):,.0f}"
    except (ValueError, TypeError):
        return "N/A"


def format_percentage(value):
    """
    Convert decimal percentage to percentage display.

    Example:
    0.25 -> 25.00%
    """
    value = safe_value(value)

    if value == "N/A":
        return "N/A"

    try:
        return f"{float(value):.2%}"
    except (ValueError, TypeError):
        return "N/A"


def get_close_series(data, ticker):
    """
    Safely extract Close price series from yfinance data.
    Handles both normal and MultiIndex DataFrames.
    """

    if data is None or data.empty:
        return None

    try:
        if isinstance(data.columns, pd.MultiIndex):

            # Case: Close -> ticker
            if "Close" in data.columns.get_level_values(0):

                close_data = data["Close"]

                if isinstance(close_data, pd.DataFrame):

                    if ticker in close_data.columns:
                        return close_data[ticker]

                    return close_data.iloc[:, 0]

                return close_data

        else:

            if "Close" in data.columns:
                return data["Close"]

    except Exception:
        pass

    return None


col1, col2, col3 = st.columns(3)

today = datetime.date.today()


with col1:

    tickers = st.multiselect(
        "Choose stock(s) you want to analyze",
        [
            "AAPL",
            "TSLA",
            "NFLX",
            "MSFT",
            "AMZN",
            "GOOGL",
            "META",
            "NVDA",
            "JPM",
            "V",
            "MA",
            "DIS",
            "PYPL",
            "ADBE",
            "CRM",
            "INTC",
            "CSCO",
            "ORCL",
            "IBM",
            "QCOM",
            "TXN",
            "ASML",
            "NET",
            "BRK.B",
            "WMT",
            "COST",
            "HD",
            "PG",
            "LLY",
            "UNH",
            "JNJ",
            "ABBV",
            "MRK",
            "BAC",
            "GS",
            "XOM",
            "CVX",
        ],
        default=["TSLA"],
    )


with col2:

    start_date = st.date_input(
        "Choose Start Date",
        datetime.date(
            today.year - 1,
            today.month,
            today.day
        )
    )


with col3:

    end_date = st.date_input(
        "Choose End Date",
        datetime.date(
            today.year,
            today.month,
            today.day
        )
    )


if start_date >= end_date:

    st.error(
        "Start Date must be earlier than End Date."
    )

    st.stop()


if "num_period" not in st.session_state:

    st.session_state.num_period = "1y"

for ticker in tickers:

    st.markdown(
        f"## 🏢 Financial Profile: **{ticker}**"
    )

    try:

        stock = yf.Ticker(ticker)

        info = stock.info


        sector = safe_value(
            info.get("sector")
        )

        employees = safe_value(
            info.get("fullTimeEmployees")
        )

        website = safe_value(
            info.get("website")
        )

        business_summary = safe_value(
            info.get(
                "longBusinessSummary"
            ),
            "No description available."
        )


        st.write(
            f"**Sector:** {sector}"
        )


        # Employee formatting
        if employees != "N/A":

            try:

                employees_display = (
                    f"{int(employees):,}"
                )

            except (
                ValueError,
                TypeError
            ):

                employees_display = str(
                    employees
                )

        else:

            employees_display = "N/A"


        st.write(
            f"**Full Time Employees:** "
            f"{employees_display}"
        )


        st.write(
            f"**Website:** {website}"
        )

        with st.expander(
            f"Click to read Business Summary for {ticker}"
        ):

            st.write(
                business_summary
            )

        layout_col1, layout_col2 = st.columns(2)


        with layout_col1:

            st.markdown(
                "### Valuation & Risk Metrics"
            )


            # Raw numeric values
            market_cap = info.get(
                "marketCap"
            )

            beta = info.get(
                "beta"
            )

            eps = info.get(
                "trailingEps"
            )

            pe_ratio = info.get(
                "trailingPE"
            )

            metrics_data = {

                "Value": [

                    format_integer(
                        market_cap
                    ),

                    format_number(
                        beta,
                        2
                    ),

                    format_number(
                        eps,
                        2
                    ),

                    format_number(
                        pe_ratio,
                        2
                    ),
                ]
            }


            df_metrics = pd.DataFrame(

                metrics_data,

                index=[
                    "Market Cap",
                    "Beta",
                    "EPS",
                    "PE Ratio",
                ]
            )


            fig_metrics = plotly_table(
                df_metrics
            )


            st.plotly_chart(
                fig_metrics,
                use_container_width=True
            )


        with layout_col2:

            st.markdown(
                "### Corporate Balance Sheet Ratios"
            )


            quick_ratio = info.get(
                "quickRatio"
            )

            revenue_per_share = info.get(
                "revenuePerShare"
            )

            profit_margins = info.get(
                "profitMargins"
            )

            debt_to_equity = info.get(
                "debtToEquity"
            )

            return_on_equity = info.get(
                "returnOnEquity"
            )


            ratio_data = {

                "Value": [

                    format_number(
                        quick_ratio,
                        2
                    ),

                    format_number(
                        revenue_per_share,
                        2
                    ),

                    format_percentage(
                        profit_margins
                    ),

                    format_number(
                        debt_to_equity,
                        2
                    ),

                    format_percentage(
                        return_on_equity
                    ),
                ]
            }


            df_ratios = pd.DataFrame(

                ratio_data,

                index=[
                    "Quick Ratio",
                    "Revenue per Share",
                    "Profit Margins",
                    "Debt to Equity",
                    "Return on Equity",
                ]
            )


            fig_ratios = plotly_table(
                df_ratios
            )


            st.plotly_chart(
                fig_ratios,
                use_container_width=True
            )

        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            progress=False
        )


        if (
            data is not None
            and not data.empty
            and len(data) >= 2
        ):

            metric_col1, metric_col2, metric_col3 = (
                st.columns(3)
            )



            close_series = get_close_series(
                data,
                ticker
            )


            if (
                close_series is not None
                and len(close_series) >= 2
            ):

                # Remove missing values
                close_series = (
                    close_series
                    .dropna()
                )


                if len(close_series) >= 2:

                    current_close = float(
                        close_series.iloc[-1]
                    )

                    previous_close = float(
                        close_series.iloc[-2]
                    )


                    daily_change = (
                        current_close
                        - previous_close
                    )


                    with metric_col1:

                        st.metric(
                            label=(
                                f"{ticker} "
                                "Latest Close Price"
                            ),

                            value=(
                                f"${current_close:.2f}"
                            ),

                            delta=(
                                f"{daily_change:.2f}"
                            )
                        )

            st.write(
                "#### Historical Price Log Data "
                "(Last 10 Days)"
            )


            last_10_df = (
                data
                .tail(10)
                .sort_index(
                    ascending=False
                )
                .round(3)
            )


            # Flatten MultiIndex columns
            if isinstance(
                last_10_df.columns,
                pd.MultiIndex
            ):

                last_10_df.columns = (
                    last_10_df
                    .columns
                    .get_level_values(0)
                )


            # Reset index
            last_10_df = (
                last_10_df
                .reset_index()
            )


            fig_hist = plotly_table(
                last_10_df
            )


            st.plotly_chart(
                fig_hist,
                use_container_width=True
            )


        else:

            st.warning(
                f"Insufficient historical "
                f"data returned for {ticker} "
                f"across the chosen dates."
            )

        st.markdown(
            "### 📊 Interactive Technical Indicator Charts"
        )


        periods_map = {
            "5D": "5d",
            "1M": "1mo",
            "6M": "6mo",
            "YTD": "ytd",
            "1Y": "1y",
            "5Y": "5y",
            "MAX": "max",
        }



        btn_cols = st.columns(
            len(periods_map)
        )


        for idx, (
            label,
            value
        ) in enumerate(
            periods_map.items()
        ):

            with btn_cols[idx]:

                if st.button(
                    label,
                    key=f"btn_{ticker}_{label}"
                ):

                    st.session_state.num_period = (
                        value
                    )



        config_col1, config_col2, config_col3 = (
            st.columns([2, 2, 4])
        )


        with config_col1:

            chart_type = st.selectbox(

                "Select Main Visualization",

                (
                    "Candle",
                    "Line"
                ),

                key=f"chart_type_{ticker}"
            )



        with config_col2:

            if chart_type == "Candle":

                indicators = st.selectbox(

                    "Apply Overlay Indicator",

                    (
                        "RSI",
                        "MACD"
                    ),

                    key=f"indicator_{ticker}"
                )

            else:

                indicators = st.selectbox(

                    "Apply Overlay Indicator",

                    (
                        "RSI",
                        "Moving Average",
                        "MACD"
                    ),

                    key=f"indicator_{ticker}"
                )



        max_history_data = stock.history(
            period="max"
        )


        if (
            max_history_data is None
            or max_history_data.empty
        ):

            st.warning(
                f"No technical analysis "
                f"history available for {ticker}."
            )

            continue


        active_period = (
            st.session_state.num_period
        )

        if chart_type == "Candle":

            try:

                st.plotly_chart(

                    candlestic(
                        max_history_data,
                        active_period
                    ),

                    use_container_width=True
                )

            except Exception as chart_error:

                st.error(
                    f"Candlestick chart error: "
                    f"{chart_error}"
                )



            if indicators == "RSI":

                try:

                    st.plotly_chart(

                        RSI(
                            max_history_data,
                            active_period
                        ),

                        use_container_width=True
                    )

                except Exception as chart_error:

                    st.error(
                        f"RSI chart error: "
                        f"{chart_error}"
                    )



            elif indicators == "MACD":

                try:

                    st.plotly_chart(

                        MACD(
                            max_history_data,
                            active_period
                        ),

                        use_container_width=True
                    )

                except Exception as chart_error:

                    st.error(
                        f"MACD chart error: "
                        f"{chart_error}"
                    )


        elif chart_type == "Line":


            if indicators == "Moving Average":

                try:

                    st.plotly_chart(

                        Moving_average(
                            max_history_data,
                            active_period
                        ),

                        use_container_width=True
                    )

                except Exception as chart_error:

                    st.error(
                        f"Moving Average chart error: "
                        f"{chart_error}"
                    )



            else:

                try:

                    st.plotly_chart(

                        close_chart(
                            max_history_data,
                            active_period
                        ),

                        use_container_width=True
                    )

                except Exception as chart_error:

                    st.error(
                        f"Close chart error: "
                        f"{chart_error}"
                    )



                if indicators == "RSI":

                    try:

                        st.plotly_chart(

                            RSI(
                                max_history_data,
                                active_period
                            ),

                            use_container_width=True
                        )

                    except Exception as chart_error:

                        st.error(
                            f"RSI chart error: "
                            f"{chart_error}"
                        )


                elif indicators == "MACD":

                    try:
                        st.plotly_chart(
                            MACD(
                                max_history_data,
                                active_period
                            ),
                            use_container_width=True
                        )
                    except Exception as chart_error:
                        st.error(
                            f"MACD chart error: "
                            f"{chart_error}"
                        )
    except Exception as general_err:

        st.error(
            f"Unable to cleanly construct dashboard "
            f"profile views for asset **{ticker}**. "
            f"Detail log: {general_err}"
        )


    st.divider()