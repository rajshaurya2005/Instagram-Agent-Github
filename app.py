import sys
import os
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ui.streamlit_ui import run_ui
from src.ui.account_manager import app as account_manager_app

if __name__ == "__main__":
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Main App", "Manage Accounts"])

    if page == "Main App":
        run_ui()
    elif page == "Manage Accounts":
        account_manager_app()