import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import analysis.utils as utl
import analysis.stock_features.chart as scharts
import uuid
import os
import analysis.stock_features.financial_metric as fmetric
import analysis.stock_features.stock_predict_prophet as spp
def format_stock(stock_data):
    stock_file_apth = f'{uuid.uuid4()}.csv'
    stock_data.to_csv(stock_file_apth)
    stock_data = pd.read_csv(stock_file_apth)
    os.remove(stock_file_apth)
    stock_data['Open'] = pd.to_numeric(stock_data['Open'], errors='coerce')
    stock_data['Close'] = pd.to_numeric(stock_data['Close'], errors='coerce')
    stock_data['High'] = pd.to_numeric(stock_data['High'], errors='coerce')
    stock_data['Low'] = pd.to_numeric(stock_data['Low'], errors='coerce')

    stock_data = stock_data.iloc[2:].copy()
    stock_data = stock_data.reset_index(drop=True)
    stock_data.rename(columns={'Price': 'Date'},inplace=True)
    return stock_data

def render():
    st.header("Stock Analysis")
    st.markdown("""
    Analyze stock performance, view financial metrics, and visualize price trends.
    Upload a file with stock symbols or manually enter symbols to get started.
    """)

    # Input methods for stock symbols
    input_method = st.radio(
        "Choose input method for stock symbols:",
        ["Manual Entry", "File Upload"]
    )

    if input_method == "Manual Entry":
        stock_symbols = st.text_input(
            "Enter stock symbol e.g., AAPL,MSFT,GOOGL,APOLLO.NS)",
            "AAPL"
        ).upper()

        symbols = [symbol.strip() for symbol in stock_symbols.split(",")]
    else:
        uploaded_file = st.file_uploader("Upload a CSV or TXT file with stock symbols (one per line)", type=["csv", "txt"])
        symbols = []
        if uploaded_file:
            try:
                content = uploaded_file.read().decode()
                symbols = [symbol.strip().upper() for symbol in content.split('\n') if symbol.strip()]
                st.success(f"Successfully loaded {len(symbols)} symbols")
            except Exception as e:
                st.error(f"Error reading file: {e}")
                symbols = ["AAPL"]  # Default fallback
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start date",
            datetime.now() - timedelta(days=365)
        )
    with col2:
        end_date = st.date_input(
            "End date",
            datetime.now()
        )
    future_n_days = st.number_input("Enter Next {n} Days to Predict the stock", 30)
    if st.button("Get Data/Analyse/Predict"):
        if not symbols:
            st.warning("No symbols provided. Using default symbol: AAPL")
            symbols = ["AAPL"]

        # Date range selection


        if start_date >= end_date:
            st.error("Start date must be before end date")
            return

        # Select stock for detailed analysis
        if len(symbols) > 0:
            selected_symbol = symbols[0]

            if selected_symbol:
                with utl.display_loading_indicator("Fetching stock data..."):
                    try:
                        stock_data = yf.download(
                            selected_symbol,
                            start=start_date,
                            end=end_date
                        )
                        stock_data = format_stock(stock_data)
                        if stock_data.empty:
                            st.error(f"No data found for {selected_symbol}. Please check the symbol and try again.")
                            return
                        # Get company info
                        stock = yf.Ticker(selected_symbol)
                        info = utl.handle_api_error(stock.info, {})

                    except Exception as e:
                        st.error(f"Error fetching data: {e}")
                        return

                # Display company information
                if info:
                    company_name = info.get('longName', selected_symbol)
                    st.subheader(f"{company_name} ({selected_symbol})")

                    # Company profile in columns
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Sector:** {info.get('sector', 'N/A')}")
                        st.markdown(f"**Industry:** {info.get('industry', 'N/A')}")
                        st.markdown(f"**Market Cap:** ${info.get('marketCap', 0):,.2f}")

                    with col2:
                        st.markdown(f"**52 Week High:** ${info.get('fiftyTwoWeekHigh', 0):.2f}")
                        st.markdown(f"**52 Week Low:** ${info.get('fiftyTwoWeekLow', 0):.2f}")
                        st.markdown(f"**Volume:** {info.get('volume', 0):,}")
                if not stock_data.empty:
                    st.dataframe(stock_data, use_container_width=True)
                    # Display stock charts in tabs
                    scharts.show_charts(selected_symbol,stock_data)
                    # Financial metrics
                    fmetric.financial_metric(stock_data, info)
                    # # Compare with other stocks (if multiple symbols provided)
                st.header(f"Predict Next {future_n_days} Stock Prices")
                tabs = st.tabs(["Prophet", "LSTM", "XGBoost"])
                with tabs[0]:
                    spp.start_predict(selected_symbol, stock_data, future_n_days)