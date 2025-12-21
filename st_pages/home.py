import streamlit as st

def show_home():
    st.title("Welcome to Data Analytics Dashboard")
    
    st.markdown("<h2 style='text-align: center;'>Our Services</h2>", unsafe_allow_html=True)
    
    # Create three columns for services
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📊 Data Analytics")
        st.write("""
        Comprehensive analytics tools for:
        - Stock analysis
        - Sales performance
        - Customer insights
        - Product metrics
        """)
        
    with col2:
        st.subheader("🔮 Predictions")
        st.write("""
        Advanced forecasting using:
        - Prophet
        - Machine Learning
        - Time Series Analysis
        - Trend Detection
        """)
        
    with col3:
        st.subheader("📈 Real-time Insights")
        st.write("""
        Monitor your business with:
        - Live dashboards
        - Automated reports
        - Custom alerts
        - Performance tracking
        """)
    
    st.markdown("---")
    
    st.header("Getting Started")
    st.write("""
    1. Navigate to Data Analytics to explore your data
    2. Use Data Predictions to forecast future trends
    3. Track your analysis history in the History section
    """)