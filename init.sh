#!/bin/bash -e
# 
# Author: firuz.cetinkaya@oracle.com
# Description: Build script for Oracle AI Vector Search Demo   
# including Vector Search for Demo & Test Purposes
#
# 

CR="container-registry.oracle.com"
DOCKER_VOLUME_NAME="ora_volume"
DOCKER_VOLUME_PATH="/tmp/oracle_volume"
DOCKER_NETWORK_NAME="ora_net"
NETWORK_SUBNET="172.11.0.0/24"
NETWORK_IP_RANGE="172.11.0.0/24"
NETWORK_GATEWAY="172.11.0.1"
DB_HOST_NAME="vector-db"
DB_IP="172.11.0.2"
DB_PORT=1521
ORACLE_PASSWD="Oracle123"
DB_EXPOSE_PORT=1529
DEMO_CONTAINER_NAME="oracle-ai-vector-search-demo"
DEMO_IP="172.11.0.3"

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
if [ "$(docker images -q container-registry.oracle.com/database/free:23.6.0.0 2> /dev/null)" ]; then
    echo "container-registry.oracle.com/database/free:23.6.0.0 already exists..."
else
    docker pull container-registry.oracle.com/database/free:23.6.0.0
fi

echo "Creating Docker Network ""${DOCKER_NETWORK_NAME}"""
if [ $(docker network ls|grep ${DOCKER_NETWORK_NAME}|wc -l) -gt 0 ]; then
    docker network ls|grep ${DOCKER_NETWORK_NAME}
    echo "${DOCKER_NETWORK_NAME} already exists..."
elif [ $(docker network ls|grep ${DOCKER_NETWORK_NAME}|wc -l) -eq 0 ]; then
    docker network create --driver=bridge --subnet=${NETWORK_SUBNET} --ip-range=${NETWORK_IP_RANGE} --gateway=${NETWORK_GATEWAY} ${DOCKER_NETWORK_NAME}
else
    echo "Docker network "${DOCKER_NETWORK_NAME}" couldn't created. Please tyr again."
    exit 1
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

echo "Running Oracle 23ai Free Docker Image with configured parameters"

if [ "$(docker ps -a -q -f name=${DB_HOST_NAME})" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=${DB_HOST_NAME})" ]; then
        # cleanup
        docker start ${DB_HOST_NAME}
    fi
    echo "Docker Image ${DB_HOST_NAME} ia already up and running!"
else
    # run your container
    docker run -td --name ${DB_HOST_NAME} --hostname ${DB_HOST_NAME} --network ${DOCKER_NETWORK_NAME} --ip ${DB_IP} -v ${DOCKER_VOLUME_NAME}:${DOCKER_VOLUME_PATH} -p ${DB_EXPOSE_PORT}:${DB_PORT} -e ORACLE_PWD=${ORACLE_PASSWD} container-registry.oracle.com/database/free:23.6.0.0
    until [ $(docker logs ${DB_HOST_NAME}|grep "DATABASE IS READY TO USE"|wc -l) -gt 0 ]; do
      sleep 1
    done
    docker exec -u 0:0 vector-db chown -R oracle:oinstall /tmp/oracle_volume
    echo "DATABASE IS READY TO USE!"
fi

# Assuming oracle23ai is up and running on Docker with the name vector-db

echo "Pulling oracle-ai-vector-search-demo Image from GHCR Registry"
if [ "$(docker images -q ghcr.io/firuzcetinkaya/oracle-ai-vector-search-demo:latest 2> /dev/null)" ]; then
    echo "ghcr.io/firuzcetinkaya/oracle-ai-vector-search-demo:latest already exists..."
else
    docker pull ghcr.io/firuzcetinkaya/oracle-ai-vector-search-demo:latest
fi

echo "Running oracle-ai-vector-search-demo Image"
if [ "$(docker ps -a -q -f name=${DEMO_CONTAINER_NAME})" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=${DEMO_CONTAINER_NAME})" ]; then
        # cleanup
        docker start ${DEMO_CONTAINER_NAME}
    fi
    echo "Docker Image ${DEMO_CONTAINER_NAME} ia already up and running!"
else
    # run your container
    docker run -td --name ${DEMO_CONTAINER_NAME} --network ${DOCKER_NETWORK_NAME} --ip ${DEMO_IP} -v ${DOCKER_VOLUME_NAME}:${DOCKER_VOLUME_PATH} -p 8501:8501 ghcr.io/firuzcetinkaya/oracle-ai-vector-search-demo:latest
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

if pgrep -x "ollama" > /dev/null
then
    echo "Ollama is Running"
else
    ollama serve &
    # get llama3.2 and run
    ollama run llama3.2 &
fi



echo "Everything is ready, open your web browser, copy and paste the link http://localhost:8501"