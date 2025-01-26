import streamlit as st
import os
import utils.common_db_operations as db_ops
from load_model.load_embedding_model import ModelLoader

# List previously loaded embedding models
@st.fragment
def top_fragment():
    with st.expander("Existing Embeding Models in DB",expanded=False):
        db_ops.get_embedding_models_table()

st.write("##### Load Embedding Model to Oracle DB")
# try to update only this fragment after model upload to reflect loaded model file
top_fragment()

# in case to implement different API's, particularly SQL API of Oracle 
#api=st.radio(
#            " ",
#            ["Langchain", "SQL","LlamaIndex"],
#            captions=["Langchain API","SQL API","LlamaIndex API"],
#            horizontal=True,
#            index=0
#            )
api="Langchain"
modelLoader = ModelLoader()
# first we upload onnx file to app server, embedding_models directory
emb_model_file=st.file_uploader("Choose ONNX file",accept_multiple_files=False)
if emb_model_file:
    path = os.path.join("./Data/onnx_files", emb_model_file.name)
    with open(path, "wb") as f:
        f.write(emb_model_file.getvalue())
    if modelLoader.ask_for_model_name():
        if st.button("Upload Model","OnnxUpLoad"):    
            with st.spinner('Uploading Model...'):
                # we copy onnx file from app server/container to db server/container
                if modelLoader.copy_onnx_to_db_host(emb_model_file.name):
                    match api:
                        case "Langchain":
                            modelLoader.load_with_langchain(emb_model_file.name) 
                        case "SQL":
                            modelLoader.load_with_sql(emb_model_file.name)
                        case "LlamaIndex":
                            modelLoader.load_with_llamaindex(emb_model_file.name) 
                        case _:
                            None 
            st.success("Done!")