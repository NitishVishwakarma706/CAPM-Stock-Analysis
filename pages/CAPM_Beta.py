import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go


st.set_page_config(
    page_title="CAPM Trading App",
    page_icon="📈",
    layout="wide"
)

stocks = {
    "AAPL": "Apple",
    "TSLA": "Tesla",
    "NFLX": "Netflix",
    "MGM": "MGM Resorts",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "NVDA": "NVIDIA",
    "GOOGL": "Google"
}


@st.cache_data
def get_stock_data(ticker, years):

    period = f"{years}y"

    stock = yf.download(
        ticker,
        period=period,
        auto_adjust=True,
        progress=False
    )

    market = yf.download(
        "^GSPC",
        period=period,
        auto_adjust=True,
        progress=False
    )

    return stock, market


def calculate_capm(stock, market):

    stock_price = stock["Close"]
    market_price = market["Close"]

    if isinstance(stock_price, pd.DataFrame):
        stock_price = stock_price.iloc[:, 0]

    if isinstance(market_price, pd.DataFrame):
        market_price = market_price.iloc[:, 0]

    stock_returns = stock_price.pct_change().dropna()
    market_returns = market_price.pct_change().dropna()

    data = pd.concat(
        [stock_returns, market_returns],
        axis=1
    )

    data.columns = ["Stock_Return", "Market_Return"]

    data = data.dropna()

    beta = (
        data["Stock_Return"].cov(data["Market_Return"])
        / data["Market_Return"].var()
    )

    stock_annual_return = data["Stock_Return"].mean() * 252
    market_annual_return = data["Market_Return"].mean() * 252

    risk_free_rate = 0.05

    expected_return = (
        risk_free_rate
        + beta * (market_annual_return - risk_free_rate)
    )

    return (
        beta,
        expected_return,
        stock_annual_return,
        market_annual_return,
        data
    )


with st.sidebar:

    st.title("Trading App")

    page = st.radio(
        "Navigation",
        [
            "CAPM Beta",
            "CAPM Return",
            "Stock Analysis",
            "Stock Prediction"
        ]
    )


if page == "CAPM Beta":

    st.title("Calculate Beta and Return for Individual Stock")

    col1, col2 = st.columns(2)

    with col1:

        selected_stock = st.selectbox(
            "Choose a stock",
            list(stocks.keys())
        )

    with col2:

        years = st.number_input(
            "Number of Years",
            min_value=1,
            max_value=10,
            value=1,
            step=1
        )

    with st.spinner("Downloading stock data..."):

        stock_data, market_data = get_stock_data(
            selected_stock,
            years
        )

    if stock_data.empty or market_data.empty:

        st.error("Unable to download stock data.")

    else:

        (
            beta,
            expected_return,
            stock_return,
            market_return,
            data
        ) = calculate_capm(
            stock_data,
            market_data
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Beta",
                f"{beta:.4f}"
            )

        with col2:
            st.metric(
                "CAPM Expected Return",
                f"{expected_return * 100:.2f}%"
            )

        with col3:
            st.metric(
                "Annual Stock Return",
                f"{stock_return * 100:.2f}%"
            )

        st.divider()


        x = data["Market_Return"] * 100
        y = data["Stock_Return"] * 100

        slope, intercept = np.polyfit(x, y, 1)

        regression_x = np.linspace(
            x.min(),
            x.max(),
            100
        )

        regression_y = (
            slope * regression_x
            + intercept
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="markers",
                name=selected_stock,
                marker=dict(
                    size=6,
                    opacity=0.65
                )
            )
        )

        fig.add_trace(
            go.Scatter(
                x=regression_x,
                y=regression_y,
                mode="lines",
                name="Expected Return",
                line=dict(
                    width=2
                )
            )
        )

        fig.update_layout(
            title=f"{selected_stock} vs S&P 500",
            xaxis_title="Market Return (%)",
            yaxis_title=f"{selected_stock} Return (%)",
            template="plotly_white",
            height=550,
            hovermode="closest"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


elif page == "CAPM Return":

    st.title("CAPM Return Calculator")

    risk_free = st.number_input(
        "Risk Free Rate (%)",
        min_value=0.0,
        max_value=20.0,
        value=5.0
    )

    market_return = st.number_input(
        "Expected Market Return (%)",
        min_value=0.0,
        max_value=50.0,
        value=12.0
    )

    beta = st.number_input(
        "Stock Beta",
        value=1.0
    )

    expected_return = (
        risk_free
        + beta * (market_return - risk_free)
    )

    st.success(
        f"CAPM Expected Return = {expected_return:.2f}%"
    )


elif page == "Stock Analysis":

    st.title("Stock Analysis")

    selected_stock = st.selectbox(
        "Choose Stock",
        list(stocks.keys())
    )

    years = st.number_input(
        "Years",
        min_value=1,
        max_value=10,
        value=1
    )

    stock_data, _ = get_stock_data(
        selected_stock,
        years
    )

    if not stock_data.empty:

        close = stock_data["Close"]

        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=close.index,
                y=close.values,
                mode="lines",
                name=selected_stock
            )
        )

        fig.update_layout(
            title=f"{selected_stock} Stock Price",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_white",
            height=550
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )



elif page == "Stock Prediction":

    st.title("🔮 Stock Prediction")

    st.info(
        "Stock Prediction module can be connected with "
        "Machine Learning models such as Linear Regression, "
        "Random Forest, XGBoost or LSTM."
    )