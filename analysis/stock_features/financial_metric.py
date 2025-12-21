import streamlit as st
import pandas as pd
import plotly.graph_objects as go
def financial_metric(stock_data,info):
    st.subheader("Financial Metrics")
                        
    # # Calculate key metrics
    if len(stock_data) > 0:
        daily_returns = stock_data['Close'].pct_change().dropna()

        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)

        with metrics_col1:
            st.metric(
                "Current Price",
                f"${stock_data['Close'].iloc[-1]:.2f}",
                f"{stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]:.2f} ({(stock_data['Close'].iloc[-1] / stock_data['Close'].iloc[-2] - 1) * 100:.2f}%)"
            )

        with metrics_col2:
            st.metric(
                "Volatility (Std Dev)",
                f"{daily_returns.std() * 100:.2f}%"
            )

        with metrics_col3:
            if len(stock_data) >= 30:
                st.metric(
                    "30-Day Return",
                    f"{(stock_data['Close'].iloc[-1] / stock_data['Close'].iloc[-min(30, len(stock_data))] - 1) * 100:.2f}%"
                )
            else:
                st.metric("30-Day Return", "N/A")

        with metrics_col4:
            if 'dividendYield' in info and info['dividendYield'] is not None:
                st.metric("Dividend Yield", f"{info['dividendYield'] * 100:.2f}%")
            else:
                st.metric("Dividend Yield", "N/A")