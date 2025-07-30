import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config import ACCOUNTS

def save_accounts_to_config(accounts_list):
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config.py'))
    groq_api_key = ""
    try:
        with open(config_path, 'r') as f:
            for line in f:
                if line.startswith("GROQ_API_KEY ="):
                    groq_api_key = line.split("=", 1)[1].strip().strip('"\'')
                    break
    except FileNotFoundError:
        st.error("config.py not found. Please ensure it exists in the root directory.")
        return

    new_config_content = f"GROQ_API_KEY = \"{groq_api_key}\"\n\nACCOUNTS = [\n"
    for account in accounts_list:
        safe_prompt = repr(account["prompt"])
        
        new_config_content += f"    {{\n        'username': \"{account['username']}\",\n"
        new_config_content += f"        'password': \"{account['password']}\",\n"
        new_config_content += f"        'prompt': {safe_prompt}\n    }},\n"
    new_config_content += "]"

    try:
        with open(config_path, 'w') as f:
            f.write(new_config_content)
        st.success("Accounts saved successfully to config.py!")
    except Exception as e:
        st.error(f"Error saving accounts to config.py: {e}")

def app():
    st.title("Manage Instagram Accounts")

    if 'accounts' not in st.session_state:
        st.session_state.accounts = ACCOUNTS

    st.subheader("Existing Accounts")
    if st.session_state.accounts:
        for i, account in enumerate(st.session_state.accounts):
            with st.expander(f"Account: {account['username']}"):
                st.text_input("Username", value=account['username'], key=f"edit_username_{i}")
                st.text_input("Password", type="password", value=account['password'], key=f"edit_password_{i}")
                st.text_area("Prompt", value=account['prompt'], height=200, key=f"edit_prompt_{i}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Update {account['username']}", key=f"update_btn_{i}"):
                        st.session_state.accounts[i]['username'] = st.session_state[f"edit_username_{i}"]
                        st.session_state.accounts[i]['password'] = st.session_state[f"edit_password_{i}"]
                        st.session_state.accounts[i]['prompt'] = st.session_state[f"edit_prompt_{i}"]
                        save_accounts_to_config(st.session_state.accounts)
                        st.rerun()
                with col2:
                    if st.button(f"Delete {account['username']}", key=f"delete_btn_{i}"):
                        st.session_state.accounts.pop(i)
                        save_accounts_to_config(st.session_state.accounts)
                        st.rerun()
    else:
        st.info("No accounts configured yet.")

    st.subheader("Add New Account")
    new_username = st.text_input("New Username", key="new_username")
    new_password = st.text_input("New Password", type="password", key="new_password")
    new_prompt = st.text_area("New Prompt", height=200, key="new_prompt")

    if st.button("Add Account"):
        if new_username and new_password and new_prompt:
            st.session_state.accounts.append({
                "username": new_username,
                "password": new_password,
                "prompt": new_prompt
            })
            save_accounts_to_config(st.session_state.accounts)
            st.rerun()
        else:
            st.warning("Please fill in all fields for the new account.")