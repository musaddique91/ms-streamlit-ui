import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from analysis import stock

def create_stock_chart(stock_data):
    # Create a more attractive stock level visualization
    fig = go.Figure()
    
    # Add bars for current stock
    fig.add_trace(go.Bar(
        x=stock_data['Product'],
        y=stock_data['Quantity'],
        name='Current Stock',
        marker_color='rgba(58, 71, 80, 0.8)',
        hovertemplate='Product: %{x}<br>Quantity: %{y}<extra></extra>'
    ))
    
    # Add line for reorder points
    fig.add_trace(go.Scatter(
        x=stock_data['Product'],
        y=stock_data['Reorder_Point'],
        name='Reorder Point',
        line=dict(color='rgba(255, 0, 0, 0.8)', width=2, dash='dash'),
        hovertemplate='Product: %{x}<br>Reorder Point: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Stock Levels and Reorder Points',
        title_x=0.5,
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig

def create_sales_chart(sales_data):
    # Create a more attractive sales visualization
    fig = make_subplots(rows=2, cols=1, 
                       subplot_titles=('Monthly Revenue', 'Revenue Growth Rate'),
                       vertical_spacing=0.15)
    
    # Calculate growth rate
    sales_data['Growth_Rate'] = sales_data['Revenue'].pct_change() * 100
    
    # Add revenue line
    fig.add_trace(
        go.Scatter(
            x=sales_data['Month'],
            y=sales_data['Revenue'],
            mode='lines+markers',
            name='Revenue',
            line=dict(width=3, color='rgb(66, 135, 245)'),
            marker=dict(size=8, symbol='circle'),
            fill='tonexty',
            fillcolor='rgba(66, 135, 245, 0.1)',
            hovertemplate='Date: %{x}<br>Revenue: $%{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add growth rate bars
    fig.add_trace(
        go.Bar(
            x=sales_data['Month'],
            y=sales_data['Growth_Rate'],
            name='Growth Rate',
            marker_color='rgba(58, 71, 80, 0.6)',
            hovertemplate='Date: %{x}<br>Growth Rate: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=700,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )
    
    return fig

def create_customer_chart(customer_data):
    # Create a more attractive customer visualization
    colors = ['rgb(66, 135, 245)', 'rgb(245, 131, 66)', 
             'rgb(66, 245, 123)', 'rgb(245, 66, 66)']
    
    fig = go.Figure()
    
    # Add pie chart
    fig.add_trace(go.Pie(
        labels=customer_data['Segment'],
        values=customer_data['Count'],
        hole=0.4,
        marker=dict(colors=colors),
        textinfo='label+percent',
        hovertemplate='Segment: %{label}<br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title='Customer Segments Distribution',
        title_x=0.5,
        annotations=[dict(text='Total Customers', x=0.5, y=0.5, font_size=20, showarrow=False)],
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_product_chart(product_data):
    # Create a more attractive product performance visualization
    fig = go.Figure()
    
    # Calculate bubble sizes based on sales
    bubble_sizes = (product_data['Sales'] / product_data['Sales'].max() * 50) + 20
    
    # Add scatter plot with bubbles
    fig.add_trace(go.Scatter(
        x=product_data['Sales'],
        y=product_data['Profit_Margin'],
        mode='markers+text',
        marker=dict(
            size=bubble_sizes,
            color=product_data['Sales'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Sales ($)'),
            line=dict(color='white', width=1)
        ),
        text=product_data['Product'],
        textposition='top center',
        hovertemplate='Product: %{text}<br>Sales: $%{x:,.0f}<br>Profit Margin: %{y:.1%}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Product Performance Matrix',
        title_x=0.5,
        xaxis_title='Sales ($)',
        yaxis_title='Profit Margin',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='closest'
    )
    
    return fig

def show_analytics():
    st.title("Data Analytics")
    
    # Create tabs for different analytics views
    tabs = st.tabs(["Stock", "Sales", "Customer", "Products"])
    
    # Sample data - In a real application, this would come from your database
    with tabs[0]:  # Stock
        print("calling stock.render")
        stock.render()

    with tabs[1]:  # Sales
        st.header("Sales Analytics")
        # Sample sales data
        sales_data = pd.DataFrame({
            'Month': pd.date_range(start='2023-01-01', periods=12, freq='M'),
            'Revenue': [10000, 12000, 9000, 15000, 11000, 13000, 
                       16000, 14000, 12000, 17000, 19000, 21000]
        })
        
        st.plotly_chart(create_sales_chart(sales_data), use_container_width=True)
        
        # Add KPI metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Revenue", f"${sales_data['Revenue'].sum():,}", "15%")
        with col2:
            st.metric("Average Monthly Revenue", f"${sales_data['Revenue'].mean():,.0f}", "8%")
        with col3:
            st.metric("Revenue Growth", "23%", "5%")

    with tabs[2]:  # Customer
        st.header("Customer Analytics")
        # Sample customer data
        customer_data = pd.DataFrame({
            'Segment': ['New', 'Regular', 'VIP', 'Inactive'],
            'Count': [100, 250, 50, 75]
        })
        
        st.plotly_chart(create_customer_chart(customer_data), use_container_width=True)
        
        # Add KPI metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Customers", f"{customer_data['Count'].sum():,}", "10%")
        with col2:
            st.metric("VIP Ratio", "10.5%", "2%")
        with col3:
            st.metric("Customer Retention", "85%", "-2%")

    with tabs[3]:  # Products
        st.header("Product Analytics")
        # Sample product data
        product_data = pd.DataFrame({
            'Product': ['Product A', 'Product B', 'Product C', 'Product D'],
            'Sales': [5000, 7000, 3000, 6000],
            'Profit_Margin': [0.25, 0.3, 0.2, 0.35]
        })
        
        st.plotly_chart(create_product_chart(product_data), use_container_width=True)
        
        # Add KPI metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Products", "4", "0")
        with col2:
            st.metric("Avg Profit Margin", "27.5%", "3%")
        with col3:
            st.metric("Best Performer", "Product B", "↑")