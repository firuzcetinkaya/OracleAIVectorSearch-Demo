import streamlit as st
import configparser
import os 

st.set_page_config(
    page_title=":o2: Oracle23ai Vector Search ",
    page_icon=":o2:",
)

st.write("# Wellcome to the Oracle23ai RAG Vector Search Demo Application!")


def readEnvFile():
    path = os.getcwd()
    config_path = os.path.join(path, ".env")
    config = configparser.ConfigParser()
    config.read(config_path)    
    if 'username' not in st.session_state:
        st.session_state['username'] = config.get('DATABASE','USERNAME')
    if 'password' not in st.session_state:
        st.session_state['password'] = config.get('DATABASE','PASSWORD')
    if 'host' not in st.session_state:
        st.session_state['host'] = config.get('DATABASE','HOST')
    if 'port' not in st.session_state:
        st.session_state['port'] = config.get('DATABASE','PORT')
    if 'service_name' not in st.session_state:
        st.session_state['service_name'] = config.get('DATABASE','SERVICE_NAME')
    if 'table_name' not in st.session_state:
        st.session_state['table_name'] = config.get('DATABASE','TABLE_NAME')
    if 'dsn' not in st.session_state:
        st.session_state['dsn'] = st.session_state.host+":"+st.session_state.port+"/"+st.session_state.service_name
    if 'directory' not in st.session_state:
        st.session_state['directory'] = config.get('ENVIRONMET','DIRECTORY')
    if 'llm' not in st.session_state:
        st.session_state['llm'] = config.get('LLM','MODEL') #'Llama3.2:latest'

readEnvFile()

st.markdown(
    """
    This App is just for demo/test purposes, for any question/issue please reach out.
    
    - Check out User Guide (https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/)
    - Langchain Oracle (https://python.langchain.com/docs/integrations/vectorstores/oracle/)
    - Llamaindex (https://docs.llamaindex.ai/en/stable/examples/vector_stores/orallamavs/)
    
"""
)


