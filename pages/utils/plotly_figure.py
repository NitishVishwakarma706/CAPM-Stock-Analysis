import datetime
import dateutil
import pandas as pd
import plotly.graph_objects as go
import pandas_ta as pta


def plotly_table(dataframe):
    header_color = "#0078ff"
    row_even_color = "#f8fafd"
    row_odd_color = "#e1efff"
    grid_line_color = "#ffffff"

    header_values = ["<b>Index</b>"] + [
        f"<b>{str(col)[:10]}</b>" for col in dataframe.columns
    ]
    index_values = [f"<b>{str(idx)[:10]}</b>" for idx in dataframe.index]

    num_rows = len(dataframe)
    cell_fill_colors = [
        [
            row_odd_color if row_idx % 2 == 0 else row_even_color
            for row_idx in range(num_rows)
        ]
        for _ in range(len(dataframe.columns) + 1)
    ]

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=header_values,
                    line_color=header_color,
                    fill_color=header_color,
                    align="left",
                    font=dict(color="white", size=15),
                    height=35,
                ),
                cells=dict(
                    values=[index_values]
                    + [dataframe[col] for col in dataframe.columns],
                    fill_color=cell_fill_colors,
                    align="left",
                    line_color=[grid_line_color],
                    font=dict(color="black", size=15),
                    height=28,
                ),
            )
        ]
    )

    fig.update_layout(
        height=min(40 + (num_rows * 30), 800),
        margin=dict(l=0, r=0, t=0, b=0),
    )
    return fig


def filter_data(dataframe, num_period):
    if num_period == '1mo':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(months=-1)
    elif num_period == '5d':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(days=-5)
    elif num_period == '6mo':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(months=-6)
    elif num_period == '1y':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(years=-1)
    elif num_period == '5y':
        date = dataframe.index[-1] + dateutil.relativedelta.relativedelta(years=-5)
    else:
        date = dataframe.index[0]

    return dataframe.reset_index()[dataframe.reset_index()['Date'] > date]


def close_chart(dataframe: pd.DataFrame, period: str) -> go.Figure:
    if period:
        dataframe = filter_data(dataframe, period)
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(x=dataframe['Date'], y=dataframe['Open'], mode='lines', name='Open', line=dict(width=2, color='#5ab7ff'))
    )
    fig.add_trace(
        go.Scatter(x=dataframe['Date'], y=dataframe['Close'], mode='lines', name='Close', line=dict(width=2, color='white'))
    )
    fig.add_trace(
        go.Scatter(x=dataframe['Date'], y=dataframe['High'], mode='lines', name='High', line=dict(width=2, color='#0078ff'))
    )
    fig.add_trace(
        go.Scatter(x=dataframe['Date'], y=dataframe['Low'], mode='lines', name='Low', line=dict(width=2, color='red'))
    )
    
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(height=500, margin=dict(l=0, r=20, t=20, b=0), plot_bgcolor='black', paper_bgcolor='#e1efff', legend=dict(yanchor='top', xanchor='right', bgcolor="black",font=dict(color="white")))

    return fig


def candlestic(dataframe, num_period):
    dataframe = filter_data(dataframe, num_period)
    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=dataframe['Date'],
            open=dataframe["Open"].squeeze(),
            high=dataframe["High"].squeeze(),
            low=dataframe["Low"].squeeze(),
            close=dataframe["Close"].squeeze(),
            name="Candlestick",
        )
    )
    fig.update_layout(height=500, margin=dict(l=0, r=20, t=20, b=0), plot_bgcolor='black', paper_bgcolor="#e1e6ff", legend=dict(yanchor='top', xanchor='right',bgcolor="black",font=dict(color="white")))
    return fig


def RSI(dataframe, num_period):
    dataframe['RSI'] = pta.rsi(dataframe['Close'])
    dataframe = filter_data(dataframe, num_period)
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dataframe['Date'], y=dataframe.RSI, 
        name='RSI', marker_color='orange', 
        line=dict(width=2, color='orange'), 
    ))

    fig.add_trace(go.Scatter(
        x=dataframe['Date'], y=[70]*len(dataframe), name='Overbought', marker_color='red', line=dict(width=2, color='red', dash='dash'),
    ))

    fig.add_trace(go.Scatter(
        x=dataframe['Date'], y=[30]*len(dataframe), fill='tonexty', name='Oversold', marker_color='#79da84', line=dict(width=2, color='#79da84', dash='dash'),
    ))

    fig.update_layout(yaxis_range=[0, 100], height=200, paper_bgcolor='black', margin=dict(l=0, r=20, t=20, b=0), legend=dict(yanchor='top', orientation='h', y=1.02, xanchor='right', x=1,bgcolor="black",font=dict(color="white")))

    return fig


def Moving_average(dataframe, num_period):
    dataframe['SMA_50'] = pta.sma(dataframe['Close'], 50)
    dataframe = filter_data(dataframe, num_period)
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(x=dataframe['Date'], y=dataframe['Open'], mode='lines', name='Open', line=dict(width=2, color='#5ab7ff'))
    )
    fig.add_trace(
        go.Scatter(x=dataframe['Date'], y=dataframe['Close'], mode='lines', name='Close', line=dict(width=2, color='white'))
    )
    fig.add_trace(
        go.Scatter(x=dataframe['Date'], y=dataframe['High'], mode='lines', name='High', line=dict(width=2, color='#0078ff'))
    )
    fig.add_trace(
        go.Scatter(x=dataframe['Date'], y=dataframe['Low'], mode='lines', name='Low', line=dict(width=2, color='red'))
    )
    fig.add_trace(go.Scatter(
        x=dataframe['Date'], y=dataframe['SMA_50'], mode='lines', name='SMA_50', line=dict(width=2, color='purple')
    ))
    
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(height=500, margin=dict(l=0, r=20, t=20, b=0), plot_bgcolor='black', paper_bgcolor='#e1efff', legend=dict(yanchor='top', xanchor='right',bgcolor="black",font=dict(color="white")))
    
    return fig


def MACD(dataframe, num_period):
    macd_df = pta.macd(dataframe['Close'])
    macd = macd_df.iloc[:, 0]
    macd_signal = macd_df.iloc[:, 1]
    macd_hist = macd_df.iloc[:, 2]

    dataframe['MACD'] = macd
    dataframe['MACD Signal'] = macd_signal
    dataframe['MACD Hist'] = macd_hist

    dataframe = filter_data(dataframe, num_period)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dataframe['Date'],
        y=dataframe['MACD'],
        name='MACD',
        marker_color='orange',
        line=dict(width=2, color='orange'),
    ))

    fig.add_trace(go.Scatter(
        x=dataframe['Date'],
        y=dataframe['MACD Signal'],
        name='Signal',
        marker_color='red',
        line=dict(width=2, color='red', dash='dash'),
    ))

    fig.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0), plot_bgcolor='black', paper_bgcolor='#e1efff', legend=dict(yanchor='top', orientation='h', y=1.02, xanchor='right', x=1,bgcolor="black",font=dict(color="white")))
    return fig

def Moving_average_forecast(forecast):
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x = forecast.index[:-29], 
        y = forecast['Close'].iloc[:-29], 
        mode = 'lines', 
        name = 'Close Price', 
        line = dict(width=2, color='white')
    ))

    fig.add_trace(go.Scatter(
        x = forecast.index[-30:], 
        y = forecast['Close'].iloc[-30:], 
        mode = 'lines', 
        name = 'Future Close Price', 
        line = dict(width=2, color='red')
    ))

    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(
        height=500, 
        margin=dict(l=20, r=20, t=20, b=20), 
        plot_bgcolor='black', 
        paper_bgcolor='#e1efff', 
        legend=dict(yanchor='top', xanchor='right',bgcolor="black",font=dict(color="white"))
    )

    return fig
