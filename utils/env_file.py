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
    if 'demo_username' not in st.session_state:
        st.session_state['demo_username'] = config.get('DATABASE','DEMO_USERNAME')
    if 'demo_password' not in st.session_state:
        st.session_state['demo_password'] = config.get('DATABASE','DEMO_PASSWORD')
    if 'host' not in st.session_state:
        st.session_state['host'] = config.get('DATABASE','HOST')
    if 'port' not in st.session_state:
        st.session_state['port'] = config.get('DATABASE','PORT')
    if 'service_name' not in st.session_state:
        st.session_state['service_name'] = config.get('DATABASE','SERVICE_NAME')
    if 'db_expose_port' not in st.session_state:
        st.session_state['db_expose_port'] = config.get('DATABASE','DB_EXPOSE_PORT')

def write_env_file():
    path = os.getcwd()
    config_path = os.path.join(path, ".env")
    config = configparser.ConfigParser()
    config.read(config_path)
    config.set('DATABASE','USERNAME',st.session_state.username)
    config.set('DATABASE','PASSWORD',st.session_state.password)
    config.set('DATABASE','DEMO_USERNAME',st.session_state.demo_username)
    config.set('DATABASE','DEMO_PASSWORD',st.session_state.demo_password)
    config.set('DATABASE','HOST',st.session_state.host)
    config.set('DATABASE','PORT',st.session_state.port)
    config.set('DATABASE','SERVICE_NAME',st.session_state.service_name)
    config.set('DATABASE','DB_EXPOSE_PORT',st.session_state.db_expose_port)
    with open(config_path, 'w') as configfile:    # save
        config.write(configfile)
    config.read(config_path)
