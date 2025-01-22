from langchain_community.embeddings.oracleai import OracleEmbeddings
import utils.db_connection as db 
import streamlit as st
import subprocess
import utils.sql_api as sql_api
from pathlib import Path
    
class ModelLoader:
    """
    A class that implements three different methods for loading an external embedding model to Oracle Database.
    """
    def __init__(self):
        self.db_connection = db.get_vector_user_connection()
        self.onnx_dir = "DEMO_PY_DIR"
        self.db_model_name=""

    def ask_for_model_name(self):
        model_name=""
        model_name = st.text_input("Model Name to save in DB","")
        if len(model_name)<1:
            st.warning("Please Provide a Model Name")
            st.stop()
            return False
        else:
            self.db_model_name=model_name
            return True


    def is_docker():
        cgroup = Path('/proc/self/cgroup')
        return Path('/.dockerenv').is_file() or cgroup.is_file() and 'docker' in cgroup.read_text()
    
    def copy_onnx_to_db_host(self, onnx_file):
        # First copy file to DEMO_PY_DIR to load
        # if this is not a docker env. we need to upload the onnx file to docker instance first, copy file operation varies on different platforms
        #command="docker cp "+"./Data/onnx_files/"+onnx_file+" vector-db:"+st.session_state.onnx_directory+"/"+onnx_file        
        #command="cp"+"./Data/onnx_files/"+onnx_file+" "+st.session_state.onnx_directory+"/"+onnx_file
        if self.is_docker():
            command="docker cp "+"./Data/onnx_files/"+onnx_file+" vector-db:/home/oracle/"+onnx_file    
        else:        
            command="docker cp "+"./Data/onnx_files/"+onnx_file+" vector-db:/home/oracle/"+onnx_file    
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        if (process.returncode==0):
            st.write("Model File is Successfuly Copied to Oracle DB Container")
            return True
        else:
            st.warning("Model File Copy Failed!!!")
            st.stop()

    def load_with_langchain(self, onnx_file: str):
        try:
            OracleEmbeddings.load_onnx_model(self.db_connection, self.onnx_dir, onnx_file, self.db_model_name )
            st.write("ONNX model "+ self.db_model_name+" loaded into Oracle DB.")
        except Exception as e:
            st.write(f"Error loading embedding model with LangChain: {e}")
            st.stop()

    def load_with_llamaindex(self, onnx_file: str):
        try:
            1
        except Exception as e:
            print(f"Error loading embedding model with LlamaIndex: {e}")
            return None

    def load_with_sql(self, onnx_file: str):
        try:
            sql_api.load_embedding_model(self.onnx_dir, onnx_file, self.db_model_name)
            st.write("ONNX model "+ self.db_model_name+" loaded into Oracle DB.")
        except Exception as e:
            st.write(f"Error loading embedding model with SQL: {e}")
            st.stop()
        #check
