import streamlit as st

st.set_page_config(
    page_title="Oracle23ai Vector Search ",
    page_icon=":o2:",
)

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

except Exception as e:
    st.warning(f"An error occurred: {e}")