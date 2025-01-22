import streamlit as st
import configparser
import json
import ollama 
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_community.vectorstores import OracleVS
from langchain_community.embeddings.oracleai import OracleEmbeddings
from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate
import utils.common_db_operations as db_ops



# read enviroment from  .env
config = configparser.ConfigParser()
config.read(".env")

def get_selected_distance():
    if (selected_distance_method):
        match selected_distance_method:
            case "COSINE":
                distance_strategy=DistanceStrategy.COSINE
                return distance_strategy
            case "DOT_PRODUCT":
                distance_strategy=DistanceStrategy.DOT_PRODUCT
                return distance_strategy
            case "EUCLIDEAN_DISTANCE":
                distance_strategy=DistanceStrategy.EUCLIDEAN_DISTANCE
                return distance_strategy
            case "JACCARD":
                distance_strategy=DistanceStrategy.JACCARD
                return distance_strategy
            case "MAX_INNER_PRODUCT":
                distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT
                return distance_strategy
            case _:
                st.write("Choose distance method")
                return ""  
    else:
        st.warning("Please Select Distance Method")
        return ""

def rag_search (question):
    PROMPT_TEMPLATE = """
     Answer the question based only on the following context:

     {context}

     ---

     Answer the question based on the above context in markdown format: {question}
     """ 
    # ############################
    if (selected_vector_store and selected_embedding_model and selected_distance_method):
        distance_method=get_selected_distance()
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        connection = st.session_state.conn_vector_user
        proxy=""
        embedder_params = {"provider": "database", "model": selected_embedding_model}
        embedder = OracleEmbeddings(conn=st.session_state.conn_vector_user, params=embedder_params, proxy=proxy)
        ovs = OracleVS(client=connection, embedding_function=embedder, table_name=selected_vector_store, distance_strategy=distance_method)
    else:
        st.warning("Select Vector Store, Embedding Model and Distance Strategy")
        st.stop()
    # Retriever
    retriever = ovs.as_retriever(search_kwargs={"k": 5})
    # Retrieve relevant documents
    documents = retriever.invoke(question)
    # Extract content from retrieved documents
    # including summary may help here check this 
    doc_texts = "\\n".join([doc.page_content for doc in documents])
    # ##########################
    prompt = prompt_template.format(context=doc_texts, question=question)    
    return prompt

from pathlib import Path

def is_docker():
    cgroup = Path('/proc/self/cgroup')
    return Path('/.dockerenv').is_file() or cgroup.is_file() and 'docker' in cgroup.read_text()

def generate_text_with_ollama(input_sentence, chat_history,llm_model):
    #if ollama is in a separate docker or in docker host
    if is_docker():    
        olc = ollama.Client().Client("http://host.docker.internal:11434")
        stream = olc.chat(
        model=llm_model,
        messages=[{'role': 'user', 'content': input_sentence}],
        stream=True
        )
    else:
        stream = ollama.chat(
        model=llm_model,
        messages=[{'role': 'user', 'content': input_sentence}],
        stream=True
        )
    for chunk in stream:
        yield chunk['message']['content']


with st.sidebar:
    Oracle_RAG = st.checkbox('Enable RAG Using Oracle 23ai Database')
    if Oracle_RAG:
        Top_key = st.number_input('Top Closest Documents    ',value=4)
        st.write('Number of Document from Database : ', str(Top_key))
        st.write("")
        selected_embedding_model = st.selectbox(
            "Embedding Model",
            (db_ops.get_embedding_models_list()),
            index=None,
            placeholder="Select embedding model...",
        )
        st.write("")
        st.write("")
        selected_distance_method = st.selectbox(
            "Distance Strategy ",
            ("COSINE","DOT_PRODUCT","EUCLIDEAN_DISTANCE","JACCARD","MAX_INNER_PRODUCT"),
            index=None,
            placeholder="Select distance method...",help="Choose your metric according to your embedding model, For the details of the Distance Metrics https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/vector-distance-metrics.html"
        )
        st.write("")
        st.write("")
        selected_vector_store = st.selectbox(
            "Vector Stores",
            (db_ops.get_vector_stores_list()),
            index=None,
            placeholder="Select vector store...",
        )

    
if Oracle_RAG:
    st.markdown("##### LLM Chatbot using RAG with Oracle 23ai Database")
else :
    st.markdown("##### LLM Chatbot using Ollama")

    
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
            imput_question_plus_chunk = rag_search(prompt)
        else :
            imput_question_plus_chunk=prompt
        for message in st.session_state.messages:
            chat_history.append(message)

        #message history that came only from role user and not from Admin user , but we can add also it
        user_cht_history = [message for message in chat_history if message["role"] == "user"]

        #convert message into json 
        chat_history_string = json.dumps(user_cht_history)

        #add history 
        imput_question_plus_chunk+=chat_history_string
        print(chat_history_string)
        response = st.write_stream(generate_text_with_ollama(imput_question_plus_chunk , chat_history, st.session_state.llm))
# Add assistant response to chat history
if prompt is not  None:
    st.session_state.messages.append({"role": "assistant", "content": response})       