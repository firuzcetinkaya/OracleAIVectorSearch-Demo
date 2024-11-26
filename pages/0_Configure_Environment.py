import streamlit as st
import oracledb
import configparser
import sys
import os
import subprocess
import ollama 
from langchain_ollama import OllamaLLM
import psutil

st.set_page_config(
    page_title="Oracle23ai Vector Search Demo Application Configuration Page",
)

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

def writeEnvFile():
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
    config.set('DATABASE','TABLE_NAME',st.session_state.table_name)
    config.set('ENVIRONMET','DIRECTORY',st.session_state.directory)
    config.set('LLM','MODEL',st.session_state.llm)
    with open(config_path, 'w') as configfile:    # save
        config.write(configfile)

st.markdown("This demo environment requires ")
st.markdown("        - :blue-background[Oracle23ai Developer Edition] Docker Image on X86_64 platform,")
st.markdown("        - :blue-background[Python] (min 3.11) installation")
st.markdown("        - :blue-background[Ollama] with a LLM.")
st.markdown("Assumes all the above are installed, App comes with predefined params,")
st.markdown("Please complete the following configurations and initialize the environments to make it run successfully.")


def checkIfOllamaProcessRunning():
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if "ollama".lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;

def checkIfDockerContainerRunning():
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if "docker".lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;

def createOracleDBObjects():
    try:
        connection = oracledb.connect(user=st.session_state.username, password=st.session_state.password, dsn=st.session_state.dsn)
        print("\nConnection successful!\n")
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                begin
                    -- Drop user
                    begin
                        execute immediate 'drop user VECTOR_USER cascade';
                    exception
                        when others then
                            dbms_output.put_line('Error dropping user: ' || SQLERRM);
                    end;
                    
                    -- Create user and grant privileges
                    execute immediate 'create user VECTOR_USER identified by Oracle123';
                    execute immediate 'grant connect, unlimited tablespace, create credential, create procedure, create any index to VECTOR_USER';
                    execute immediate 'create or replace directory DEMO_PY_DIR as ''/scratch/hroy/view_storage/hroy_devstorage/demo/orachain''';
                    execute immediate 'grant read, write on directory DEMO_PY_DIR to public';
                    execute immediate 'grant create mining model to VECTOR_USER';
                    
                    -- Network access
                    begin
                        DBMS_NETWORK_ACL_ADMIN.APPEND_HOST_ACE(
                            host => '*',
                            ace => xs$ace_type(privilege_list => xs$name_list('connect'),
                                            principal_name => 'VECTOR_USER',
                                            principal_type => xs_acl.ptype_db)
                        );
                    end;
                end;
                """
            )
            print("User setup done!")
        except Exception as e:
            print(f"User setup failed with error: {e}")
        finally:
            cursor.close()
        connection.close()
    except Exception as e:
        print(f"Connection failed with error: {e}")
        sys.exit(1)

# Configuration Top Menu
tab1, tab2, tab3 = st.tabs(["Configuration Parameters","Initialize the Oracle23ai Environment", "Initialize Ollama"])
with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        col1.subheader("Database")
        readEnvFile()
        USERNAME=st.text_input("USERNAME",st.session_state.username)
        PASSWORD=st.text_input("PASSWORD",st.session_state.password)
        HOST=st.text_input("HOST",st.session_state.host)
        PORT=st.text_input("PORT",st.session_state.port)
        dsn=st.text_input("dsn",st.session_state.dsn)
        SERVICE_NAME=st.text_input("SERVICE_NAME",st.session_state.service_name)
        TABLE_NAME=st.text_input("TABLE_NAME",st.session_state.table_name)
    with col2:    
        col2.subheader("Environment")
        DIRECTORY=st.text_input("DIRECTORY",st.session_state.directory)
    with col3:
        col3.subheader("LLM")
        LLM=st.text_input("LLM",st.session_state.llm)       
with tab2:
    # the following statement requires Create User privilege, SYS user in Oracle23ai Developer Edition is used
    if st.button("Initialize the Oracle23ai Environment","DB_Initialization"):
        if checkIfDockerContainerRunning(): # check more if docker is running with vector-db
            st.write('Docker is up & running, Docker ')             
            if st.button("Create Vector User, Onnx Directory object and other objects","Oracle_run"):
                createOracleDBObjects()
        else:
            st.warning('No docker process was running. Please install Docker first')
        
with tab3:
    try:         
        if checkIfOllamaProcessRunning():
            #st.write('Ollama is currently running currently')    
            running_LLM_list=[model["name"] for model in ollama.ps()["models"]]
            #ollama is running with the models
            #ollama is up but no model is running 
            st.write('Ollama '+str(len(running_LLM_list)))
            if len(running_LLM_list)>0:
                st.write('Ollama is currently running currently'+running_LLM_list[0])
            OLLAMA_MODELS = ollama.list()["models"]
            #embedding_models_list=[row[0] for row in rows]
            local_LLM_list=[model["name"] for model in OLLAMA_MODELS]
            #st.write(local_LLM_list)
            #st.write(OLLAMA_MODELS)
            selected_LLM_model = st.selectbox(
                "Select one of the the LLM Model stored locally from the list. To load a new LLM please execute \n\n 'ollama pull `model_name`' \n\n from command line",
                (local_LLM_list),
                index=None,
                placeholder="Select LLM ...",
            )
            if st.button("Start the LLM using Ollama","LLM_run"):
                ollama.pull(selected_LLM_model)
                st.write("Running Ollama with "+selected_LLM_model)             
        else:
            st.warning('No Ollama process was running. Please install Ollama first') 
            st.markdown("You may use initialization script below")
            if st.button("Initialize the Ollama Environment","LLM_Initialization"):            
                st.stop()
    except Exception as e:
        st.warning("Exception Occured. See the details below and please make sure Ollama is installed and running. See https://ollama.ai for more details.")
        st.warning(e)
            
if st.button("Save Configuration Changes","Config_Save"):
    st.session_state.username=USERNAME
    st.session_state.password=PASSWORD
    st.session_state.host=HOST
    st.session_state.port=PORT
    st.session_state.dsn=dsn
    st.session_state.service_name=SERVICE_NAME
    st.session_state.table_name=TABLE_NAME
    st.session_state.directory=DIRECTORY
    st.session_state.llm=LLM
    writeEnvFile()             
st.stop()
