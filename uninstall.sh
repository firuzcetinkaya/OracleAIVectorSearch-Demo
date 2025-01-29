#!/bin/bash -e
# 
# Author: firuz.cetinkaya@oracle.com
# Description: Uninstall script for Oracle AI Vector Search Demo   
# 

#to exit the script immediately when any command in the flow fails.
set -euo pipefail

DB_IMAGE="container-registry.oracle.com/database/free:23.6.0.0"
DEMO_IMAGE="ghcr.io/firuzcetinkaya/oracle-ai-vector-search-demo:latest"
DB_CONTAINER_NAME="vector-db"
DEMO_CONTAINER_NAME="OracleAI-VS-Demo"

echo "Removing Containers"
if docker ps -aq --filter "name=${DB_CONTAINER_NAME}" | grep -q .; then 
    docker stop ${DB_CONTAINER_NAME} && docker rm -fv ${DB_CONTAINER_NAME}; f
if docker ps -aq --filter "name=${DEMO_CONTAINER_NAME}" | grep -q .; then 
    docker stop ${DEMO_CONTAINER_NAME} && docker rm -fv ${DEMO_CONTAINER_NAME}; f

echo "Removing Container Images"
    docker rmi ${DB_IMAGE}
    docker rmi ${DEMO_IMAGE}

echo "Stopping Ollama"
if pgrep -x "ollama" > /dev/null; then
    kill (ps aux | grep ollama | grep -v "grep" | awk '{print $2}')

echo "Demo Environment uninstalled"
