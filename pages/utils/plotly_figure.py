import pandas as pd
import plotly.graph_objects as go
import pandas_ta as pta
import dateutil.relativedelta

def prepare_dataframe(dataframe):
    """
    Prepare yfinance DataFrame for technical analysis.

    Handles:
    - MultiIndex columns
    - Normal columns
    - Missing values
    - Date index
    """

    if dataframe is None or dataframe.empty:
        return pd.DataFrame()

    df = dataframe.copy()


    if isinstance(df.columns, pd.MultiIndex):

        df.columns = df.columns.get_level_values(0)


    df = df.loc[:, ~df.columns.duplicated()]


    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    for column in required_columns:

        if column not in df.columns:
            df[column] = pd.NA


    for column in [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


    df = df.dropna(
        subset=["Close"]
    )


    df = df.reset_index()

    if "Date" not in df.columns:

        if "Datetime" in df.columns:

            df = df.rename(
                columns={
                    "Datetime": "Date"
                }
            )

        else:

            df = df.rename(
                columns={
                    df.columns[0]: "Date"
                }
            )

    return df


def plotly_table(dataframe):

    header_color = "#0078ff"
    row_even_color = "#f8fafd"
    row_odd_color = "#e1efff"
    grid_line_color = "#ffffff"

    if dataframe is None or dataframe.empty:

        dataframe = pd.DataFrame(
            {"Value": ["No data available"]}
        )

    header_values = ["<b>Index</b>"] + [
        f"<b>{str(col)[:20]}</b>"
        for col in dataframe.columns
    ]

    index_values = [
        f"<b>{str(idx)[:30]}</b>"
        for idx in dataframe.index
    ]

    num_rows = len(dataframe)

    cell_fill_colors = [

        [
            row_odd_color
            if row_idx % 2 == 0
            else row_even_color

            for row_idx in range(num_rows)
        ]

        for _ in range(
            len(dataframe.columns) + 1
        )
    ]

    fig = go.Figure(

        data=[

            go.Table(

                header=dict(

                    values=header_values,

                    line_color=header_color,

                    fill_color=header_color,

                    align="left",

                    font=dict(
                        color="white",
                        size=15
                    ),

                    height=35,
                ),

                cells=dict(

                    values=[index_values]
                    + [
                        dataframe[col].tolist()
                        for col in dataframe.columns
                    ],

                    fill_color=cell_fill_colors,

                    align="left",

                    line_color=grid_line_color,

                    font=dict(
                        color="black",
                        size=15
                    ),

                    height=28,
                ),
            )
        ]
    )

    fig.update_layout(

        height=min(
            40 + (num_rows * 30),
            800
        ),

        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0
        ),
    )

    return fig


def filter_data(dataframe, num_period):

    df = prepare_dataframe(dataframe)

    if df.empty:
        return df


    if "Date" not in df.columns:
        return df

    # Make sure dates are datetime
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Date"]
    )

    if df.empty:
        return df

   

    last_date = df["Date"].iloc[-1]


    if num_period == "1mo":

        date = (
            last_date
            + dateutil.relativedelta.relativedelta(
                months=-1
            )
        )

    elif num_period == "5d":

        date = (
            last_date
            + dateutil.relativedelta.relativedelta(
                days=-5
            )
        )

    elif num_period == "6mo":

        date = (
            last_date
            + dateutil.relativedelta.relativedelta(
                months=-6
            )
        )

    elif num_period == "1y":

        date = (
            last_date
            + dateutil.relativedelta.relativedelta(
                years=-1
            )
        )

    elif num_period == "5y":

        date = (
            last_date
            + dateutil.relativedelta.relativedelta(
                years=-5
            )
        )

    elif num_period == "ytd":

        date = pd.Timestamp(
            year=last_date.year,
            month=1,
            day=1
        )

    else:

        date = df["Date"].iloc[0]


    filtered_df = df[
        df["Date"] >= date
    ].copy()

    return filtered_df



def close_chart(
    dataframe: pd.DataFrame,
    period: str
) -> go.Figure:

    df = prepare_dataframe(
        dataframe
    )

    if period:
        df = filter_data(
            df,
            period
        )

    fig = go.Figure()

    if df.empty:
        return fig

    fig.add_trace(

        go.Scatter(

            x=df["Date"],

            y=df["Open"],

            mode="lines",

            name="Open",

            line=dict(
                width=2,
                color="#5ab7ff"
            )
        )
    )


    fig.add_trace(

        go.Scatter(

            x=df["Date"],

            y=df["Close"],

            mode="lines",

            name="Close",

            line=dict(
                width=2,
                color="white"
            )
        )
    )


    fig.add_trace(

        go.Scatter(

            x=df["Date"],

            y=df["High"],

            mode="lines",

            name="High",

            line=dict(
                width=2,
                color="#0078ff"
            )
        )
    )


    fig.add_trace(

        go.Scatter(

            x=df["Date"],

            y=df["Low"],

            mode="lines",

            name="Low",

            line=dict(
                width=2,
                color="red"
            )
        )
    )

    fig.update_xaxes(
        rangeslider_visible=True
    )

    fig.update_layout(

        height=500,

        margin=dict(
            l=0,
            r=20,
            t=20,
            b=0
        ),

        plot_bgcolor="black",

        paper_bgcolor="#e1efff",

        legend=dict(
            yanchor="top",
            xanchor="right",
            bgcolor="black",
            font=dict(
                color="white"
            )
        ),

        xaxis_title="Date",

        yaxis_title="Price",
    )

    return fig



def candlestic(
    dataframe,
    num_period
):

    df = prepare_dataframe(
        dataframe
    )

    df = filter_data(
        df,
        num_period
    )

    fig = go.Figure()

    if df.empty:
        return fig


    fig.add_trace(

        go.Candlestick(

            x=df["Date"],

            open=df["Open"],

            high=df["High"],

            low=df["Low"],

            close=df["Close"],

            name="Candlestick",
        )
    )


    fig.update_layout(

        height=500,

        margin=dict(
            l=0,
            r=20,
            t=20,
            b=0
        ),

        plot_bgcolor="black",

        paper_bgcolor="#e1e6ff",

        legend=dict(
            yanchor="top",
            xanchor="right",
            bgcolor="black",
            font=dict(
                color="white"
            )
        ),

        xaxis_title="Date",

        yaxis_title="Price",
    )

    return fig



def RSI(
    dataframe,
    num_period
):

    df = prepare_dataframe(
        dataframe
    )

    if df.empty:
        return go.Figure()


    close_series = df["Close"]


    df["RSI"] = pta.rsi(
        close_series,
        length=14
    )


    df = filter_data(
        df,
        num_period
    )

    fig = go.Figure()

    if df.empty:
        return fig


    fig.add_trace(

        go.Scatter(

            x=df["Date"],

            y=df["RSI"],

            name="RSI",

            line=dict(
                width=2,
                color="orange"
            )
        )
    )

    fig.add_trace(

        go.Scatter(

            x=df["Date"],

            y=[70] * len(df),

            name="Overbought",

            line=dict(
                width=2,
                color="red",
                dash="dash"
            )
        )
    )


    fig.add_trace(

        go.Scatter(

            x=df["Date"],

            y=[30] * len(df),

            name="Oversold",

            line=dict(
                width=2,
                color="#79da84",
                dash="dash"
            )
        )
    )

    fig.update_layout(

        yaxis_range=[
            0,
            100
        ],

        height=250,

        paper_bgcolor="black",

        plot_bgcolor="black",

        margin=dict(
            l=0,
            r=20,
            t=20,
            b=0
        ),

        legend=dict(

            yanchor="top",

            orientation="h",

            y=1.02,

            xanchor="right",

            x=1,

            bgcolor="black",

            font=dict(
                color="white"
            )
        ),

        xaxis_title="Date",

        yaxis_title="RSI",
    )

    return fig



def Moving_average(
    dataframe,
    num_period
):

    df = prepare_dataframe(
        dataframe
    )

    if df.empty:
        return go.Figure()


    df["SMA_50"] = pta.sma(
        df["Close"],
        length=50
    )

    df = filter_data(
        df,
        num_period
    )

    fig = go.Figure()

    if df.empty:
        return fig

  
    fig.add_trace(

        go.Scatter(

            x=df["Date"],

            y=df["Open"],

            mode="lines",

            name="Open",

            line=dict(
                width=2,
                color="#5ab7ff"
            )
        )
    )

    fig.add_trace(

        go.Scatter(

            x=df["Date"],

            y=df["Close"],

            mode="lines",

            name="Close",

            line=dict(
                width=2,
                color="white"
            )
        )
    )


    fig.add_trace(

        go.Scatter(

            x=df["Date"],

            y=df["High"],

            mode="lines",

            name="High",

            line=dict(
                width=2,
                color="#0078ff"
            )
        )
    )


    fig.add_trace(

        go.Scatter(

            x=df["Date"],

            y=df["Low"],

            mode="lines",

            name="Low",

            line=dict(
                width=2,
                color="red"
            )
        )
    )

    fig.add_trace(

        go.Scatter(

            x=df["Date"],

            y=df["SMA_50"],

            mode="lines",

            name="SMA 50",

            line=dict(
                width=2,
                color="purple"
            )
        )
    )


    fig.update_xaxes(
        rangeslider_visible=True
    )

    fig.update_layout(

        height=500,

        margin=dict(
            l=0,
            r=20,
            t=20,
            b=0
        ),

        plot_bgcolor="black",

        paper_bgcolor="#e1efff",

        legend=dict(

            yanchor="top",

            xanchor="right",

            bgcolor="black",

            font=dict(
                color="white"
            )
        ),

        xaxis_title="Date",

        yaxis_title="Price",
    )

    return fig



def MACD(
    dataframe,
    num_period
):

    df = prepare_dataframe(
        dataframe
    )

    if df.empty:
        return go.Figure()


    macd_df = pta.macd(
        df["Close"],
        fast=12,
        slow=26,
        signal=9
    )

    if macd_df is None or macd_df.empty:
        return go.Figure()


    macd_column = [
        col
        for col in macd_df.columns
        if col.startswith("MACD_")
        and not col.startswith("MACDs_")
        and not col.startswith("MACDh_")
    ]

    signal_column = [
        col
        for col in macd_df.columns
        if col.startswith("MACDs_")
    ]

    histogram_column = [
        col
        for col in macd_df.columns
        if col.startswith("MACDh_")
    ]


    if (
        not macd_column
        or not signal_column
        or not histogram_column
    ):
        return go.Figure()


    df["MACD"] = macd_df[
        macd_column[0]
    ].values

    df["MACD Signal"] = macd_df[
        signal_column[0]
    ].values

    df["MACD Hist"] = macd_df[
        histogram_column[0]
    ].values


    df = filter_data(
        df,
        num_period
    )

    fig = go.Figure()

    if df.empty:
        return fig

    fig.add_trace(

        go.Scatter(

            x=df["Date"],

            y=df["MACD"],

            name="MACD",

            line=dict(
                width=2,
                color="orange"
            )
        )
    )

    fig.add_trace(

        go.Scatter(

            x=df["Date"],

            y=df["MACD Signal"],

            name="Signal",

            line=dict(
                width=2,
                color="red",
                dash="dash"
            )
        )
    )


    fig.add_trace(

        go.Bar(

            x=df["Date"],

            y=df["MACD Hist"],

            name="Histogram",

            opacity=0.5
        )
    )

    fig.update_layout(

        height=250,

        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0
        ),

        plot_bgcolor="black",

        paper_bgcolor="#e1efff",

        legend=dict(

            yanchor="top",

            orientation="h",

            y=1.02,

            xanchor="right",

            x=1,

            bgcolor="black",

            font=dict(
                color="white"
            )
        ),

        xaxis_title="Date",

        yaxis_title="MACD",
    )

    return fig

def Moving_average_forecast(
    forecast
):

    fig = go.Figure()

    if forecast is None or forecast.empty:
        return fig

    future_days = min(
        30,
        len(forecast)
    )

    historical_end = (
        len(forecast)
        - future_days
    )



    if historical_end > 0:

        fig.add_trace(

            go.Scatter(

                x=forecast.index[
                    :historical_end
                ],

                y=forecast["Close"].iloc[
                    :historical_end
                ],

                mode="lines",

                name="Close Price",

                line=dict(
                    width=2,
                    color="white"
                )
            )
        )

    fig.add_trace(
        go.Scatter(
            x=forecast.index[
                historical_end:
            ],
            y=forecast["Close"].iloc[
                historical_end:
            ],
            mode="lines",
            name="Future Close Price",
            line=dict(
                width=2,
                color="red"
            )
        )
    )
    fig.update_xaxes(
        rangeslider_visible=True
    )

    fig.update_layout(
        height=500,
        margin=dict(l=20,r=20,t=20,b=20),
        plot_bgcolor="black",
        paper_bgcolor="#e1efff",
        legend=dict(
            yanchor="top",
            xanchor="right",
            bgcolor="black",
            font=dict(
                color="white"
            )
        ),
        xaxis_title="Date",
        yaxis_title="Close Price",
    )

    return fig
