import streamlit as st
from langchain_community.embeddings.oracleai import OracleEmbeddings
import os
import oracledb
import subprocess

#this part is to export onnx using oml
#from oml.utils import EmbeddingModel, EmbeddingModelConfig

#config = EmbeddingModelConfig.from_template("text",max_seq_length=512,trust_remote_code=True)
#em = EmbeddingModel(model_name="avsolatorio/GIST-Embedding-v0", config=config)
#em.export2file("GIST-Embedding-v0",output_dir="/home/oracle/23_test/onnx/")
#quit()

embedding_model_list=['sentence-transformers/all-mpnet-base-v2',
 'sentence-transformers/all-MiniLM-L6-v2',
 'sentence-transformers/multi-qa-MiniLM-L6-cos-v1',
 'ProsusAI/finbert',
 'medicalai/ClinicalBERT',
 'sentence-transformers/distiluse-base-multilingual-cased-v2',
 'sentence-transformers/all-MiniLM-L12-v2',
 'BAAI/bge-small-en-v1.5',
 'BAAI/bge-base-en-v1.5',
 'taylorAI/bge-micro-v2',
 'intfloat/e5-small-v2',
 'intfloat/e5-base-v2',
 'prajjwal1/bert-tiny',
 'thenlper/gte-base',
 'thenlper/gte-small',
 'TaylorAI/gte-tiny',
 'infgrad/stella-base-en-v2',
 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2',
 'intfloat/multilingual-e5-base',
 'intfloat/multilingual-e5-small',
 'sentence-transformers/stsb-xlm-r-multilingual']


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
    for emb in embedding_models_list:
        st.markdown("- " + emb)


try:
    connection = oracledb.connect(user=st.session_state.username, password=st.session_state.password, dsn=st.session_state.dsn)
    print("\nConnection successful!\n")
except Exception as e:
    print(e)
    print("\nConnection failed!\n")
    st.stop()#
    

st.markdown("Existing Models in Database")
generate_embedding_models_list()

st.write("")
st.write("")

selected_embedding_model = st.selectbox(
        "Select an Embedding Model to Load in Oracle DB.",
        (embedding_model_list),
        index=None,
        placeholder="Select embedding model...",
    )

st.write("")

if st.button("Download Embedding Model","OnnxDownLoad"):   
    command="wget https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    if (process.returncode==0):
        st.write("Model Successfully Downloaded")
    else:
        st.warning("Model Download Failed!!!")


st.write("")

# please update with your related information
# make sure that you have onnx file in the system
onnx_dir = "DEMO_PY_DIR"
onnx_file = "tinybert.onnx"
model_name = "demo_model"


if st.button("Load Your Onnx format model to Oracle Database","OnnxLoader"):
    # since this is assumed to be the docker env. we need to upload the onnx file to docker instance first
    command="docker cp v23.3.zip CONVERGED_DB_FREE:/home/oracle/v23.3.zip"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    if (process.returncode==0):
        st.write("Model Successfully Downloaded")
    else:
        st.warning("Model Download Failed!!!")
    try:
        OracleEmbeddings.load_onnx_model(connection, onnx_dir, onnx_file, model_name)
        print("ONNX model loaded.")
    except Exception as e:
        print("ONNX model loading failed!")
        st.stop()#