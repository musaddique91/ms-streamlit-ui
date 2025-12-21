import streamlit as st
from envs.env.Lib.unittest.mock import inplace
from prophet import Prophet
import plotly.graph_objs as go

def start_predict(symbol, stock_data, n_days):
    st.title(f"{symbol} Stock Price Forecast using Prophet for next {n_days}")
    stock_df = stock_data[['Date', 'Close']].copy()
    stock_df.rename(columns={'Date': 'ds', 'Close': 'y'}, inplace=True)
    model = Prophet()
    model.fit(stock_df)
    future = model.make_future_dataframe(periods=n_days)
    forecast = model.predict(future)
    st.subheader(f"Forecast Data")
    forcast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(n_days)
    forcast_data.rename(columns={'ds': 'Date', 'yhat': 'Close', 'yhat_lower': 'Lower Bound', 'yhat_upper': 'Upper Bound'}, inplace=True)
    st.dataframe(forcast_data)

    # Plot forecast
    st.subheader(f"Forecast Plot")
    fig1 = model.plot(forecast)
    st.pyplot(fig1)

    # Plot components
    st.subheader("Forecast Components")
    fig2 = model.plot_components(forecast)
    st.pyplot(fig2)