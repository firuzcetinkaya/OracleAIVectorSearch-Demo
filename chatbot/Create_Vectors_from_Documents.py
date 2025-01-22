import streamlit as st
import main
import os
from langchain_core.documents import Document
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_community.vectorstores import oraclevs
from langchain_community.vectorstores import OracleVS
from langchain_community.utilities.oracleai import OracleSummary
from langchain_community.embeddings.oracleai import OracleEmbeddings
from langchain_community.document_loaders.oracleai import OracleTextSplitter 
from langchain_community.document_loaders.oracleai import OracleDocLoader 

#langusages from Oracle DB Supported Langs, refine the language list as desired
#all_supported_languages=["ALBANIAN","AMERICAN","AMHARIC","ARABIC","ARMENIAN","ASSAMESE","AZERBAIJANI","BANGLA","BASQUE","BELARUSIAN","BRAZILIAN PORTUGUESE","BULGARIAN","BURMESE","CANADIAN FRENCH","CATALAN","CROATIAN","CYRILLIC KAZAKH","CYRILLIC SERBIAN","CYRILLIC UZBEK","CZECH","DANISH","DARI","DIVEHI","DUTCH","EGYPTIAN","ENGLISH","ESTONIAN","FINNISH","FRENCH","GEORGIAN","GERMAN DIN","GERMAN","GREEK","GUJARATI","HEBREW","HINDI","HUNGARIAN","ICELANDIC","INDONESIAN","IRISH","ITALIAN","JAPANESE","KANNADA","KHMER","KOREAN","KYRGYZ","LAO","LATIN AMERICAN SPANISH","LATIN BOSNIAN","LATIN SERBIAN","LATIN UZBEK","LATVIAN","LITHUANIAN","MACEDONIAN","MALAY","MALAYALAM","MALTESE","MARATHI","MEXICAN SPANISH","NEPALI","NORWEGIAN","ORIYA","PERSIAN","POLISH","PORTUGUESE","PUNJABI","ROMANIAN","RUSSIAN","SIMPLIFIED CHINESE","SINHALA","SLOVAK","SLOVENIAN","SPANISH","SWAHILI","SWEDISH","TAMIL","TELUGU","THAI","TRADITIONAL CHINESE","TURKISH","TURKMEN","UKRAINIAN","URDU","VIETNAMESE"]
#selected some 
supported_languages=["ALBANIAN","AMERICAN","ARABIC","ARMENIAN","AZERBAIJANI","BULGARIAN","CROATIAN","CZECH","DANISH","DUTCH","EGYPTIAN","ENGLISH","ESTONIAN","FINNISH","FRENCH","GEORGIAN","GERMAN","GREEK","HEBREW","HINDI","HUNGARIAN","ICELANDIC","INDONESIAN","IRISH","ITALIAN","JAPANESE","KOREAN","KYRGYZ","LATVIAN","LITHUANIAN","MACEDONIAN","MALAY","NORWEGIAN","PERSIAN","POLISH","PORTUGUESE","PUNJABI","ROMANIAN","RUSSIAN","SIMPLIFIED CHINESE","SLOVAK","SLOVENIAN","SPANISH","SWAHILI","SWEDISH","TAMIL","THAI","TRADITIONAL CHINESE","TURKISH","TURKMEN","UKRAINIAN","URDU","VIETNAMESE"]

def list_existing_embedding_models():
    if 'conn_vector_user' not in st.session_state:
        main.getVectorUserConnection() 
        connection=st.session_state.conn_vector_user
    elif st.session_state.conn_vector_user.is_healthy():
        connection=st.session_state.conn_vector_user
        print("Vector User Connection is ok ")
    else:
        st.warning("Please Check Oracle Database 23ai Container!!!")
        st.stop()
    #query to find the vector embedding models that currently exists in DB
    sql1 = """SELECT model_name, vector_info
    FROM user_mining_model_attributes
    WHERE attribute_type = :atype
    ORDER BY model_name
    """
    r_count=0
    cursor = connection.cursor()
    try:
        cursor.execute(sql1,atype="VECTOR")
        rows = cursor.fetchall()
        r_count=cursor.rowcount;
    except Exception as e:
        st.warning(f"Loaded Models Couldn't be retrieved from DB: {e}")
    finally:
        cursor.close()
    if (r_count>0):        
        embedding_models_list=[row[0] for row in rows]
    else:
        st.write("There are no embedding models exist in database")
        embedding_models_list=[]
    return embedding_models_list

def list_existing_vector_stores():
    if 'conn_vector_user' not in st.session_state:
        main.getVectorUserConnection() 
        connection=st.session_state.conn_vector_user
    elif st.session_state.conn_vector_user.is_healthy():
        connection=st.session_state.conn_vector_user
        print("Vector User Connection is ok ")
    else:
        st.warning("Please Check Oracle Database 23ai Container!!!")
        st.stop()
    #query to find the vector embedding models that currently exists in DB
    sql1 = """SELECT distinct table_name
    FROM user_tab_columns
    WHERE data_type = :atype
    ORDER BY table_name
    """
    r_count=0
    cursor = connection.cursor()
    try:
        cursor.execute(sql1,atype="VECTOR")
        rows = cursor.fetchall()
        r_count=cursor.rowcount;        
    except Exception as e:
        st.warning(f"Loaded Models Couldn't be retrieved from DB: {e}")
    finally:
        cursor.close()
    if (r_count>0):
        table_list=[row[0] for row in rows]
    else:
        st.write("There are no Vector Store in Database")
        table_list=[]
    return table_list

def list_existing_tables():
    if 'conn_vector_user' not in st.session_state:
        main.getVectorUserConnection() 
        connection=st.session_state.conn_vector_user
    elif st.session_state.conn_vector_user.is_healthy():
        connection=st.session_state.conn_vector_user
        print("Vector User Connection is ok ")
    else:
        st.warning("Please Check Oracle Database 23ai Container!!!")
        st.stop()
    #query to find the vector embedding models that currently exists in DB
    sql1 = """SELECT distinct table_name
    FROM user_tables where table_name not like '%$%'
    ORDER BY table_name
    """
    r_count=0
    cursor = connection.cursor()
    try:
        cursor.execute(sql1)
        rows = cursor.fetchall()
        r_count=cursor.rowcount;        
    except Exception as e:
        st.warning(f"Tables Couldn't be retrieved from DB: {e}")
    finally:
        cursor.close()
    if (r_count>0):
        table_list=[row[0] for row in rows]
    else:
        st.write("There are no tables in Database")
        table_list=[]
    return table_list

def list_columns_of_table(table_name):
    if 'conn_vector_user' not in st.session_state:
        main.getVectorUserConnection() 
        connection=st.session_state.conn_vector_user
    elif st.session_state.conn_vector_user.is_healthy():
        connection=st.session_state.conn_vector_user
        print("Vector User Connection is ok ")
    else:
        st.warning("Please Check Oracle Database 23ai Container!!!")
        st.stop()
    #query to find the vector embedding models that currently exists in DB
    sql1 = """SELECT distinct column_name
    FROM user_tab_columns
    WHERE table_name = :tname
    ORDER BY table_name
    """
    r_count=0
    cursor = connection.cursor()
    try:
        cursor.execute(sql1,tname=table_name)
        rows = cursor.fetchall()
        r_count=cursor.rowcount;        
    except Exception as e:
        st.warning(f"Columns Couldn't be retrieved from DB: {e}")
    finally:
        cursor.close()
    if (r_count>0):
        columns_list=[row[0] for row in rows]
    else:
        st.write("There are no columns in table")
        columns_list=[]
    return columns_list

def get_selected_embedding():
    if (selected_embedding_model):
        return selected_embedding_model  
    else:
        st.warning("Please Select embedding Model or Load a New embedding Model First")
        return ""

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
    
def get_selected_vector_store():
    if (selected_vector_store):
        return selected_vector_store  
    else:
        st.warning("Please Select Vector Store or Create a New Vector Store First")
        return ""
        
def create_loader(loader_params):
    loader = OracleDocLoader(conn=st.session_state.conn_vector_user, params=loader_params)
    return loader

def create_splitter(splitter_params):
    splitter = OracleTextSplitter(conn=st.session_state.conn_vector_user, params=splitter_params)    
    return splitter

def create_summary(summary_params):
    proxy=""
    summary = OracleSummary(conn=st.session_state.conn_vector_user, params=summary_params, proxy=proxy)
    return summary

def create_embedder(embedder_params):
    proxy=""
    embedder = OracleEmbeddings(conn=st.session_state.conn_vector_user, params=embedder_params, proxy=proxy)
    return embedder

def suggestTableName():
    table_name=""
    st.info("It is a good practice to include Distance Method to table name if  vector store environment")
    table_name = st.text_input("Provide a Table Name for Vector Store","TBL_"+get_selected_distance())
    if len(table_name)<1:
        st.warning("Please Provide a Table Name")
        return("")
    else:
        return table_name

def load_split_embed_docs(loader,splitter,summary,embedder):
        #""" load the docs """
        docs = loader.load()
        st.write(f"Number of docs loaded: {len(docs)}")
        # make a list of which files processe and list generated chunks, summaries
        #for id, doc in enumerate(docs, start=1):
            #st.write(doc)
            #st.write(doc.metadata["_file"])
        #st.write(f"Document-0: {docs[0].page_content}") # content
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
            st.write(doc.metadata["_file"])
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
                #st.write("Page content:", doc.page_content)
                st.write("ChunkId:", info.metadata['id'])
                st.write("DocId:",info.metadata['document_id'])
                st.write("Chunk Content:",info.page_content)
                #st.write("Summary into Metadata:", info.metadata['document_summary'])        
                      
        #===count number of documents
        unique_files = set()
        for chunk in chunks_with_mdata:
            file_name = chunk.metadata['_file']
            unique_files.add(file_name)
            
            
        #Create and load Oracle Table 
        st.write("Total number of documents:", len(unique_files))
        #st.stop()
        # Ingest documents into Oracle Vector Store using different distance strategies

        # When using our API calls, start by initializing your vector store with a subset of your documents
        # through from_documents(), then incrementally add more documents using add_texts().
        # This approach prevents system overload and ensures efficient document processing.
        
        #try:
        #    #vs.add_texts(texts, metadata)
        #    print(f"\n\n\nAdd texts complete for vector store {i}\n\n\n")
        #except Exception as ex:
        #    print(f"\n\n\nExpected error on duplicate add for vector store {i}\n\n\n")

        # Deleting texts using the value of 'id'
        #vs.delete([metadata[0]["id"]])
        #print(f"\n\n\nDelete texts complete for vector store {i}\n\n\n")
        
        # create new vector store or add to existing one
        #table_name=suggestTableName()
        table_name="test1"
        distance_strategy=get_selected_distance()
        vector_store = OracleVS.from_documents(documents=chunks_with_mdata, embedding=embedder, client=st.session_state.conn_vector_user, table_name=table_name, distance_strategy=distance_strategy)
        if vector_store is not None:
            st.write("\n Documents loading, chunking and generating embeddings and summary are complete.\n")
            st.write(f"Total chunks sent to Oracle Vector Store: {len(chunks_with_mdata)}\n")
        else:
            print("\nFailed to get the VectorStore populated.\n")

def create_vector_index(table_name,selected_index_type,index_params):
    if selected_index_type=="IVF":
        oraclevs.create_index(client=st.session_state.conn_vector_user,vector_store=vector_store, params={
                "idx_name": "ivf"+table_name, "idx_type": "IVF"
            })
    elif selected_index_type=="HNSW":
        oraclevs.create_index(client=st.session_state.conn_vector_user,vector_store=vector_store, params={
                "idx_name": "hnsw"+table_name, "idx_type": "HNSW"
            })
    else:
        st.warning("Please Select an Index Type")

with st.sidebar:
    st.write("")
    selected_embedding_model = st.selectbox(
        "Embedding Model",
        (list_existing_embedding_models()),
        index=None,
        placeholder="Select embedding model...",
    )
    st.page_link("Load_Embedding_Model.py", label=":gray-background[Load a new Embedding Model]")
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
        "Vector Store",
        (list_existing_vector_stores()),
        index=None,
        placeholder="Select vector store...",
    )

tab1, tab2 = st.tabs(["Document Loader & Splitter (Chunking), Summary, Embedder", "Indexing"])
with tab1:
    #Loader and Splitter
    with st.expander("Splitter Parameters",expanded=False):
        #list_splitter_params()
        by = st.radio(
            "Split Unit",
            ["CHARS", "WORDS", "VOCABULARY"],
            captions=[
                "Load a single file",
                "Load all files from a directory",
                "Load docs from Oracle Database Table",
            ],index=1,horizontal=True,
            help="For the Oracle Split Example visit https://python.langchain.com/v0.2/docs/integrations/document_loaders/oracleai/#split-documents"
        )
        m1,m2 = st.columns(2,gap='medium')
        with m1:
            if by=="CHARS":
                max = st.slider("Max", 50, 4000, 400)
            if by=="WORDS":
                max = st.slider("Max", 10, 1000, 25)
            if by=="VOCABULARY":
                max = st.slider("Max", 10, 1000, 25)  
            split_by = st.selectbox(
            "Split By",
            ("NONE","BY NEWLINE","RECURSIVELY","SENTENCE","CUSTOM (Not Implemented in the Demo)"),
            index=1,
            placeholder="Select split by method...",
            )
            #languages from Oracle DB Supported Langs, refine the language list as desired
            language = st.selectbox(
                "Language ",
                (supported_languages),
                index=11,
                placeholder="Select language...",
            )
        with m2:
            overlap = st.slider("Overlap", 5, 20, 0,help="Valid value: 5% to 20% of MAX, Default value: 0") 
            normalize = st.selectbox(
            "Normalization ",
            ("NONE","ALL"),
            index=1,
            placeholder="Select normalization method...",
            )                        

    
    with st.expander("Summary Parameters",expanded=False):
        #list_summary_params()
        provider = st.radio(
            "Provider",
            ["DATABASE", "EXTERNAL"],
            captions=[
                "Embedding Model from Database",
                "External Embedding Provider",
            ],horizontal=True,index=0,
            help="For the Oracle Split Example visit https://python.langchain.com/v0.2/docs/integrations/document_loaders/oracleai/#split-documents"
        )
        m1,m2 = st.columns(2,gap='medium')
        with m1:
            #glevel, numParagraphs  = st.columns(2, vertical_alignment="top")
            glevel = st.radio(
                "GLevel",
                ["S", "P"],
                captions=[
                    "Sentence",
                    "Paragraph",
                ],horizontal=True,index=0,
                help="For the Oracle Split Example visit https://python.langchain.com/v0.2/docs/integrations/document_loaders/oracleai/#split-documents"
            )
            maxPercent = st.slider("maxPercent", 0, 100, 10,help="Maximum number of document paragraphs (or sentences) selected for the summary, as a percentage of the total paragraphs (or sentences) in the document. The default value is 10.")
            language = st.selectbox(
                "Language",
                (supported_languages),
                index=11,
                placeholder="Select language...",
                )   
        with m2:
            numParagraphs = st.text_input("numParagraphs", 16,help="Maximum number of document paragraphs (or sentences) selected for the summary. The default value is 16.") 
            num_themes = st.slider("num_themes", 0, 50, 50,help="Number of theme summaries to produce. For example, if you specify 10, then this function returns the top 10 theme summaries. If you specify 0 or NULL, then this function returns all themes in a document. The default value is 50. If the document contains more than 50 themes, only the top 50 themes show conceptual hierarchy.")
              
    with st.expander("Loader Parameters",expanded=True):  
        localdir=st.session_state.documents_directory
        loader_params = {}        
        # different loaders file, dir, db
        selected_loader_type = st.radio(
            "Loader Method",
            ["File", "Directory", "Database"],
            captions=[
                "Load a single document",
                "Load all documents in a directory",
                "Load documents from Oracle Table",
            ],horizontal=True, help="For the Oracle Loader Example visit https://python.langchain.com/v0.2/docs/integrations/document_loaders/oracleai/#load-documents"
        )
        if selected_loader_type == "File":
            selected_file = st.file_uploader("Select your file to Create Vector Embeddings:", accept_multiple_files=False)
            if selected_file:
                path = os.path.join("./Data", selected_file.name)
                with open(path, "wb") as f:
                    f.write(selected_file.getvalue())
                #st.write(f"- {file.name}")
                #loader_params['file'] = file.name
                loader_params['file'] = path
        elif selected_loader_type == "Directory":
            selected_files = st.file_uploader("Select your file to Create Vector Embeddings:", accept_multiple_files=True)
            if selected_files:
                for file in selected_files:
                    path = os.path.join("./Data", file.name)
                    with open(path, "wb") as f:
                        f.write(file.getvalue())
            loader_params['dir'] = "./Data"
        elif selected_loader_type == "Database":
            # select a table and column from db containing docs
            selected_table_name = st.selectbox(
                "Existing Tables",
                (list_existing_tables()),
                index=None,
                placeholder="Select table name...",
            )
            if (selected_table_name==""):
                st.write("Select a table first")
            else:
                selected_column_name = st.selectbox(
                    "Existing Columns",
                    (list_columns_of_table(selected_table_name)),
                    index=None,
                    placeholder="Select column name...",
                )
                if (selected_column_name==""):
                    st.write("select a column")
                else:                    
                    loader_params = {
                        "owner": "VECTOR_USER",
                        "tablename": selected_table_name,
                        "colname": selected_column_name,
                    }

        if st.button("Load, Chunk & Embed Your Document(s)","Loader"):
                embedding=get_selected_embedding()
                distance_strategy=get_selected_distance()
                if (embedding=="" or distance_strategy==""):
                    st.stop()
                else:
                    loader=create_loader(loader_params)
                    splitter_params = {"BY" :by, "MAX": max, "OVERLAP": overlap, "SPLIT": split_by, "LANGUAGE": language, "NORMALIZE": normalize}
                    splitter=create_splitter(splitter_params)
                    #you may have external provider for both embedding and summary
                    summary_params  = {"provider": "database", "model": embedding} 
                    summary=create_summary(summary_params)
                    embedder_params = {"provider": "database", "model": embedding}
                    embedder=create_embedder(embedder_params)
                    load_split_embed_docs(loader,splitter,summary,embedder)
with tab2:
    with st.expander("Index Parameters"):  
            embedding=get_selected_embedding()
            distance_strategy = get_selected_distance()
            vector_store = get_selected_vector_store()
            if (embedding=="" or distance_strategy=="" or vector_store==""):
                st.stop()
            selected_index_type = st.radio(
            "Select Your Index Type",
            ["HNSW", "IVF", "Hybrid"],
            captions=[
                "HNSW Index",
                "IVF Index",
                "Hybrid Index",
            ],horizontal=True, index=0,help="For the Oracle Vector Indexing Details visit https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/guidelines-using-vector-indexes.html"
            )   
            if selected_index_type == "HNSW":
                distance = distance_strategy # for hnsw EUCLIDEAN, L2_SQUARED (aka EUCLIDEAN_SQUARED), COSINE, DOT, MANHATTAN, HAMMING
                #if hnsw index
                m1,m2 = st.columns(2,gap='medium')
                with m1:
                    accuracy = st.slider("Accuracy", 0, 100, 90,help="Target accuracy at which the approximate search should be performed when running an approximate search query using vector indexes.")            
                    neighbors=st.slider("neighbors", 0, 2048, 8,help="Neigbors.") #NEIGHBORS and M are equivalent and represent the maximum number of neighbors a vector can have on any layer. The last vertex has one additional flexibility that it can have up to 2M neighbors.  
                with m2:
                    parallel=st.slider("Parallel", 0, 64, 8,help="Parallel Option may bring soe performance gains if your system supports.")   
                    efConstruction=st.slider("efConstruction", 0, 65535, 100,help="efConstruction.")   # only for HNSW, EFCONSTRUCTION represents the maximum number of closest vector candidates considered at each step of the search during insertion.                    
                index_params = ""
                if st.button("Create Vector Index","Indexing"):
                    create_vector_index()
            elif selected_index_type == "IVF":
                #if ivf index
                distance = distance_strategy # for hnsw EUCLIDEAN, L2_SQUARED (aka EUCLIDEAN_SQUARED), COSINE, DOT, MANHATTAN, HAMMING
                m1,m2 = st.columns(2,gap='medium')
                with m1:
                    accuracy = st.slider("Accuracy", 0, 100, 90,help="Target accuracy at which the approximate search should be performed when running an approximate search query using vector indexes.")            
                    neighbor_partitions=st.slider("Parallel", 0, 10000000, 8,help="Neigbors.")   
                    #SAMPLE_PER_PARTITION: from 1 to (num_vectors/neighbor_partitions)
                    #MIN_VECTORS_PER_PARTITION: from 0 (no trimming of centroid partitions) to total number of vectors (would result in 1 centroid partition)    
                with m2:
                    parallel=st.slider("Parallel", 0, 64, 8,help="Parallel Option may bring soe performance gains if your system supports.")   
                    #SAMPLE_PER_PARTITION: from 1 to (num_vectors/neighbor_partitions)
                    #MIN_VECTORS_PER_PARTITION: from 0 (no trimming of centroid partitions) to total number of vectors (would result in 1 centroid partition)    
                index_params = ""
                if st.button("Create Vector Index","Indexing"):
                    create_vector_index()
            elif selected_index_type == "Hybrid":
                index_params_params = {
                    "owner": "VECTOR_USER",
                    "tablename": "demo_tab",
                    "colname": "data",
                }
                st.write("Hybrid Indexes will be implemented.")
            else:
                st.write("You didn't select any Index Type.")
                st.stop()
            
