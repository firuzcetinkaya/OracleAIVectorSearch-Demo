import streamlit as st
import utils.db_connection as db 
import utils.common_db_operations as db_ops
from langchain_community.vectorstores import OracleVS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_community.embeddings.oracleai import OracleEmbeddings
import pandas as pd
#defne 5d
st.write("##### Oradefnecle 23ai Similarity Search (Semantic Search) ")
api=st.radio(
            " ",
            ["Langchain", "SQL","LlamaIndex"],
            captions=["Langchain API","SQL API","LlamaIndex API"],
            horizontal=True,
            index=0
            )

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
                st.warning("Please Select Distance Method")
                return ""
    else:
        st.warning("Please Select Distance Method")
        return ""

# some of them are not implemented and some of them are doing similarity search with embedding
# 
#all_similarity_search_methods=['search','similarity_search','similarity_search_with_score','similarity_search_with_relevance_scores',
#'similarity_search_by_vector','similarity_search_by_vector_with_relevance_scores','similarity_search_by_vector_returning_embeddings',    
#'max_marginal_relevance_search','max_marginal_relevance_search_by_vector','max_marginal_relevance_search_with_score_by_vector']
#similarity_search_methods=['search','similarity_search','similarity_search_with_score','similarity_search_with_relevance_scores',   
#'max_marginal_relevance_search']



vscol, embcol,discol = st.columns(3)
with vscol:
    selected_vector_store = st.selectbox(  
        "Vector Store",
        db_ops.get_vector_stores_list(),
        index=None,
        placeholder="Select Vector Store ...",
        )
with embcol:
    selected_embedding_model = st.selectbox(
        "Embedding Model",
        (db_ops.get_embedding_models_list()),
        index=None,
        placeholder="Select embedding model...",
        )
with discol:
    selected_distance_method = st.selectbox(
        "Distance Strategy ",
        ("COSINE","DOT_PRODUCT","EUCLIDEAN_DISTANCE","JACCARD","MAX_INNER_PRODUCT"),
        index=None,
        placeholder="Select distance method...",help="Choose your metric according to your embedding model, For the details of the Distance Metrics https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/vector-distance-metrics.html"
    )
if (selected_vector_store and selected_embedding_model and selected_distance_method):
    distance_method=get_selected_distance()
    proxy=""
    embedder_params = {"provider": "database", "model": selected_embedding_model}
    embedder = OracleEmbeddings(conn=st.session_state.conn_vector_user, params=embedder_params, proxy=proxy)
    OracleVS = OracleVS(client=st.session_state.conn_vector_user,table_name=selected_vector_store,embedding_function=embedder,distance_strategy=distance_method) 
else:
    st.warning("Select Vector Store, Embedding Model and Distance Strategy")
query_text = st.text_area(
"Enter your query :",
"",
placeholder="query..."
)

m1,m2 = st.columns(2,gap='medium')
with m1:
    #similarity_search_method = st.pills("Select Similarity Search Method", similarity_search_methods, selection_mode="single")
    similarity_search_method = st.radio(
            "Similarity Search Method",
            ['Similarity Search','Similarity Search with Relevance Threshold','Max Marginal Relevance Search'],
            captions=[
                "Returns most similar docs.",
                "Returns most similar docs with relevance scores",
                "Returns most similar docs by maximal marginal relevance.",
            ],horizontal=True,index=0,
            help="For the Oracle Split Example visit https://python.langchain.com/v0.2/docs/integrations/document_loaders/oracleai/#split-documents"
        )
with m2:
    if (similarity_search_method):
        match similarity_search_method:
            case "Similarity Search":
                st.checkbox("Use filter")
                k = st.slider("k", 1, 10, 4,help="Amount of documents to return (Default: 4)") 
            case "Similarity Search with Relevance Threshold":
                st.checkbox("Use filter")                
                k = st.slider("k", 1, 10, 4,help="Amount of documents to return (Default: 4)") 
                score_threshold=st.slider("score_threshold", 0.00, 1.00, 0.90,help="Minimum relevance threshold; Only retrieve documents that have a relevance score above a certain threshold")
            case "Max Marginal Relevance Search":
                st.checkbox("Use filter")
                k = st.slider("k", 1, 10, 4,help="Amount of documents to return (Default: 4)") 
                fetch_k = st.slider("fetch_k", 1, 100, 20, help="Amount of documents to pass to MMR algorithm; (Default: 20)") 
                lambda_mult = st.slider("lambda_mult", 0.0, 1.0, 0.5,help="Diversity of results returned by MMR; 1 for minimum diversity and 0 for maximum. (Default: 0.5)")
                
#  Document(metadata={'SOURCE MIME TYPE': 'application/pdf', 'creation date': '9/23/2024 12:44:46 PM', 
#  'author': 'Microsoft Office User', 'revision date': '9/23/2024 12:44:46 PM', 
#  'Creator': '\rMicrosoft® Word 2016', 'publisher': 'Microsoft® Word 2016', 
#  '_oid': '674db350ff14cdb19fa16b5acc350db1', '_file': './Data/6 Yas 2. Unite Veli Mektubu.pdf', 
#  'id': '9', 'document_id': '1', 'document_summary':'...'}, 
#  page_content='unit from the posts we will share at the end of each theme on social media.')

if st.button("Search Vector Store"):
    if (similarity_search_method):
        match similarity_search_method:
            case "Similarity Search":
                #search_kwargs={'filter': {'paper_title':'GPT-4 Technical Report'}}
                search_kwargs={'k': k} 
                retriever = OracleVS.as_retriever(search_kwargs=search_kwargs)
                document_list=retriever.invoke(input=query_text,search_kwargs=search_kwargs)
                cols = ['Chunk Id','Doc Id','File Name','Content','Doc Summary']
                rows = []
                for d in document_list: 
                    row = [d.metadata['id'],d.metadata['document_id'],d.metadata['_file'],d.page_content,d.metadata['document_summary']]
                    rows.append(row)
                docs = pd.DataFrame(rows, columns = cols)
                st.dataframe(docs)
            case "Similarity Search with Relevance Threshold":
                search_type='similarity_score_threshold'
                search_kwargs={'k': k,'score_threshold': score_threshold} 
                retriever = OracleVS.as_retriever(search_type=search_type,search_kwargs=search_kwargs)
                document_list=retriever.invoke(input=query_text,search_kwargs=search_kwargs)
                cols = ['Chunk Id','Doc Id','File Name','Content','Doc Summary']
                rows = []
                for d in document_list: 
                    row = [d.metadata['id'],d.metadata['document_id'],d.metadata['_file'],d.page_content,d.metadata['document_summary']]
                    rows.append(row)
                docs = pd.DataFrame(rows, columns = cols)
                st.dataframe(docs)
            case "max_marginal_relevance_search":
                search_type='mmr'
                search_kwargs={'k': k,'fetch_k': fetch_k,'lambda_mult':lambda_mult} 
                retriever = OracleVS.as_retriever(search_type=search_type,search_kwargs=search_kwargs)
                document_list=retriever.invoke(input=query_text,search_kwargs=search_kwargs)
                cols = ['Chunk Id','Doc Id','File Name','Content','Doc Summary']
                rows = []
                for d in document_list: 
                    row = [d.metadata['id'],d.metadata['document_id'],d.metadata['_file'],d.page_content,d.metadata['document_summary']]
                    rows.append(row)
                docs = pd.DataFrame(rows, columns = cols)
                st.dataframe(docs)
    else:
        st.warning("Please Select Similarity Search Method")
        st.stop()