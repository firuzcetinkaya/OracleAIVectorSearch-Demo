import sys
import json
import oracledb
import configparser
import streamlit as st
import os
from langchain_core.documents import Document
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_community.vectorstores import oraclevs
from langchain_community.vectorstores import OracleVS
from langchain_community.document_loaders import oracleai
from langchain_community.utilities.oracleai import OracleSummary
from langchain_community.embeddings.oracleai import OracleEmbeddings
from langchain_community.document_loaders.oracleai import OracleTextSplitter 
from langchain_community.document_loaders.oracleai import OracleDocLoader 

# stages 0,1,2,3,4,5
# 

if 'stage' not in st.session_state:
    st.session_state.stage = 0

def set_state(i):
    st.session_state.stage = i

try:
    connection = oracledb.connect(user=st.session_state.username, password=st.session_state.password, dsn=st.session_state.dsn)
    print("\nConnection successful!\n")
except Exception as e:
    print(e)
    print("\nConnection failed!\n")
    sys.exit(1)#
    
def generate_embedding_models_list():
    #query to find the vector embedding models that currently exists in DB
    sql1 = """SELECT model_name, vector_info
    FROM user_mining_model_attributes
    WHERE attribute_type = :atype
    ORDER BY model_name
    """
    with connection.cursor() as cursor:
                cursor.execute(sql1,atype="VECTOR")
                rows = cursor.fetchall()            
    embedding_models_list=[row[0] for row in rows]
    return embedding_models_list


with st.sidebar:
    selected_embedding_model=""
    selected_embedding_model = st.selectbox(
        "Select an Embedding Model stored in Oracle DB.",
        (generate_embedding_models_list()),
        index=None,
        placeholder="Select embedding model...",on_change=set_state,args=[1]
    )
    st.page_link("pages/1_Load_Embedding_Model.py", label="Load a new embedding model")
    selected_distance_method=""
    selected_distance_method = st.selectbox(
        "Select the Distance Strategy (Choose according to your embedding model)",
        ("COSINE","DOT_PRODUCT","EUCLIDEAN_DISTANCE","JACCARD","MAX_INNER_PRODUCT"),
        index=None,
        placeholder="Select distance method...",on_change=set_state,args=[2],help="For the details of the Distance Metrics https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/vector-distance-metrics.html"
    )
    
    
tab1, tab2, tab3, tab4 = st.tabs(["Loader & Splitter (Chunking)", "Summary", "Embedder", "Indexing"])
with tab1:
    #Loader and Splitter
    #st.markdown("You can load your documents via this page")
    #st.write("Please place all your files that you want to create vector embeddings, under Data directory in the working directory of Vector Search App")
    #https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/vector_chunks.html
    if st.session_state.stage < 2:
        st.warning("Please Select Embedding Model and Distance Metric Values!!!")
    else:
        distance_strategy=""
        match selected_distance_method:
            case "COSINE":
                distance_strategy=DistanceStrategy.COSINE
            case "DOT_PRODUCT":
                distance_strategy=DistanceStrategy.DOT_PRODUCT
            case "EUCLIDEAN_DISTANCE":
                distance_strategy=DistanceStrategy.EUCLIDEAN_DISTANCE
            case "JACCARD":
                distance_strategy=DistanceStrategy.JACCARD
            case "MAX_INNER_PRODUCT":
                distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT
            case _:
                set_state(0)

        if selected_embedding_model=="":
            set_state(0)

        table_name = st.session_state.table_name+'_'+distance_strategy
        print("table Name :",table_name)
        
        st.markdown("Loader Parameters")
        localdir=st.session_state.directory
        loader_params = {}        
        # different loaders file, dir, db
        selected_loader_type = st.radio(
            "Select Your Loader Method",
            ["File", "Directory", "Database"],
            captions=[
                "Load a single file",
                "Load all files from a directory",
                "Load docs from Oracle Database Table",
            ],horizontal=True, help="For the Oracle Loader Example visit https://python.langchain.com/v0.2/docs/integrations/document_loaders/oracleai/#load-documents"
        )
        st.markdown("Splitter Parameters")

        by, max, overlap, split_by, language, normalize  = st.columns(6, vertical_alignment="top")
        
 
        by = st.radio(
            "Choose the Split Units",
            ["CHARS", "WORDS", "VOCABULARY"],
            captions=[
                "Load a single file",
                "Load all files from a directory",
                "Load docs from Oracle Database Table",
            ],horizontal=True,help="For the Oracle Split Example visit https://python.langchain.com/v0.2/docs/integrations/document_loaders/oracleai/#split-documents"
        )
        
        if by=="CHARS":
            max = st.slider("Max?", 50, 4000, 400)
        if by=="WORDS":
            max = st.slider("Max?", 10, 1000, 25)
        if by=="VOCABULARY":
            max = st.slider("Max?", 10, 1000, 25)
            
        overlap = st.slider("Overlap?", 5, 20, 0,help="Valid value: 5% to 20% of MAX, Default value: 0") 
        split_by = st.selectbox(
        "Select the Split By method",
        ("NONE","BY NEWLINE","RECURSIVELY","SENTENCE","CUSTOM (Not Implemented in the Demo)"),
        index=None,
        placeholder="Select split by method...",
        )
        #languages from Oracle DB Supported Langs, refine the language list as desired
        all_supported_languages=["ALBANIAN","AMERICAN","AMHARIC","ARABIC","ARMENIAN","ASSAMESE","AZERBAIJANI","BANGLA","BASQUE","BELARUSIAN","BRAZILIAN PORTUGUESE","BULGARIAN","BURMESE","CANADIAN FRENCH","CATALAN","CROATIAN","CYRILLIC KAZAKH","CYRILLIC SERBIAN","CYRILLIC UZBEK","CZECH","DANISH","DARI","DIVEHI","DUTCH","EGYPTIAN","ENGLISH","ESTONIAN","FINNISH","FRENCH","GEORGIAN","GERMAN DIN","GERMAN","GREEK","GUJARATI","HEBREW","HINDI","HUNGARIAN","ICELANDIC","INDONESIAN","IRISH","ITALIAN","JAPANESE","KANNADA","KHMER","KOREAN","KYRGYZ","LAO","LATIN AMERICAN SPANISH","LATIN BOSNIAN","LATIN SERBIAN","LATIN UZBEK","LATVIAN","LITHUANIAN","MACEDONIAN","MALAY","MALAYALAM","MALTESE","MARATHI","MEXICAN SPANISH","NEPALI","NORWEGIAN","ORIYA","PERSIAN","POLISH","PORTUGUESE","PUNJABI","ROMANIAN","RUSSIAN","SIMPLIFIED CHINESE","SINHALA","SLOVAK","SLOVENIAN","SPANISH","SWAHILI","SWEDISH","TAMIL","TELUGU","THAI","TRADITIONAL CHINESE","TURKISH","TURKMEN","UKRAINIAN","URDU","VIETNAMESE"]
        supported_languages=["ALBANIAN","AMERICAN","ARABIC","ARMENIAN","AZERBAIJANI","BULGARIAN","CROATIAN","CZECH","DANISH","DUTCH","EGYPTIAN","ENGLISH","ESTONIAN","FINNISH","FRENCH","GEORGIAN","GERMAN","GREEK","HEBREW","HINDI","HUNGARIAN","ICELANDIC","INDONESIAN","IRISH","ITALIAN","JAPANESE","KOREAN","KYRGYZ","LATVIAN","LITHUANIAN","MACEDONIAN","MALAY","NORWEGIAN","PERSIAN","POLISH","PORTUGUESE","PUNJABI","ROMANIAN","RUSSIAN","SIMPLIFIED CHINESE","SLOVAK","SLOVENIAN","SPANISH","SWAHILI","SWEDISH","TAMIL","THAI","TRADITIONAL CHINESE","TURKISH","TURKMEN","UKRAINIAN","URDU","VIETNAMESE"]
        language = st.selectbox(
        "Select the Language ",
        (supported_languages),
        index=12,
        placeholder="Select language...",
        )
        normalize = st.selectbox(
        "Select the normalization ",
        ("NONE","ALL"),
        index=None,
        placeholder="Select normalization method...",
        )
        
        
        

        if st.button("Load & Chunk Your Document(s)","Loader"):
            
            if selected_loader_type == "File":
                #selected_file = st.file_uploader("Select your files to Create Vector Embeddings:", accept_multiple_files=True)
                #st.write(f"- {file.name}")
                #loader_params['file'] = file.name
                loader_params['file'] = "Data/cv_simplified_en.pdf"
            elif selected_loader_type == "Directory":
                loader_params['dir'] = localdir
            elif selected_loader_type == "Directory":
                loader_params = {
                    "owner": "<owner>",
                    "tablename": "demo_tab",
                    "colname": "data",
                }
            else:
                st.write("You didn't select any Loader Type.")
                st.stop()
            loader = OracleDocLoader(conn=connection, params=loader_params)
            splitter_params = {"BY" :by, "MAX": max, "OVERLAP": overlap, "SPLIT": split_by, "LANGUAGE": language, "NORMALIZE": normalize}
            splitter = OracleTextSplitter(conn=connection, params=splitter_params)
            #""" load the docs """
            docs = loader.load()
            st.write(f"Number of docs loaded: {len(docs)}")
            st.write(f"Document-0: {docs[0].page_content}") # content
            
            doc_origin = Document
            max_lengh_oracle_allow=9000
            counter = 0  
            document_num = 0
            chunks_with_mdata = []
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
                
                # splitter part for each doc  
                # chunk the doc
                chunks = splitter.split_text(doc_origin.page_content)
                st.write(f"Doc {id}: chunks# {len(chunks)}")
                
                #For each chunk create chunk_metadata with 
                #this is going to be used in the embedding 
                for ic, chunk in enumerate(chunks, start=1):
                    counter += 1  
                    chunk_metadata = doc.metadata.copy()  
                    chunk_metadata['id'] = str(counter)  
                    chunk_metadata['document_id'] = str(document_num)
                    chunk_metadata['document_summary'] = str(summ[0])
                    chunks_with_mdata.append(Document(page_content=str(chunk), metadata=chunk_metadata))
                    st.write(f"Doc {id}: metadata: {doc.metadata}")
                    for info in chunks_with_mdata:
                        #st.write("Page content:", doc.page_content)
                        st.write("Metadata:", info.metadata)
                        #st.write("Summary into Metadata:", info.metadata['document_summary'])
                                    
                #===count number of documents
                unique_files = set()
                for chunk in chunks_with_mdata:
                    file_name = chunk.metadata['_file']
                    unique_files.add(file_name)

                #Create and load Oracle Table 
                st.write("Total number of documents:", len(unique_files))
                set_state(3)
with tab2:
    #Trasformation parameters
    st.markdown("You can load your documents via this page")
    if st.button("Create Summary of Your Document(s)","Summary"):
        if st.session_state.stage < 2:
            st.warning("Please Select Embedding Model and Distance Metric Values!!!")
        else:
            distance_strategy=""
            match selected_distance_method:
                case "COSINE":
                    distance_strategy=DistanceStrategy.COSINE
                case "DOT_PRODUCT":
                    distance_strategy=DistanceStrategy.DOT_PRODUCT
                case "EUCLIDEAN_DISTANCE":
                    distance_strategy=DistanceStrategy.EUCLIDEAN_DISTANCE
                case "JACCARD":
                    distance_strategy=DistanceStrategy.JACCARD
                case "MAX_INNER_PRODUCT":
                    distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT
                case _:
                    set_state(0)

            if selected_embedding_model=="":
                set_state(0)

            table_name = st.session_state.table_name+'_'+distance_strategy
            print("table Name :",table_name)
            
            localdir=st.session_state.directory
            loader_params = {}        
            # different loaders file, dir, db
            selected_loader_type = st.radio(
                "Select Your Loader Preference",
                ["File", "Directory", "Database"],
                captions=[
                    "Load a single file",
                    "Load all files from a directory",
                    "Load docs from Oracle Database Table",
                ],horizontal=True
            )
            
            if selected_loader_type == "File":
                #selected_file = st.file_uploader("Select your files to Create Vector Embeddings:", accept_multiple_files=True)
                #st.write(f"- {file.name}")
                #loader_params['file'] = file.name
                loader_params['file'] = "Data/cv_simplified_en.pdf"
            elif selected_loader_type == "Directory":
                loader_params['dir'] = localdir
            elif selected_loader_type == "Directory":
                loader_params = {
                    "owner": "<owner>",
                    "tablename": "demo_tab",
                    "colname": "data",
                }
            else:
                st.write("You didn't select any Loader Type.")
            

                        
            # Some examples of splitter
            # split by chars, max 500 chars
            #splitter_params = {"split": "chars", "max": 500, "normalize": "all"}
            # split by words, max 100 words
            #splitter_params = {"split": "words", "max": 100, "normalize": "all"}
            # split by sentence, max 20 sentences
            #splitter_params = {"split": "sentence", "max": 20, "normalize": "all"}
            splitter_params = {"BY" :"words", "MAX": 100, "OVERLAP": 10, "SPLIT": "BY NEWLINE", "LANGUAGE": "american", "NORMALIZE": "all"}
            
            embedder_params = {"provider": "database", "model": selected_embedding_model}
            summary_params  = {"provider": "database", "model": selected_embedding_model} 
            
            proxy=""

            #==== Oracle Langchain lib
            # instantiate loader, splitter and embedder
            loader = OracleDocLoader(conn=connection, params=loader_params)
            splitter = OracleTextSplitter(conn=connection, params=splitter_params)
            embedder = OracleEmbeddings(conn=connection, params=embedder_params, proxy=proxy)
            summary = OracleSummary(conn=connection, params=summary_params, proxy=proxy)

            #""" load the docs """
            docs = loader.load()
            st.write(f"Number of docs loaded: {len(docs)}")
            st.write(f"Document-0: {docs[0].page_content}") # content

            
            doc_origin = Document
            max_lengh_oracle_allow=9000
            counter = 0  
            document_num = 0
            chunks_with_mdata = []
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
                
                # splitter part for each doc  
                # chunk the doc
                chunks = splitter.split_text(doc_origin.page_content)
                st.write(f"Doc {id}: chunks# {len(chunks)}")
                
                #For each chunk create chunk_metadata with 
                #this is going to be used in the embedding 
                for ic, chunk in enumerate(chunks, start=1):
                    counter += 1  
                    chunk_metadata = doc.metadata.copy()  
                    chunk_metadata['id'] = str(counter)  
                    chunk_metadata['document_id'] = str(document_num)
                    chunk_metadata['document_summary'] = str(summ[0])
                    chunks_with_mdata.append(Document(page_content=str(chunk), metadata=chunk_metadata))
                    st.write(f"Doc {id}: metadata: {doc.metadata}")
                    for info in chunks_with_mdata:
                        #st.write("Page content:", doc.page_content)
                        st.write("Metadata:", info.metadata)
                        #st.write("Summary into Metadata:", info.metadata['document_summary'])
                          
            #===count number of documents
            unique_files = set()
            for chunk in chunks_with_mdata:
                file_name = chunk.metadata['_file']
                unique_files.add(file_name)

            #Create and load Oracle Table 
            st.write("Total number of documents:", len(unique_files))
            set_state(3)
with tab3:
    if st.button("Create Vector Embeddings and Store in Oracle DB","Embedding"):
        if st.session_state.stage < 3:
            st.warning("Please Complete the Previous Steps !!!")
        else:
            vector_store = OracleVS.from_documents(documents=chunks_with_mdata, embedding=embedder, client=connection, table_name=table_name, distance_strategy=distance_strategy)
            if vector_store is not None:
                st.write("\n Documents loading, chunking and generating embeddings and summary are complete.\n")
                st.write(f"Total chunks sent to Oracle Vector Store: {len(chunks_with_mdata)}\n")
                set_state(4)
            else:
                print("\nFailed to get the VectorStore populated.\n")
                sys.exit(1)

with tab4:
    selected_index_type = st.selectbox(
    "Select one of the Index Type ",
    ("IVF","HNSW","HYBRID"),
    index=None,
    placeholder="Select vector index type...",
    )
        
    if st.button("Create Vector Embeddings and Store in Oracle DB","Indexing"):
        if st.session_state.stage < 4:
            st.warning("Please Complete the Previous Steps!!!")
        elif selected_index_type=="IVF":
            oraclevs.create_index(client=connection,vector_store=vector_store, params={
                    "idx_name": "hnsw"+table_name, "idx_type": "IVF"
                })
        elif selected_index_type=="HNSW":
            oraclevs.create_index(client=connection,vector_store=vector_store, params={
                    "idx_name": "hnsw"+table_name, "idx_type": "HNSW"
                })
        elif selected_index_type=="HNSW":
            oraclevs.create_index(client=connection,vector_store=vector_store, params={
                    "idx_name": "hnsw"+table_name, "idx_type": "HNSW"
                })
        else:
            st.warning("Please Select an Index Type")
