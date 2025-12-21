import streamlit as st
import contextlib

@contextlib.contextmanager
def display_loading_indicator(text="Loading..."):
    """Display a loading indicator while executing a code block"""
    with st.spinner(text):
        yield

def handle_api_error(function_call, default_value=None):
    """
    Handle API errors gracefully by returning a default value
    
    Args:
        function_call: The function or value to try and evaluate
        default_value: Value to return if there's an error
        
    Returns:
        The result of function_call if successful, otherwise default_value
    """
    try:
        if callable(function_call):
            return function_call()
        else:
            return function_call
    except Exception as e:
        st.warning(f"API error: {e}")
        return default_value
