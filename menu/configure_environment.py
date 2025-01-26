import streamlit as st
import ollama 
import utils.env_file as env
import utils.common_db_operations as db_ops
import utils.db_connection as db 

# Functions

def save_configuration_changes():
    st.session_state.username=USERNAME
    st.session_state.password=PASSWORD
    st.session_state.demo_username=DEMO_USERNAME
    st.session_state.demo_password=DEMO_PASSWORD
    st.session_state.host=HOST
    st.session_state.port=PORT
    st.session_state.service_name=SERVICE_NAME
    st.session_state.db_expose_port=DB_EXPOSE_PORT
    st.session_state.onnx_directory=ONNX_DIRECTORY
    st.session_state.llm=LLM
    env.write_env_file()

def configure_db():
    if st.session_state.conn_sys.is_healthy():
        print("Sys Connection is ok ")
        st.write("Vector-db is up & running")
        st.write("Starting Config")
        if db_ops.configure_demo_user():
            st.write("DB Config is complete")
            st.info("DB is ready to be used")
    else:
        db.init_db_connections()
        st.warning("Please Check Oracle Database 23ai Container!!!")

def configure_llm(ollama):
    try:         
        #st.write('Ollama is currently running currently')    
        running_LLM_list=[model["name"] for model in ollama.ps()["models"]]
        #ollama is running with the models
        #ollama is up but no model is running 
        if len(running_LLM_list)>0:
            st.write('Ollama is up, Currently running the model '+running_LLM_list[0])
        else:
            st.write('Ollama is up, But currently no LLM model is running')
        OLLAMA_MODELS = ollama.list()["models"]
        #embedding_models_list=[row[0] for row in rows]
        local_LLM_list=[model["name"] for model in OLLAMA_MODELS]
        #st.write(local_LLM_list)
        #st.write(OLLAMA_MODELS)
        selected_LLM_model = st.selectbox(
            "Select one of the locally stored LLM from the list",
            (local_LLM_list),
            index=None,
            placeholder="Select LLM ...",
        )
        if st.button("Start the LLM using Ollama","LLM_run"):
            ollama.pull(selected_LLM_model)
            st.write("Running Ollama with "+selected_LLM_model)
        st.write("To load a new LLM please execute `ollama pull [MODEL_NAME]` from command line")             
    except Exception as e:
        st.warning("Exception Occured. See the details below and please make sure Ollama is installed and running.")
        st.warning(e)  

env.read_env_file()

#Start of the page

# Configuration Top Menu
tab1, tab2 = st.tabs(["Database Settings", "LLM Settings"])
with tab1: 
    USERNAME=st.text_input("Username",st.session_state.username)
    PASSWORD=st.text_input("Password",st.session_state.password)
    DEMO_USERNAME=st.text_input("Demo Username",st.session_state.demo_username)
    DEMO_PASSWORD=st.text_input("Demo Password",st.session_state.demo_password)
    HOST=st.text_input("Host",st.session_state.host)
    PORT=st.text_input("Port",st.session_state.port)
    SERVICE_NAME=st.text_input("Service Name",st.session_state.service_name)
    DB_EXPOSE_PORT=st.text_input("DB Expose Port",st.session_state.db_expose_port)
    if st.button("Save Configuration Changes","Config_Save"):
        save_configuration_changes()  
with tab2:
    LLM=""
    if (st.session_state.host=="host.docker.internal"):
        ollama = ollama.Client("host.docker.internal")
    elif (st.session_state.host=="localhost"):
        ollama = ollama.Client("localhost")
    configure_llm(ollama)          
st.stop()
