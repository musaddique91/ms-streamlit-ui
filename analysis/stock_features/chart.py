import streamlit as st
import pandas as pd
import plotly.graph_objects as go
def show_charts(selected_symbol,stock_data):
    chart_tabs = st.tabs(["Candlestick", "Line Chart", "Volume", "Returns Distribution"])      
    # Candlestick chart
    with chart_tabs[0]:
        fig = go.Figure(data=[go.Candlestick(
            x=stock_data['Date'],
            open=stock_data['Open'],
            high=stock_data['High'],
            low=stock_data['Low'],
            close=stock_data['Close'],
            name='Candlesticks'
        )])

        # Add titles and format
        fig.update_layout(
            title=f'{stock_data} Candlestick Chart',
            yaxis_title='Price',
            xaxis_title='Date',
            xaxis_rangeslider_visible=True  # Hide range slider
        )
        st.plotly_chart(fig, use_container_width=True)
        
        
        
    # Line chart
    with chart_tabs[1]:
        # Create line chart
        fig = go.Figure()
        
        # Add Close price line
        fig.add_trace(go.Scatter(
            x=stock_data['Date'],
            y=stock_data['Close'],
            mode='lines',
            name='Close'
        ))
        
        # Add Open price line
        fig.add_trace(go.Scatter(
            x=stock_data['Date'],
            y=stock_data['Open'],
            mode='lines',
            name='Open'
        ))
        
        fig.update_layout(
            title=f"{selected_symbol} Price Trend",
            xaxis_title="Date",
            yaxis_title="Price ($)"
        )
        
        # Add moving averages        
        stock_data['MA30'] = stock_data['Close'].rolling(window=30).mean()
        stock_data['MA90'] = stock_data['Close'].rolling(window=90).mean()
        
        fig.add_scatter(
            x=stock_data['Date'],
            y=stock_data['MA30'], 
            mode='lines', 
            name='30-day MA',
            line=dict(color='orange')
        )
        
        fig.add_scatter(
            x=stock_data['Date'],
            y=stock_data['MA90'], 
            mode='lines', 
            name='90-day MA',
            line=dict(color='green')
        )
        
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

    # Volume chart
    with chart_tabs[2]:
        # Create volume chart using go.Figure
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=stock_data['Date'],
            y=stock_data['Volume'],
            name='Volume'
        ))
        
        fig.update_layout(
            title=f"{selected_symbol} Trading Volume"
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Volume",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)

    # Returns distribution
    with chart_tabs[3]:
        # Calculate daily returns
        stock_data['Daily Return'] = stock_data['Close'].pct_change() * 100
        
        # Create histogram using go.Figure
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=stock_data['Daily Return'],
            nbinsx=50,
            name='Daily Returns'
        ))
        
        fig.update_layout(
            title=f"{selected_symbol} Daily Returns Distribution"
        )
        
        fig.update_layout(
            xaxis_title="Daily Return (%)",
            yaxis_title="Frequency",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)