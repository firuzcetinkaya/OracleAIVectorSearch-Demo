import streamlit as st
from langchain_core.documents import Document
from langchain_community.vectorstores import OracleVS
import utils.model_distance_selector as model_distance_selector
import vector_operations.load as vecops_load
import vector_operations.split as vecops_split
import vector_operations.summary as vecops_summary
import vector_operations.index as vecops_index
import vector_operations.embed as vecops_embed
from utils.remove_loaded_files import rm_files as remove_loaded_files
import pandas as pd

def load_split_embed_docs(loader,splitter,summary,embedder):

    #""" load the docs """
    docs = loader.load()
    st.write(f"Number of docs loaded: {len(docs)}")
    doc_origin = Document
    max_lengh_oracle_allow=9000
    counter = 0  
    document_num = 0
    chunks_with_mdata = []
    cols = ['Chunk Id','Doc Id','Chunk Content']
    rows = []
    for id, doc in enumerate(docs, start=1):
        #remove line break from the text document
        doc.page_content = doc.page_content.replace("\n", "")
        doc_origin.page_content = doc.page_content
        
        # summary part for each doc
        # check the doc
        if len(doc.page_content)>max_lengh_oracle_allow :
            #reduce the text to max_lengh_oracle_allow
            doc.page_content = doc.page_content[:9000]
        # get the summary
        summ = summary.get_summary(doc) 
        document_num += 1
        #st.write(doc.metadata["_file"])
        #st.write(summ)
        
        # splitter part for each doc  
        # chunk the doc
        chunks = splitter.split_text(doc_origin.page_content)
        #st.write(f"Doc {id}: chunks# {len(chunks)}")
        
        #For each chunk create chunk_metadata with summary or keep summary somewhere else, but use the summary in RAG
        # this is going to be used in the embedding 
        # for docid chunkid etc
        for ic, chunk in enumerate(chunks, start=1):
            counter += 1  
            chunk_metadata = doc.metadata.copy()  
            chunk_metadata['id'] = str(counter)  
            chunk_metadata['document_id'] = str(document_num)
            chunk_metadata['document_summary'] = str(summ[0])
            chunks_with_mdata.append(Document(page_content=str(chunk), metadata=chunk_metadata))
            #st.write(f"Doc {id}: metadata: {doc.metadata}")
        for info in chunks_with_mdata:
            i=1    
            row = [info.metadata['id'],info.metadata['document_id'],info.page_content]
            rows.append(row)
    docs = pd.DataFrame(rows, columns = cols)
    st.dataframe(docs)
               
    #===count number of documents
    unique_files = set()
    for chunk in chunks_with_mdata:
        file_name = chunk.metadata['_file']
        unique_files.add(file_name)
        
    st.write("Total number of documents:", len(unique_files))
    return chunks_with_mdata




def load_split_embed_docs_from_db(loader,splitter,summary,embedder):
    docs = loader.load()
    st.write(f"Number of docs loaded: {len(docs)}")
    chunks_with_mdata = []
    for id, doc in enumerate(docs, start=1):
        summ = summary.get_summary(doc.page_content)
        chunks = splitter.split_text(doc.page_content)
        for ic, chunk in enumerate(chunks, start=1):
            chunk_metadata = doc.metadata.copy()
            chunk_metadata["id"] = chunk_metadata["_oid"] + "$" + str(id) + "$" + str(ic)
            chunk_metadata["document_id"] = str(id)
            chunk_metadata["document_summary"] = str(summ[0])
            chunks_with_mdata.append(
                Document(page_content=str(chunk), metadata=chunk_metadata)
            )
    return chunks_with_mdata

@st.dialog("Preferences",width="large")
def show_embedding_dialog():
    if st.checkbox("Create New Table"):
        table_name=st.text_input("New Table Name","TBL_"+st.session_state.distance_metric+"_",placeholder="Please enter tablename")
        st.session_state["new_vector_table_name"]=table_name
    model_distance_selector.selector_form()
    if st.checkbox("Show Additional Parameters"):
        with st.expander("Document Embedder Parameters",expanded=False):  
            vecops_embed.embed_parameters_form()                    
        with st.expander("Document Splitter Parameters",expanded=False):  
            vecops_split.split_parameters_form()                    
        with st.expander("Document Summary Parameters",expanded=False):
            vecops_summary.summary_parameters_form()
    if st.button("Run"):
        st.session_state['run_embedding_process']='True'  
        st.rerun()    


@st.dialog("Index Preferences",width="large")
def show_index_dialog():
    index_name=st.text_input("New Index Name","IND_"+st.session_state.index_type+"_"+st.session_state.vector_store+"_",placeholder="Please enter index name")
    st.session_state["new_vector_index_name"]=index_name
    model_distance_selector.selector_form()
    if st.checkbox("Show Index Parameters"):
        vecops_index.index_parameters_form()
    if st.button("Execute"):
        st.session_state['run_indexing_process']='True'  
        st.rerun()  


tab1, tab2 = st.tabs(["Create Vector Embeddings", "Create Vector Index"])
with tab1:
    vecops_load.load_parameters_form()       
    if st.button("Load & Create Vectors","CreateVectors"):
        show_embedding_dialog()
    
    if 'run_embedding_process' not in st.session_state:
        st.session_state['run_embedding_process']='False'
        
    if st.session_state.run_embedding_process=='True': 
        st.session_state['run_embedding_process']='False'
        loader=vecops_load.create_loader()
        splitter=vecops_split.create_splitter()
        summary=vecops_summary.create_summarizer()
        embedder=vecops_embed.create_embedder()
        if (st.session_state.loader_type=='Database'):
            documents=load_split_embed_docs_from_db(loader,splitter,summary,embedder)
        else:
            documents=load_split_embed_docs(loader,splitter,summary,embedder)

        vector_store = OracleVS.from_documents(documents=documents, embedding=embedder, client=st.session_state.conn_demo_user, table_name=st.session_state.new_vector_table_name, distance_strategy=st.session_state.distance_metric)
        remove_loaded_files()
        if vector_store is not None:
            st.success("\n Vector Store Created.\n")
        else:
            print("\nFailed to get the VectorStore populated.\n")
        

with tab2:
    vecops_index.index_main_form()
    if st.button("Create Vector Index","CreateIndex"):    
        show_index_dialog()

    if 'run_indexing_process' not in st.session_state:
        st.session_state['run_indexing_process']='False'

    if st.session_state.run_indexing_process=='True': 
        st.session_state['run_indexing_process']='False'
        vecops_index.create_vector_index() 

