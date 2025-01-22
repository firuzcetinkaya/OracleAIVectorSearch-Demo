import streamlit as st

st.markdown(
            """
            This application is for demonstration and testing purposes only. Please reach out if you have any questions or issues.
            ##### Resources:
            - Check out User Guide (https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/)
            - Langchain Oracle (https://python.langchain.com/docs/integrations/vectorstores/oracle/)
            - Llamaindex (https://docs.llamaindex.ai/en/stable/examples/vector_stores/orallamavs/)
            
            ##### Features:
           
            - Load an external embedding model in ONNX format to Oracle Database.
            - Create vector embeddings from local documents using a document loader, splitter, and embedder.
            - Generate a summary of a document.
            - Perform a similarity search on Oracle Database for previously loaded documents.
            - Run a chatbot that can use your own local documents from the Oracle Vector DB through Retrieval-Augmented Generation (RAG).
                        
        """
        )