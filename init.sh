#!/bin/bash -e
# 
# Author: firuz.cetinkaya@oracle.com
# Description: Build script for Oracle AI Vector Search Demo   
# including Vector Search for Demo & Test Purposes
#
# 

#to exit the script immediately when any command in the flow fails.
set -euo pipefail

CR="container-registry.oracle.com"
DB_IMAGE="container-registry.oracle.com/database/free:23.6.0.0"
DEMO_IMAGE="ghcr.io/firuzcetinkaya/oracle-ai-vector-search-demo:latest"
DB_HOST_NAME="vector-db"
DB_PORT=1521
DB_EXPOSE_PORT=1529
ORACLE_PASSWD="Oracle123"
DB_CONTAINER_NAME="vector-db"
DEMO_CONTAINER_NAME="OracleAI-VS-Demo"
DOCKER_VOLUME_NAME="ora_volume"
DOCKER_VOLUME_PATH="/tmp/oracle_volume"
LLM="llama3.2"

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
if [ "$(docker images -q ${DB_IMAGE} 2> /dev/null)" ]; then
    echo "${DB_IMAGE} already exists..."
else
    docker pull ${DB_IMAGE}
fi


echo "Creating Docker Volume ""${DOCKER_VOLUME_NAME}"""
if [ $(docker volume ls|grep ${DOCKER_VOLUME_NAME}|wc -l) -gt 0 ]; then
    docker volume ls|grep ${DOCKER_VOLUME_NAME}
    echo "${DOCKER_VOLUME_NAME} already exists..."
elif [ $(docker network ls|grep ${DOCKER_VOLUME_NAME}|wc -l) -eq 0 ]; then
    docker volume create  ${DOCKER_VOLUME_NAME}
else
    echo "Docker volume "${DOCKER_VOLUME_NAME}" couldn't created. Please tyr again."
    exit 1
fi


echo "Running Oracle 23ai Image"
if [ "$(docker ps -q -a -f name=${DB_CONTAINER_NAME})" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=${DB_CONTAINER_NAME})" ]; then
        docker start ${DB_CONTAINER_NAME}
    fi
    echo "Docker Image ${DB_CONTAINER_NAME} is already running!"
else
    # run your container
    docker run -td --name ${DB_CONTAINER_NAME} --hostname ${DB_HOST_NAME} -v ${DOCKER_VOLUME_NAME}:${DOCKER_VOLUME_PATH} -p ${DB_EXPOSE_PORT}:${DB_PORT} -e ORACLE_PWD=${ORACLE_PASSWD} ${DB_IMAGE}
    until [ $(docker logs ${DB_CONTAINER_NAME}|grep "DATABASE IS READY TO USE"|wc -l) -gt 0 ]; do
      sleep 1
    done
    docker exec -u 0:0 ${DB_CONTAINER_NAME} chown -R oracle:oinstall /tmp/oracle_volume
    echo "DATABASE IS READY TO USE!"
fi


echo "Pulling Oracle AI VS Demo Image from GHCR"
if [ "$(docker images -q ${DEMO_IMAGE} 2> /dev/null)" ]; then
    echo "${DEMO_IMAGE} already exists..."
else
    docker pull ${DEMO_IMAGE}
fi


echo "Running Oracle AI VS Demo Image"
if [ "$(docker ps -a -q -f name=${DEMO_CONTAINER_NAME})" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=${DEMO_CONTAINER_NAME})" ]; then
        # cleanup
        docker start ${DEMO_CONTAINER_NAME}
    fi
    echo "Docker Image ${DEMO_CONTAINER_NAME} is already running!"
else
    # run your container
    docker run -td --name ${DEMO_CONTAINER_NAME} -v ${DOCKER_VOLUME_NAME}:${DOCKER_VOLUME_PATH} --add-host=host.docker.internal:host-gateway -p 8501:8501 ${DEMO_IMAGE}
    #no need this here, works as root
    #docker exec -u 0:0 ${DEMO_CONTAINER_NAME} chown -R oracle:oinstall /tmp/oracle_volume
    echo "DATABASE IS READY TO USE!"
fi


echo "Checking Ollama installation"
if command -v ollama &> /dev/null; then
    echo "Ollama installation found."
else
    echo "Ollama installation not found. Installing Ollama first."
    if [[ $OSTYPE == 'darwin'* ]]; then
        echo 'Running on macOS'
        # get ollama and run, this is for Macos, please modify according to your OS
        mkdir -p models
        wget https://ollama.com/download/Ollama-darwin.zip -O ./models/Ollama-darwin.zip
        unzip ./models/Ollama-darwin.zip
        mv  ./models/Ollama.app /Applications/Ollama.app
    else
        curl -fsSL https://ollama.com/install.sh | sh
    fi
fi


if pgrep -x "ollama" > /dev/null; then
    echo "Ollama is already running"
else
    # Run Ollama
    ollama serve &
    # Get LLaMA3.2 and run
    ollama run ${LLM} &
fi

echo "Demo Environment is ready, open your web browser, copy and paste the link http://localhost:8501"
