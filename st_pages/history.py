import streamlit as st
import pandas as pd
from datetime import datetime

def show_history():
    st.title("Analysis History")
    
    # In a real application, this would fetch from your database
    # Here's a sample history display
    history_data = pd.DataFrame({
        'Date': pd.date_range(start='2024-01-01', periods=5, freq='D'),
        'Analysis Type': ['Sales Prediction', 'Stock Analysis', 'Customer Segmentation', 
                         'Product Analysis', 'Revenue Forecast'],
        'Status': ['Completed', 'Completed', 'Completed', 'In Progress', 'Scheduled']
    })
    
    # Add filters
    status_filter = st.multiselect('Filter by Status', 
                                 options=history_data['Status'].unique(),
                                 default=history_data['Status'].unique())
    
    type_filter = st.multiselect('Filter by Analysis Type',
                                options=history_data['Analysis Type'].unique(),
                                default=history_data['Analysis Type'].unique())
    
    # Apply filters
    filtered_data = history_data[
        (history_data['Status'].isin(status_filter)) &
        (history_data['Analysis Type'].isin(type_filter))
    ]
    
    # Display filtered history
    st.table(filtered_data)