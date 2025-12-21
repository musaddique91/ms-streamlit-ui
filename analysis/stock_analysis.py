import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def candal_stick(df):
    # Ensure the Date column is in datetime format
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Reset index to use Date as the x-axis
    df = df.reset_index(drop=True)

    # Create candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='green',  # Color for increasing prices
        decreasing_line_color='red'  # Color for decreasing prices
    )])
    
    # Update layout
    fig.update_layout(
        title="Candlestick Chart Example",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False  # Hide range slider for simplicity
    )
    
    # Show the plot using Streamlit
    st.plotly_chart(fig)
def analyse_stock():
    st.title("📈 Stock Market Analysis")
    st.markdown("Enter a stock symbol and a date range to get the stock data.")
    col1, col2 = st.columns([3, 3])  # Adjust column width as needed
    stock_symbol = col1.text_input("Stock Symbol (e.g., AAPL, TSLA):", "AAPL")
    start_date = col2.date_input("Start Date", pd.to_datetime("2020-01-01"))
    end_date = col2.date_input("End Date", pd.to_datetime("2021-01-01"))
    if st.button("Get Stock Data"):
        # Fetch data using yfinance
        stock_data = yf.download(stock_symbol, start=start_date, end=end_date)
        stock_data = pd.DataFrame(stock_data)
        # Check if data exists
        if stock_data.empty:
            st.error(f"❌ No data found for the symbol {stock_symbol} within the given date range.")
        else:
            # Display stock data
            st.write(f"**Stock Data for {stock_symbol} from {start_date} to {end_date}:**")
            
            
            
            st.dataframe(stock_data, width=800)
            st.title("Average value for each column")
            st.dataframe(stock_data.describe(), width=800)
            
            st.subheader("Stock Close Price Chart")
            st.line_chart(stock_data['Close'])
            
            st.subheader("Stock Volumn Chart")
            st.line_chart(stock_data['Volume'])
            
            # candal_stick(stock_data)
            
            # stock_data['10-Day MA'] = stock_data['Close'].rolling(window=10).mean()
            # stock_data['20-Day MA'] = stock_data['Close'].rolling(window=20).mean()
            # stock_data['50-Day MA'] = stock_data['Close'].rolling(window=50).mean()
            # stock_data_ma = stock_data[['Close', '10-Day MA', '20-Day MA', '50-Day MA']].dropna()
            # st.line_chart(stock_data_ma.reset_index())

