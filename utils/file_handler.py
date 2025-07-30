import os
import streamlit as st


def delete_video_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        st.warning(f"Could not delete video file: {e}")
    return False