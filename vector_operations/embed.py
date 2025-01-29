import streamlit as st
from langchain_community.embeddings.oracleai import OracleEmbeddings

def create_embedder():
    proxy=""
    embedder_params = {"provider": st.session_state.provider, "model": st.session_state.embedding_model}
    embedder = OracleEmbeddings(conn=st.session_state.conn_demo_user, params=embedder_params, proxy=proxy)
    return embedder
    
def embed_parameters_form():    
    provider="database"
    def set_provider():
        st.session_state['provider'] = provider         

    provider = st.radio(
        "Embedding Model Provider",
        ["DATABASE", "EXTERNAL"],
        captions=[
            "",
            "",
        ],horizontal=True,
        index=0,
        on_change=set_provider,
        help="For the Oracle Split Example visit https://python.langchain.com/v0.2/docs/integrations/document_loaders/oracleai/#split-documents"
    )
    
    set_provider()
    
    return None