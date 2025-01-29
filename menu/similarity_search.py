import streamlit as st
from langchain_community.vectorstores import OracleVS
from langchain_community.embeddings.oracleai import OracleEmbeddings
import pandas as pd
import utils.model_distance_selector as model_distance_selector
import similarity_search.search as search

st.write("##### Similarity Search (Semantic Search) ")


def run_search():
    proxy=""
    embedder_params = {"provider": "database", "model": st.session_state.embedding_model}
    embedder = OracleEmbeddings(conn=st.session_state.conn_demo_user, params=embedder_params, proxy=proxy)
    vec_store = OracleVS(client=st.session_state.conn_demo_user,table_name=st.session_state.vector_store,embedding_function=embedder,distance_strategy=st.session_state.distance_metric) 
    if st.session_state.search_method=="Similarity Search":
        #search_kwargs={'filter': {'paper_title':'GPT-4 Technical Report'}}
        search_kwargs={'k': st.session_state.k} 
        if st.session_state.use_filter=="True":
            document_list=vec_store.similarity_search(query_text,filter=st.session_state.filter_criteria,search_kwargs=search_kwargs)
        else:
            document_list=vec_store.similarity_search(query_text, search_kwargs=search_kwargs)
    elif st.session_state.search_method=="Search with Relevance Threshold":
        search_kwargs={'k': st.session_state.k,'score_threshold': st.session_state.score_threshold} 
        if (st.session_state.use_filter=="True"):
            document_list=vec_store.similarity_search_with_score(query_text,filter=st.session_state.filter_criteria, search_kwargs=search_kwargs)
        else:
            document_list=vec_store.similarity_search_with_score(query_text, search_kwargs=search_kwargs)
    elif st.session_state.search_method=="MMR Search":
        search_kwargs={'k': st.session_state.k,'fetch_k': st.session_state.fetch_k,'lambda_mult':st.session_state.lambda_mult} 
        if (st.session_state.use_filter=="True"):
            document_list=vec_store.max_marginal_relevance_search(query_text,filter=st.session_state.filter_criteria,search_kwargs=search_kwargs)
        else:
            document_list=vec_store.max_marginal_relevance_search(query_text, search_kwargs=search_kwargs)
    else:
        st.warning("Select Search Method")       
        st.stop()

    #  Returned document structure, if with score
    #    
    #  Document(metadata={'SOURCE MIME TYPE': 'application/pdf', 'creation date': '9/23/2024 12:44:46 PM', 
    #  'author': 'Microsoft Office User', 'revision date': '9/23/2024 12:44:46 PM', 
    #  'Creator': '\rMicrosoft® Word 2016', 'publisher': 'Microsoft® Word 2016', 
    #  '_oid': '674db350ff14cdb19fa16b5acc350db1', '_file': './Data/docs/test.pdf', 
    #  'id': '9', 'document_id': '1', 'document_summary':'...'}, 
    #  page_content='unit from the posts we will share at the end of each theme on social media.'),0.455522
    if st.session_state.search_method=="Search with Relevance Threshold":
        cols = ['Score','Chunk Id','Doc Id','File Name','Content','Doc Summary']
        rows = []
        for d,s in document_list: 
            row = [s,d.metadata['id'],d.metadata['document_id'],d.metadata['_file'],d.page_content,d.metadata['document_summary']]
            rows.append(row)
        docs = pd.DataFrame(rows, columns = cols)
        st.dataframe(docs)
    else:
        cols = ['Chunk Id','Doc Id','File Name','Content','Doc Summary']
        rows = []
        for d in document_list: 
            row = [d.metadata['id'],d.metadata['document_id'],d.metadata['_file'],d.page_content,d.metadata['document_summary']]
            rows.append(row)
        docs = pd.DataFrame(rows, columns = cols)
        st.dataframe(docs)

@st.dialog("Search Preferences",width="large")
def show_search_dialog():
    model_distance_selector.selector_form()
    params=st.checkbox("Show Search Parameters")
    if params:
        search.search_params_form()
    ok = st.button("OK")
    if ok:
        st.session_state['run_searching_process']='True'  
        st.rerun()  



search.search_main_form()

query_text = st.text_area(
"Enter your query :",
"",
placeholder="query..."
)

  
if st.button("Search"):
    show_search_dialog()
    
if 'run_searching_process' not in st.session_state:
        st.session_state['run_searching_process']='False'
        
if (st.session_state.run_searching_process=='True'): 
    st.session_state['run_searching_process']='False'
    run_search()       