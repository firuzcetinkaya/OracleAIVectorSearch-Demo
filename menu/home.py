import streamlit as st
import configparser
import os 
import utils.db_connection as db

st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.subheader("",divider="red")
st.write("# Oracle AI Vector Search")
st.subheader("",divider="red")

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
    if 'dsn' not in st.session_state:
        st.session_state['dsn'] = st.session_state.host+":"+st.session_state.port+"/"+st.session_state.service_name
    if 'documents_directory' not in st.session_state:
        st.session_state['documents_directory'] = config.get('ENVIRONMET','DOCUMENTS_DIRECTORY')
    if 'onnx_directory' not in st.session_state:
        st.session_state['onnx_directory'] = config.get('ENVIRONMET','ONNX_DIRECTORY')
    if 'llm' not in st.session_state:
        st.session_state['llm'] = config.get('MODELS','LLM')
    if 'embedding_model' not in st.session_state:
        st.session_state['embedding_model'] = config.get('MODELS','EMBEDDING_MODEL')
    if 'container_name' not in st.session_state:
        st.session_state['container_name'] = config.get('CONTAINER','CONTAINER_NAME')
    if 'oracle_passwd' not in st.session_state:
        st.session_state['oracle_passwd'] = config.get('CONTAINER','ORACLE_PASSWD')
    if 'db_host_name' not in st.session_state:
        st.session_state['db_host_name'] = config.get('CONTAINER','DB_HOST_NAME')
    if 'db_port' not in st.session_state:
        st.session_state['db_port'] = config.get('CONTAINER','DB_PORT')
    if 'db_expose_port' not in st.session_state:
        st.session_state['db_expose_port'] = config.get('CONTAINER','DB_EXPOSE_PORT')

def main():
    readEnvFile()
    db.init_db_connections()

try:
    main()
except Exception as e:
    st.warning(f"An error occurred: {e}")
    st.write("Please check Installation and Configuration Pages for more details...")
