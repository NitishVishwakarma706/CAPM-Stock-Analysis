# importing libraries
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import pandas_datareader.data as web
import datetime 
import pages.utils.capm_function as capm_function

st.set_page_config(page_title="CAPM", 
                   page_icon=":chart_with_upwards_trend:", 
                   layout="wide"
                   )

st.title("Capital Asset Pricing Model (CAPM)")

col1, col2 = st.columns([1,1])
with col1:
    stocks_list = st.multiselect("Choose 4  stock(s) you want to analyze", ["AAPL", "TSLA", "NFLX", "MSFT" , "AMZN", "GOOGL", "META", "NVDA", "JPM", "V", "MA", "DIS", "PYPL", "ADBE", "CRM", "INTC", "CSCO", "ORCL", "IBM", "QCOM", "TXN", "ASML", "NET", "BRK.B", "WMT", "COST", "HD", "PG", "LLY", "UNH", "JNJ", "ABBV", "MRK", "BAC", "GS", "XOM", "CVX"], default=["AAPL", "TSLA", "GOOGL", "AMZN"])

with col2:
    year = st.number_input("Number of Years to analyze", min_value=1, max_value=10)
try:
    start = datetime.date(datetime.date.today().year - year, datetime.date.today().month, datetime.date.today().day)
    end = datetime.date.today()

    SP500 = web.DataReader(['sp500'],'fred',start,end)
    stocks_df = pd.DataFrame()

    for stock in stocks_list:
        data = yf.download(stock, start=start, end=end, group_by="column")
        if not data.empty:
            close_prices = data['Close'].copy()
            close_prices.index = close_prices.index.tz_localize(None)
            stocks_df[stock] = close_prices

    stocks_df.reset_index(inplace=True)
    SP500.reset_index(inplace=True)
    SP500.rename(columns={'DATE': 'Date'}, inplace=True)

    stocks_df = pd.merge(stocks_df, SP500, on='Date', how='inner')

    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown('### DataFrame Head')
        st.dataframe(stocks_df.head(), use_container_width = True)

    with col2:
        st.markdown('### DataFrame Tail')
        st.dataframe(stocks_df.tail(), use_container_width = True)

    col1, col2 = st.columns([1,1])

    with col1:
        st.markdown('### Price Of All Stocks')
        st.plotly_chart(capm_function.interactiveplot(stocks_df))

    with col2:
        st.markdown('### Price Of All Stocks (After Normalization)')
        st.plotly_chart(capm_function.interactiveplot(capm_function.normalize(stocks_df)))

    stocks_daily_return = capm_function.daily_return(stocks_df)
    print(stocks_daily_return.head())

    beta = {}
    alpha = {}

    for i in stocks_daily_return.columns:
        if i != 'Date' and i != 'sp500':
            b, a = capm_function.calculate_beta(stocks_daily_return,i)

            beta[i] = b
            alpha[i] = a
    print(beta, alpha)

    beta_df = pd.DataFrame(columns=['Stock', 'Beta Value'])
    beta_df['Stock'] = beta.keys()
    beta_df['Beta Value'] = [str(round(i,2)) for i in beta.values()]

    with col1:
        st.markdown('### Calculated Beta Value')
        st.dataframe(beta_df, use_container_width=True)

    rf = 0
    rm = stocks_daily_return['sp500'].mean()*252
    return_df = pd.DataFrame()
    return_value = []

    for stock, value in beta.items():
        return_value.append(str(round(rf + (value*(rf-rm)),2)))
    return_df['Stock'] = stocks_list

    return_df['Return Value'] = return_value

    with col2:
        st.markdown('### Calculated Return using CAPM')
        st.dataframe(return_df, use_container_width=True)

except:
    st.write('Please Select Valid Input...')