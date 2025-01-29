import streamlit as st
from langchain_community.vectorstores import oraclevs
from langchain_community.vectorstores import OracleVS
from langchain_community.embeddings.oracleai import OracleEmbeddings

def create_vector_index():
    proxy=""
    embedder_params = {"provider": "database", "model": st.session_state.embedding_model}
    embedder = OracleEmbeddings(conn=st.session_state.conn_demo_user, params=embedder_params, proxy=proxy)
    vector_store = OracleVS(client=st.session_state.conn_demo_user,table_name=st.session_state.vector_store,embedding_function=embedder,distance_strategy=st.session_state.distance_metric) 

    if st.session_state.index_type=="IVF":
        oraclevs.create_index(client=st.session_state.conn_demo_user,vector_store=vector_store, params={
                "idx_name": st.session_state.new_vector_index_name, "idx_type": "IVF"
            })
    elif st.session_state.index_type=="HNSW":
        oraclevs.create_index(client=st.session_state.conn_demo_user,vector_store=vector_store, params={
                "idx_name": st.session_state.new_vector_index_name, "idx_type": "HNSW"
            })
    elif st.session_state.index_type=="Hybrid":
        oraclevs.create_index(client=st.session_state.conn_demo_user,vector_store=vector_store, params={
                "idx_name": "hnsw"+st.session_state.vector_store, "idx_type": "HNSW"
            })
        
        #CREATE HYBRID VECTOR INDEX my_hybrid_idx on ccnews(info) PARAMETERS ('model doc_model') parallel 8;
        #CREATE HYBRID VECTOR INDEX my_hybrid_idx_hnsw on ccnews_1(info) PARAMETERS ('model doc_model vector_idxtype HNSW') parallel 8;
    else:
        st.warning("Please Select an Index Type")
    
def index_main_form():    
    #default values
    if 'accuracy' not in st.session_state:
        st.session_state['accuracy'] = "90"  
    if 'neighbors' not in st.session_state:
        st.session_state['neighbors'] = "8"
    if 'parallel' not in st.session_state:
        st.session_state['parallel'] = "8"
    if 'efConstruction' not in st.session_state:
        st.session_state['efConstruction'] = "100"
    if 'neighbor_partitions' not in st.session_state:
        st.session_state['neighbor_partitions'] = "8"
    if 'index_type' not in st.session_state:
        st.session_state['index_type'] = "HNSW"
    
    
    def set_index_type():
        st.session_state['index_type'] = index_type          

    index_type = st.radio(
        "Select Your Index Type",
        ["HNSW", "IVF", "Hybrid"],
        captions=[
            "HNSW Index",
            "IVF Index",
            "Hybrid Index",
        ],horizontal=True, 
        index=0,
        on_change=set_index_type,
        help="For the Oracle Vector Indexing Details visit https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/guidelines-using-vector-indexes.html"
        )

    return None


def index_parameters_form():    
    #default values

    def set_accuracy():
        st.session_state['accuracy'] = accuracy          
    def set_neighbors():
        st.session_state['neighbors'] = neighbors
    def set_parallel():
        st.session_state['parallel'] = parallel 
    def set_ef_construction():
        st.session_state['efConstruction'] = efConstruction 
    def set_neighbor_partitions():
        st.session_state['neighbor_partitions'] = neighbor_partitions 


    if st.session_state.index_type=="HNSW":
        #if hnsw index
        accuracy = st.slider(
            "Accuracy", 0, 100, 90,
            on_change=set_accuracy,
            help="Target accuracy at which the approximate search should be performed when running an approximate search query using vector indexes.")            
        neighbors=st.slider(
            "neighbors", 0, 2048, 8,
            on_change=set_neighbors,
            help="Neighbors.") 
        #NEIGHBORS and M are equivalent and represent the maximum number of neighbors a vector can have on any layer. The last vertex has one additional flexibility that it can have up to 2M neighbors.  
        parallel=st.slider(
            "Parallel", 0, 64, 8,
            on_change=set_parallel,
            help="Parallel Option may bring soe performance gains if your system supports.")   
        efConstruction=st.slider(
            "efConstruction", 0, 65535, 100,
            on_change=set_ef_construction,
            help="efConstruction.")   # only for HNSW, EFCONSTRUCTION represents the maximum number of closest vector candidates considered at each step of the search during insertion.                    
        index_params = ""
    elif st.session_state.index_type=="IVF":
        #if ivf index
        accuracy = st.slider(
            "Accuracy", 0, 100, 90,
            on_change=set_accuracy,
            help="Target accuracy at which the approximate search should be performed when running an approximate search query using vector indexes.")            
        neighbor_partitions=st.slider(
            "Parallel", 0, 10000000, 8,
            on_change=set_neighbor_partitions,
            help="Neigbors.")   
        #SAMPLE_PER_PARTITION: from 1 to (num_vectors/neighbor_partitions)
        #MIN_VECTORS_PER_PARTITION: from 0 (no trimming of centroid partitions) to total number of vectors (would result in 1 centroid partition)    
        parallel=st.slider(
            "Parallel", 0, 64, 8,
            on_change=set_parallel,
            help="Parallel Option may bring soe performance gains if your system supports.")   
        #SAMPLE_PER_PARTITION: from 1 to (num_vectors/neighbor_partitions)
        #MIN_VECTORS_PER_PARTITION: from 0 (no trimming of centroid partitions) to total number of vectors (would result in 1 centroid partition)    
        index_params = ""
    elif st.session_state.index_type== "Hybrid":
        index_params = {}
        st.write("Hybrid Indexes will be implemented.")
    else:
        st.write("You didn't select any Index Type.")
        st.stop()

    return None