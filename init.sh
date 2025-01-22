#!/bin/bash -e
# 
# Author: firuz.cetinkaya@oracle.com
# Description: Build script for Oracle Converged Database  
# including Vector Search for Demo & Test Purposes
#
# 

CR="container-registry.oracle.com"
DB_HOST_NAME="VECTOR_DB"
DB_PORT=1521
ORACLE_PASSWD="Oracle123"
DB_EXPOSE_PORT=1525

echo "Checking Docker installation"
if command -v docker &> /dev/null; then
    echo "Docker installation found."
else
    echo "Docker installation not found. Please install Docker first."
    exit 1
fi


echo "Please login to "${CR}" with your Oracle SSO Credentials before proceeding"
docker login "${CR}"

echo "Pulling Oracle 23ai Image from Oracle Container Registry"
if [ "$(docker images -q container-registry.oracle.com/database/free:latest 2> /dev/null)" ]; then
    echo "container-registry.oracle.com/database/free:latest already exists..."
else
    docker pull container-registry.oracle.com/database/free:latest
fi

echo "Running Oracle 23ai Free Docker Image with configured parameters"

if [ "$(docker ps -a -q -f name=${DB_HOST_NAME})" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=${DB_HOST_NAME})" ]; then
        # cleanup
        docker start ${DB_HOST_NAME}
    fi
    echo "Docker Image ${DB_HOST_NAME} ia already up and running!"
else
    # run your container
    docker run -td --name ${DB_HOST_NAME} --hostname ${DB_HOST_NAME}  -p ${DB_EXPOSE_PORT}:${DB_PORT} -e ORACLE_PWD=${ORACLE_PASSWD} container-registry.oracle.com/database/free:latest
    until [ $(docker logs ${DB_HOST_NAME}|grep "DATABASE IS READY TO USE"|wc -l) -gt 0 ]; do
      sleep 1
    done
    echo "DATABASE IS READY TO USE!"
fi


# get ollama and run, this is for Macos, please modify according to your OS 
mkdir -p models
wget https://ollama.com/download/Ollama-darwin.zip -O ./models/Ollama-darwin.zip
unzip Ollama-darwin.zip
mv  Ollama.app /Applications/Ollama.app
ollama serve &

# get llama3.2 and run
ollama run llama3.2 &


# Assuming oracle23ai is up and running on Docker with the name vector_db
# Load onnx 

# https://blogs.oracle.com/machinelearning/post/oml4py-leveraging-onnx-and-hugging-face-for-advanced-ai-vector-search

# get embedding model
wget https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 -O ./models/all-MiniLM-L6-v2.onnx


docker exec -i ${DB_HOST_NAME} sqlplus sys/${ORACLE_PASSWD} as sysdba@FREEPDB1 << EOF
    Alter session set container=FREEPDB1;
    Create bigfile tablespace TBS_VECTOR datafile '/opt/oracle/oradata/FREE/FREEPDB1/data_vector01.dbf' size 256M autoextend on maxsize 2G;
    Create user vector_user identified by ${ORACLE_PASSWD} default tablespace TBS_VECTOR temporary tablespace TEMP quota unlimited on TBS_VECTOR;
    GRANT create mining model TO vector_user;
    GRANT DB_DEVELOPER_ROLE to vector_user;
    CREATE DIRECTORY ONNX_IMPORT AS '/tmp/models';
    GRANT READ, WRITE ON DIRECTORY ONNX_IMPORT to VECTOR_USER;
    GRANT CREATE MINING MODEL TO VECTOR_USER;
    exit;
EOF

docker exec -i vector-db sqlplus VECTOR_USER/${ORACLE_PASSWD}@FREEPDB1 << EOF
    BEGIN
    DBMS_VECTOR.LOAD_ONNX_MODEL(
        directory => 'ONNX_IMPORT',
        file_name => 'all-MiniLM-L6.onnx',
        model_name => 'DOC_MODEL3');
    END;
    /
    SELECT MODEL_NAME, ALGORITHM, MINING_FUNCTION
    FROM USER_MINING_MODELS 
    WHERE MODEL_NAME='DOC_MODEL';
    exit;
EOF


# python requirements
conda create -n vector_demo python=3.12
conda activate vector_demo
pip install -r requirements.txt
pip install --upgrade oracledb
#the following omlclient is only required to use in the export any model as onnx part
pip install client/oml-2.0-cp312-cp312-linux_x86_64.whl
mkdir Data
# run the app
# Before running the app please place some pdf files according to your use-case
python oracle23aiVS.py
streamlit run fc_rag_test.py --server.port=8502 --server.address=0.0.0.0
