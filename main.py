import streamlit as st

st.set_page_config(
    page_title="Trading App", page_icon=":chart_with_upwards_trend:", layout="wide"
)

st.title('Tradin Guide App :bar_chart:')
st.header('We provide a Greatest platform for you to collect all information prior to investing in Stocks')
st.image('apps.jpg',use_container_width=True)
st.markdown('### We provide the following Services:')

st.markdown('#### :one: Stock Information')
st.write('Through this page, you can see all the information about stock. ')

st.markdown('#### :two: Stock Prediction')
st.write('You can explore predicted closing price for the next 30 days based on historical stock data and Advance forecasting models, Use this tool to gain valuable insights into market trends and make informed investment decision.')

st.markdown('#### :three: CAPM Return')
st.write('Discover hoe the Central Asset Price Model(CAPM) calculates the expected the expected return of different stocks asset based on its risk and market performance.')

st.markdown('#### :four: CAPM Beta')
st.write('Calculate beta and Expected Return for Individual Stocks.')