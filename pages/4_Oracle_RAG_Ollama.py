import streamlit as st
import random
import time
from dotenv import load_dotenv
import os
import oracledb
import configparser
import json
import ollama 
from langchain_community.vectorstores.utils import DistanceStrategy

# read enviroment from  .env
config = configparser.ConfigParser()
config.read(".env")

oracle_user = config["DATABASE"]["USERNAME"]
oracle_password = config["DATABASE"]["PASSWORD"]
oracle_hostname = config["DATABASE"]["HOST"]
oracle_port = config["DATABASE"]["PORT"]
oracle_service_name = config["DATABASE"]["SERVICE_NAME"]
tab_name = config["DATABASE"]["TABLE_NAME_CV_LANG"]


#distance_strategy="DOT_PRODUCT"         #DOT
distance_strategy="MAX_INNER_PRODUCT"    #COSINE
#distance_strategy="EUCLIDEAN_DISTANCE"  #EUCLIDEAN

#tab_name = tab_name+'_'+distance_strategy

if distance_strategy == DistanceStrategy.EUCLIDEAN_DISTANCE:
  distance_function = 'EUCLIDEAN'
elif distance_strategy == DistanceStrategy.DOT_PRODUCT:
  distance_function = 'DOT'
elif distance_strategy == DistanceStrategy.MAX_INNER_PRODUCT:
  distance_function = 'COSINE'

tab_name = tab_name+'_'+distance_function

try:
    OLLAMA_MODELS = ollama.list()["models"]
except Exception as e:
    st.warning("Please make sure Ollama is installed first. See https://ollama.ai for more details.")
    st.stop()
    

def assert_models_installed():
    if len(OLLAMA_MODELS) < 1:
        st.sidebar.warning("No models found. Please install at least one model e.g. `ollama run llama2`")
        st.sidebar.warning("Visit https://ollama.com/library for available models")
        st.stop()


def select_model():    
    model_names = [model["name"] for model in OLLAMA_MODELS]   
    st.sidebar.warning("for additional models please visit https://ollama.com/library ")
    llm_name = st.sidebar.selectbox(f"Choose LLM (locally available {len(model_names)})", [""] + model_names)
    if llm_name:
        # llm details object
        llm_details = [model for model in OLLAMA_MODELS if model["name"] == llm_name][0]
        # convert size in llm_details from bytes to GB (human-friendly display)
        if type(llm_details["size"]) != str:
            llm_details["size"] = f"{round(llm_details['size'] / 1e9, 2)} GB"
        # display llm details
        with st.expander("LLM Details"):
            st.write(llm_details)
        return llm_name
    
def rag_search (prompt_question_corret, k_top):
    print("connecting...  to Oracle Database")
    print(oracle_user)
    connection = oracledb.connect(
    user=oracle_user,
    password=oracle_password,
    dsn=oracle_hostname+":"+oracle_port+"/"+oracle_service_name
    )
    cursor = connection.cursor()

    print("connected to Oracle Database")
    #query to find the closest vector embeding related input question vector
    sql1 = """select  TO_CHAR(vector_distance(EMBEDDING,(select json_value(COLUMN_VALUE, '$.embed_vector' RETURNING clob) 
                                                              from dbms_vector.UTL_TO_EMBEDDINGS(:prompt_question_corret,
                                                            json('{"provider":"database", "model": "DOC_MODEL"}'))
                                                            ),"""+distance_function+""" 
                                              ),'9.99999999999999999999999999999999999999') Distance
               ,text|| ' summary :'||json_value(METADATA,'$.document_summary'),
                substr(json_value(METADATA,'$._file'),instr(json_value(METADATA,'$._file'),'/',-1))     
  from """ +tab_name+""" where 
  vector_distance(EMBEDDING,(select json_value(COLUMN_VALUE, '$.embed_vector' RETURNING clob) 
from 
  dbms_vector.UTL_TO_EMBEDDINGS(:prompt_question_corret,
    json('{"provider":"database", "model": "DOC_MODEL"}') )),"""+distance_function+""" )
order by vector_distance(EMBEDDING,(select json_value(COLUMN_VALUE, '$.embed_vector' RETURNING clob) 
from 
  dbms_vector.UTL_TO_EMBEDDINGS(:prompt_question_corret,
    json('{"provider":"database", "model": "DOC_MODEL"}') )),"""+distance_function+""" ) 
FETCH FIRST :k_top ROWS ONLY
"""

    bind_values = {"prompt_question_corret": prompt_question_corret,"k_top":k_top}  # Map placeholders to values
    with connection.cursor() as cursor:
            cursor.execute(sql1,bind_values)
            rows = cursor.fetchall()

    # Generate the answer using chunk obtained from the database 
    input_sentence ='Answer this question : "' + prompt_question_corret  + '" based solely on this information  :  ' ;
    for i in range(len(rows)):
        input_sentence += str(rows[i][1])+' and  '
    File_rif='File  Ref : \n'
    seen_values = set()
    for row in rows:
        value = row[2]
        if value not in seen_values:
            File_rif += "\n --"+ value + '\n'
            seen_values.add(value)
    chunk_info= 'Chunk info : \n '
    for i in range(len(rows)):
        chunk_info += '\n Distance : '+rows[i][0]+ ' Chunk : '+str(rows[i][1])+' \n ************* \n'        
    print(input_sentence)
    print(File_rif)
    return input_sentence,File_rif,chunk_info


def generate_text_ollama(input_sentence, chat_history,llm_model):
    stream = ollama.chat(
    model=llm_model,
    messages=[{'role': 'user', 'content': input_sentence}],
    stream=True
    )
    for chunk in stream:
        yield chunk['message']['content']


with st.sidebar:
    llm_name = select_model()    
    assert_models_installed()    
    if not llm_name: st.stop()
    Oracle_RAG = st.checkbox(':o2: USe Oracle Database to RAG ')
    if Oracle_RAG:
        Top_key = st.number_input('Top Closest Documents    ',value=4)
        st.write('Number of Document from Database : ', Top_key)

    
if Oracle_RAG:
    st.header(":robot_face: LLM Chatbot using RAG :red[Oracle] Database 💬")
else :
    st.header(":robot_face: LLM Chatbot 💬")

    
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask somenthing."):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

# Display assistant response in chat message container
with st.chat_message("assistant"):
    chat_history=[]
    if prompt is not  None:
        if Oracle_RAG:
            imput_question_plus_chunk,File_rif,chunk_info = rag_search(prompt,Top_key)
            with st.sidebar:
                st.write("    ")
                st.write("    ")
                st.write("    ")
                st.write(File_rif)
                st.write("    ")
                st.write("    ")
                st.write("*************    ")                
                ""+chunk_info+""
                #"[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"
        else :
            imput_question_plus_chunk=prompt
        #response = st.write_stream(generate_text(prompt,compartment_id))
        for message in st.session_state.messages:
            #print ("******")
            #print (message)
            #print ("******")
            chat_history.append(message)

        #message history that came only from role user and not from Admin user , but we can add also it
        user_cht_history = [message for message in chat_history if message["role"] == "user"]

        #convert message into json 
        chat_history_string = json.dumps(user_cht_history)

        #add history 
        imput_question_plus_chunk+=chat_history_string
        print(chat_history_string)
        #response = st.write_stream(generate_text(imput_question_plus_chunk  ,compartment_id,chat_history))
        response = st.write_stream(generate_text_ollama(imput_question_plus_chunk , chat_history,llm_model))
# Add assistant response to chat history
if prompt is not  None:
    st.session_state.messages.append({"role": "assistant", "content": response})       