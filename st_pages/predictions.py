import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

def create_prophet_chart(forecast, historical_data):
    # Create figure with secondary y-axis
    fig = make_subplots(rows=2, cols=1, 
                       subplot_titles=('Forecast with Confidence Intervals', 'Components'),
                       vertical_spacing=0.2,
                       row_heights=[0.7, 0.3])
    
    # Add historical data
    fig.add_trace(
        go.Scatter(
            name='Historical',
            x=historical_data['Date'],
            y=historical_data['Value'],
            mode='markers',
            marker=dict(color='rgb(66, 135, 245)', size=6),
            hovertemplate='Date: %{x}<br>Value: %{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add forecast
    fig.add_trace(
        go.Scatter(
            name='Forecast',
            x=forecast['ds'],
            y=forecast['yhat'],
            mode='lines',
            line=dict(color='rgb(245, 131, 66)', width=2),
            hovertemplate='Date: %{x}<br>Forecast: %{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add confidence intervals
    fig.add_trace(
        go.Scatter(
            name='Upper Bound',
            x=forecast['ds'],
            y=forecast['yhat_upper'],
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hovertemplate='Date: %{x}<br>Upper: %{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            name='Lower Bound',
            x=forecast['ds'],
            y=forecast['yhat_lower'],
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(66, 135, 245, 0.2)',
            fill='tonexty',
            showlegend=False,
            hovertemplate='Date: %{x}<br>Lower: %{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add trend component
    fig.add_trace(
        go.Scatter(
            name='Trend',
            x=forecast['ds'],
            y=forecast['trend'],
            mode='lines',
            line=dict(color='rgb(66, 245, 123)', width=2),
            hovertemplate='Date: %{x}<br>Trend: %{y:.2f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        title='Prophet Forecast Analysis',
        title_x=0.5,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )
    
    return fig

def create_model_comparison_chart(comparison_df, historical_data):
    fig = go.Figure()
    
    # Add historical data
    fig.add_trace(
        go.Scatter(
            name='Historical',
            x=historical_data['Date'],
            y=historical_data['Value'],
            mode='markers',
            marker=dict(color='rgb(66, 135, 245)', size=6),
            hovertemplate='Date: %{x}<br>Value: %{y:.2f}<extra></extra>'
        )
    )
    
    # Add Prophet predictions
    fig.add_trace(
        go.Scatter(
            name='Prophet',
            x=comparison_df['Date'],
            y=comparison_df['Prophet'],
            mode='lines',
            line=dict(color='rgb(245, 131, 66)', width=2, dash='solid'),
            hovertemplate='Date: %{x}<br>Prophet: %{y:.2f}<extra></extra>'
        )
    )
    
    # Add Random Forest predictions
    fig.add_trace(
        go.Scatter(
            name='Random Forest',
            x=comparison_df['Date'],
            y=comparison_df['Random_Forest'],
            mode='lines',
            line=dict(color='rgb(66, 245, 123)', width=2, dash='dash'),
            hovertemplate='Date: %{x}<br>Random Forest: %{y:.2f}<extra></extra>'
        )
    )
    
    # Update layout
    fig.update_layout(
        title='Model Comparison',
        title_x=0.5,
        xaxis_title='Date',
        yaxis_title='Value',
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

def show_predictions():
    st.title("Data Predictions")
    
    uploaded_file = st.file_uploader("Upload your data (CSV with Date and Value columns)", type="csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Show data preview in an expander
            with st.expander("Data Preview"):
                st.write(df.head())
                st.write("Data Shape:", df.shape)
            
            # Add loading spinner
            with st.spinner('Training models and generating predictions...'):
                # Create tabs for different models
                tabs = st.tabs(["Prophet", "Random Forest", "Comparison"])
                
                with tabs[0]:
                    st.header("Prophet Predictions")
                    
                    # Train Prophet model
                    df_prophet = df.rename(columns={'Date': 'ds', 'Value': 'y'})
                    model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=True)
                    model.fit(df_prophet)
                    
                    # Make future predictions
                    future_dates = model.make_future_dataframe(periods=30)
                    forecast = model.predict(future_dates)
                    
                    # Display interactive chart
                    st.plotly_chart(create_prophet_chart(forecast, df), use_container_width=True)
                    
                    # Show metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Forecast End Value", f"{forecast['yhat'].iloc[-1]:.2f}", 
                                f"{((forecast['yhat'].iloc[-1] - df['Value'].iloc[-1])/df['Value'].iloc[-1]*100):.1f}%")
                    with col2:
                        st.metric("Trend", "Increasing" if forecast['trend'].diff().mean() > 0 else "Decreasing")
                    with col3:
                        st.metric("Forecast Uncertainty", 
                                f"±{(forecast['yhat_upper'] - forecast['yhat_lower']).mean():.2f}")
                
                with tabs[1]:
                    st.header("Random Forest Predictions")
                    
                    # Train Random Forest model
                    df['Date_Numeric'] = pd.to_numeric(df['Date'])
                    X = df[['Date_Numeric']]
                    y = df['Value']
                    
                    model_rf = RandomForestRegressor(n_estimators=100, random_state=42)
                    model_rf.fit(X, y)
                    
                    # Make future predictions
                    future_dates = pd.date_range(start=df['Date'].max(), periods=30, freq='D')
                    future_dates_numeric = pd.to_numeric(future_dates)
                    predictions_rf = model_rf.predict(future_dates_numeric.reshape(-1, 1))
                    
                    rf_predictions = pd.DataFrame({
                        'Date': future_dates,
                        'Prediction': predictions_rf
                    })
                    
                    # Create comparison DataFrame for visualization
                    comparison_df = pd.DataFrame({
                        'Date': forecast['ds'].tail(30),
                        'Prophet': forecast['yhat'].tail(30),
                        'Random_Forest': rf_predictions['Prediction']
                    })
                    
                    # Display interactive chart
                    st.plotly_chart(create_model_comparison_chart(comparison_df, df), use_container_width=True)
                    
                with tabs[2]:
                    st.header("Model Comparison")
                    
                    # Display comparison metrics
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Prophet Metrics")
                        st.metric("Mean Forecast", f"{forecast['yhat'].mean():.2f}")
                        st.metric("Trend Direction", "Upward" if forecast['trend'].diff().mean() > 0 else "Downward")
                    
                    with col2:
                        st.subheader("Random Forest Metrics")
                        st.metric("Mean Forecast", f"{rf_predictions['Prediction'].mean():.2f}")
                        st.metric("Prediction Range", 
                                f"{rf_predictions['Prediction'].max() - rf_predictions['Prediction'].min():.2f}")
                    
                    # Display interactive comparison chart
                    st.plotly_chart(create_model_comparison_chart(comparison_df, df), use_container_width=True)
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.write("Please ensure your CSV file has 'Date' and 'Value' columns.")
    else:
        # Show sample data option
        if st.button("Use Sample Data"):
            # Generate sample data
            dates = pd.date_range(start='2023-01-01', end='2024-02-25', freq='D')
            values = np.random.normal(100, 10, size=len(dates)) + np.linspace(0, 50, len(dates))
            sample_df = pd.DataFrame({
                'Date': dates,
                'Value': values
            })
            
            # Save sample data to CSV
            sample_df.to_csv('sample_data.csv', index=False)
            st.success("Sample data generated! Click 'Browse files' and select 'sample_data.csv'")

