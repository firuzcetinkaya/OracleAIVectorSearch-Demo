# we may use entrypoint.sh file or directly write entrypoint in the Dockerfile, which is preferred now
exec streamlit run /app/app.py --server.port=8501 --server.address=0.0.0.0