# Set up the container with Python 3.11 installed.
FROM python:3.11-slim
SHELL ["/bin/bash", "-c"]
# Copy content to the /app directory in the container.
#COPY . /app
COPY . /app/

# Set the /app directory as the working directory for any RUN, CMD, ENTRYPOINT, or COPY instructions that follow.
WORKDIR /app


RUN pip3 install -r requirements.txt

ENV PATH=“${PATH}:/root/.local/bin”

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "/app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

#access token for ghcr
#username firuzcetinkaya
#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

#docker login --username firuzcetinkaya --password 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 ghcr.io
#docker build . -t ghcr.io/firuzcetinkaya/oracle-ai-vector-search-demo:latest
#docker push ghcr.io/firuzcetinkaya/oracle-ai-vector-search-demo:latest