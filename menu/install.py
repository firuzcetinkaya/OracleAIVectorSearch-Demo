import streamlit as st

st.write("#### Installation")

st.markdown(
            """
           This demo environment comes with predefined parameters and assumes all the following are installed and running properly: 
            
            - Oracle Database 23ai Developer Edition as a Docker container with the container name "vector-db"\n
                
            ###### Docker Setup (if not previously configured)
            1.  Run the following Docker command to start the Oracle Database container named "vector-db": \n
                `docker run -d --name vector-db --hostname vector_db -p 1529:1521 -e ORACLE_PWD=Oracle123 container-registry.oracle.com/database/free:latest`\n
            2.  Verify if the database is ready by running:\n
                `docker logs -f vector-db`
            
            - Ollama with a Large Language Model (LLM)\n
            ###### Installing Ollama
            Download Ollama from: https://ollama.com/download
            ###### Ollama Setup (if not previously configured)
            1.  After downloading Ollama, use the following commands to start the server and run the desired model: \n
                `ollama serve &`\n 
                `ollama run llama2`\n  
            ###### Configuration
            The init.sh file configures most of the environment's requirements. Refer to the following configuration pages to change parameters:

            - Configuration page:
        """    
        )
st.page_link("menu/configure_environment.py", label=":gray-background[Configure Environment]")
st.markdown(
            """
            ###### Important Note: 
            After making any changes to the configuration, remember to restart the environment.
        """
        )
