import streamlit as st
import configparser
import os

def read_env_file():
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
    if 'onnx_directory' not in st.session_state:
        st.session_state['onnx_directory'] = config.get('DATABASE','ONNX_DIRECTORY')
    if 'dsn' not in st.session_state:
        st.session_state['dsn'] = st.session_state.host+":"+st.session_state.port+"/"+st.session_state.service_name
    if 'documents_directory' not in st.session_state:
        st.session_state['documents_directory'] = config.get('ENVIRONMET','DOCUMENTS_DIRECTORY')
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

def write_env_file():
    path = os.getcwd()
    config_path = os.path.join(path, ".env")
    config = configparser.ConfigParser()
    config.read(config_path)
    config.set('DATABASE','USERNAME',st.session_state.username)
    config.set('DATABASE','PASSWORD',st.session_state.password)
    config.set('DATABASE','HOST',st.session_state.host)
    config.set('DATABASE','PORT',st.session_state.port)
    config.set('DATABASE','DSN','host:port/service_name')
    config.set('DATABASE','SERVICE_NAME',st.session_state.service_name)
    config.set('DATABASE','ONNX_DIRECTORY',st.session_state.onnx_directory)
    config.set('ENVIRONMET','DOCUMENTS_DIRECTORY',st.session_state.documents_directory)
    config.set('MODELS','LLM',st.session_state.llm)
    config.set('CONTAINER','CONTAINER_NAME',st.session_state.container_name)
    config.set('CONTAINER','ORACLE_PASSWD',st.session_state.oracle_passwd)
    config.set('CONTAINER','DB_HOST_NAME',st.session_state.db_host_name)
    config.set('CONTAINER','DB_PORT',st.session_state.db_port)
    config.set('CONTAINER','DB_EXPOSE_PORT',st.session_state.db_expose_port)
    with open(config_path, 'w') as configfile:    # save
        config.write(configfile)
    config.read(config_path)
