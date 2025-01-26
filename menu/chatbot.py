import streamlit as st
import configparser
import json
import ollama 
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_community.vectorstores import OracleVS
from langchain_community.embeddings.oracleai import OracleEmbeddings
from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate
from utils.model_distance_selector import selector_form


# read enviroment from  .env
config = configparser.ConfigParser()
config.read(".env")


def rag_search (question):
    PROMPT_TEMPLATE = """
     Answer the question based only on the following context:

     {context}

     ---

     Answer the question based on the above context in markdown format: {question}
     """ 
    # ############################
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    connection = st.session_state.conn_demo_user
    proxy=""
    embedder_params = {"provider": "database", "model": st.session_state.embedding_model}
    embedder = OracleEmbeddings(conn=st.session_state.conn_demo_user, params=embedder_params, proxy=proxy)
    ovs = OracleVS(client=connection, embedding_function=embedder, table_name=st.session_state.vector_store, distance_strategy=st.session_state.distance_metric)
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



def generate_text_with_ollama(input_sentence, chat_history,llm_model):
    #if ollama is in a separate docker or in docker host
    if (st.session_state.is_docker == "True"):    
        olc = ollama.Client("http://host.docker.internal:11434")
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
        with st.sidebar:
            user_input = selector_form()

    
if Oracle_RAG:
    st.markdown("##### LLM Chatbot using RAG with Oracle 23ai")
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