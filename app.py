import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Oracle23ai Vector Search ",
    page_icon=":o2:",
)
# check whether the app is running inside a container or not
def is_docker():
    cgroup = Path('/proc/self/cgroup')
    return Path('/.dockerenv').is_file() or cgroup.is_file() and 'docker' in cgroup.read_text()

try:
    pages = {
        "":[st.Page("menu/home.py", title="Home Page")],
        "Vector Operations": [
            st.Page("menu/load_model.py", title="Load Model"),
            st.Page("menu/vector_operations.py", title="Vector Operations"),
        ],
        "Similarity Search & Chatbot": [
            st.Page("menu/similarity_search.py", title="Similarity Search"),
            st.Page("menu/chatbot.py", title="Chatbot (RAG)"),
        ],
        "App Installlation & Configuration": [        
            st.Page("menu/install.py", title="Installation Tips"),
            st.Page("menu/configure_environment.py", title="Configure Environment"),
            st.Page("menu/about.py", title="About the App"),
        ],
    }
    pg = st.navigation(pages)
    pg.run()
    
    if is_docker():
        if 'is_docker' not in st.session_state:
            st.session_state['is_docker'] = "True"
        else:
            st.session_state['is_docker'] = "True"
    else:
        if 'is_docker' not in st.session_state:
            st.session_state['is_docker'] = "False"
        else:
            st.session_state['is_docker'] = "False"
    
except Exception as e:
    st.warning(f"An error occurred: {e}")