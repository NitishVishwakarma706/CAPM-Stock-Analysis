import streamlit as st
import pandas as pd
from pages.utils.model_train import get_data, get_rolling_mean, get_differencing_order, evaluate_model, scaling, get_forcast, inverse_scaling
from pages.utils.plotly_figure import plotly_table, Moving_average_forecast

st.set_page_config(page_title="Stock Analysis", page_icon="page_with_curl", layout="wide")
st.title("📈 Stock Prediction Dashboard")

col1, col2, col3 = st.columns(3)
with col1:
    with st.form(key='ticker_form'):
        user_input = st.text_input('Stock Ticker', 'TSLA')
        submit_button = st.form_submit_button(label='Run Prediction Analysis')

ticker = user_input.strip().upper()

if submit_button and ticker:
    st.subheader(f'Prediction Next 30 days Close Price for {ticker}...')
    try:
        with st.spinner('Running models...'):
            close_price = get_data(ticker)
            if isinstance(close_price.columns, pd.MultiIndex):
                close_price.columns = close_price.columns.get_level_values(0)
            
            rolling_price = get_rolling_mean(close_price)
            differencing_order = get_differencing_order(rolling_price)
            scaled_data, scaler = scaling(rolling_price)
            rmse = evaluate_model(scaled_data, differencing_order)
            
        st.write(f"📊 **Model RMSE Score:** `{rmse}`")

        forecast = get_forcast(scaled_data, differencing_order)
        forecast['Close'] = inverse_scaling(scaler, forecast['Close'])
        
        st.write('#### 📋 Forecast Data (Next 30 Days)')
        fig_tail = plotly_table(forecast.sort_index(ascending=True).round(3))
        fig_tail.update_layout(height=220)
        st.plotly_chart(fig_tail, use_container_width=True)

        historical_series = pd.Series(rolling_price.values.flatten(), index=rolling_price.index, name='Close')
        
        forecast_series = pd.Series(forecast['Close'].values.flatten(), index=forecast.index, name='Close')
        
        forecast_series.index = pd.to_datetime(forecast_series.index)
        historical_series.index = pd.to_datetime(historical_series.index)
        
        forecast_combined = pd.concat([historical_series, forecast_series]).to_frame(name='Close')

        st.write('#### 📉 Historical vs Predicted Rolling Close Trend')
        
        chart_figure = Moving_average_forecast(forecast_combined)
        
        if chart_figure is not None:
            st.plotly_chart(chart_figure, use_container_width=True)
            
    except Exception as error:
        st.error(f"Execution Error: {str(error)}")
elif not ticker:
    st.warning("Please provide a valid stock ticker symbol.")


