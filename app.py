import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Oracle23ai Vector Search ",
    page_icon=":o2:",
)
# check whether the app is running inside a container or not
def check_runnning_env():
    def is_docker():
        cgroup = Path('/proc/self/cgroup')
        return Path('/.dockerenv').is_file() or cgroup.is_file() and 'docker' in cgroup.read_text()
    if is_docker():
        st.session_state['is_docker'] = "True"
    else:
        st.session_state['is_docker'] = "False"

    check_runnning_env()

try:
    pages = {
        "":[st.Page("menu/home.py", title="Home Page"),
            st.Page("menu/load_model.py", title="Load Embedding Model"),
            st.Page("menu/vector_operations.py", title="Create Vector Embeddings"),
            st.Page("menu/similarity_search.py", title="Similarity Search"),
            st.Page("menu/chatbot.py", title="Chatbot (RAG)"),
            st.Page("menu/configure_environment.py", title="App Settings"),
            #st.Page("menu/about.py", title="About the App"),
        ],
    }
    pg = st.navigation(pages)
    pg.run()
    
    
    
except Exception as e:
    st.warning(f"An error occurred: {e}")