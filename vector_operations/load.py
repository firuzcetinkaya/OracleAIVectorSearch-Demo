import streamlit as st
import os
from langchain_community.document_loaders.oracleai import OracleDocLoader 
import utils.common_db_operations as db_ops

supported_languages=["ALBANIAN","AMERICAN","ARABIC","ARMENIAN","AZERBAIJANI","BULGARIAN","CROATIAN","CZECH","DANISH","DUTCH","EGYPTIAN","ENGLISH","ESTONIAN","FINNISH","FRENCH","GEORGIAN","GERMAN","GREEK","HEBREW","HINDI","HUNGARIAN","ICELANDIC","INDONESIAN","IRISH","ITALIAN","JAPANESE","KOREAN","KYRGYZ","LATVIAN","LITHUANIAN","MACEDONIAN","MALAY","NORWEGIAN","PERSIAN","POLISH","PORTUGUESE","PUNJABI","ROMANIAN","RUSSIAN","SIMPLIFIED CHINESE","SLOVAK","SLOVENIAN","SPANISH","SWAHILI","SWEDISH","TAMIL","THAI","TRADITIONAL CHINESE","TURKISH","TURKMEN","UKRAINIAN","URDU","VIETNAMESE"]

def create_loader():
    loader = OracleDocLoader(conn=st.session_state.conn_demo_user, params=st.session_state.loader_params)
    return loader

def init_all_embedding_params():

    if 'provider' not in st.session_state:
        st.session_state['provider'] = "DATABASE"          
    if 'glevel' not in st.session_state:
        st.session_state['glevel'] = "S"
    if 'max_percent' not in st.session_state:
        st.session_state['max_percent'] = "10" 
    if 'language' not in st.session_state:
        st.session_state['language'] = "ENGLISH" 
    if 'num_paragraphs' not in st.session_state:
        st.session_state['num_paragraphs'] = "16" 
    if 'num_themes' not in st.session_state:
        st.session_state['num_themes'] = "50" 
    if 'by' not in st.session_state:
        st.session_state['by'] = "WORDS"          
    if 'split_by' not in st.session_state:
        st.session_state['split_by'] = "BY NEWLINE"
    if 'max' not in st.session_state:
        st.session_state['max'] = "25" 
    if 'overlap' not in st.session_state:
        st.session_state['overlap'] = "0"  
    if 'normalize' not in st.session_state:
        st.session_state['normalize'] = "ALL" 
    if 'loader_type' not in st.session_state:
        st.session_state['loader_type'] = "File"
    if 'loader_params' not in st.session_state:
        st.session_state['loader_params'] = {}
        
        
def load_parameters_form():    
    init_all_embedding_params()
    loader_params = {} 

    def set_loader_type():
        st.session_state['loader_params'] = loader_type  
    def set_loader_params(loader_params):
        st.session_state['loader_params'] = loader_params  
    # different loaders file, dir, db
    loader_type = st.radio(
        "",
        ["File", "Directory", "Database"],
        captions=[
            "Single File",
            "Files in a folder",
            "Docs in DB",
        ],horizontal=True,
        on_change=set_loader_type, 
        #help="For the Oracle Loader Example visit https://python.langchain.com/v0.2/docs/integrations/document_loaders/oracleai/#load-documents"
    )
    if loader_type == "File":
        selected_file = st.file_uploader("Select your file to Create Vector Embeddings:", accept_multiple_files=False)
        if selected_file:
            path = os.path.join("./Data/docs", selected_file.name)
            with open(path, "wb") as f:
                f.write(selected_file.getvalue())
            loader_params['file'] = path
            set_loader_params(loader_params)
            st.session_state['loader_type'] = 'File' 
    elif loader_type == "Directory":
        selected_files = st.file_uploader("Select your file to Create Vector Embeddings:", accept_multiple_files=True)
        if selected_files:
            for file in selected_files:
                path = os.path.join("./Data/docs", file.name)
                with open(path, "wb") as f:
                    f.write(file.getvalue())
        loader_params['dir'] = "./Data/docs"
        st.session_state['loader_type'] = 'Directory' 
        set_loader_params(loader_params)
    elif loader_type == "Database":
        # select a table and column from db containing docs
        table_name = st.selectbox(
            "Existing Tables",
            (db_ops.get_tables_list()),
            index=None,
            placeholder="Select table name...",
        )
        if (table_name==""):
            st.write("Select a table first")
        else:
            column_name = st.selectbox(
                "Existing Columns",
                (db_ops.get_columns_list(table_name)),
                index=None,
                placeholder="Select column name...",
            )
            if (column_name==""):
                st.write("select a column")
            else:                    
                loader_params = {
                    "owner": st.session_state.demo_username,
                    "tablename": table_name,
                    "colname": column_name,
                }
                set_loader_params(loader_params)
        st.session_state['loader_type'] = 'Database'
         
    return None