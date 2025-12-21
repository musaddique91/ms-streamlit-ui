import streamlit as st

def show_personal():
    st.title("Personal Dashboard")
    st.write(f"Welcome, {st.session_state.user.email}!")
    
    # Add personal dashboard content here
    st.header("Your Activity Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Analyses Performed", "15", "2")
    with col2:
        st.metric("Predictions Made", "7", "-1")
    with col3:
        st.metric("Data Sets Uploaded", "3", "1")
    
    st.header("Recent Activity")
    activities = [
        {"date": "2024-02-24", "action": "Ran sales prediction", "result": "10% growth forecasted"},
        {"date": "2024-02-22", "action": "Analyzed customer data", "result": "Identified 3 key segments"},
        {"date": "2024-02-20", "action": "Uploaded new dataset", "result": "Product inventory (1000 items)"}
    ]
    for activity in activities:
        st.write(f"**{activity['date']}**: {activity['action']} - {activity['result']}")
    
    st.header("Saved Reports")
    saved_reports = ["Q4 2023 Sales Analysis", "Customer Churn Prediction", "Product Performance Dashboard"]
    for report in saved_reports:
        st.write(f"- {report}")

