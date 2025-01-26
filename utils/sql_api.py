import streamlit as st
import utils.db_connection as db

def load_embedding_model(onnx_dir, onnx_file, db_model_name):
    try:
        conn=db.get_demo_user_connection()
        cursor=conn.cursor()
        sql1 = "EXECUTE DBMS_VECTOR.LOAD_ONNX_MODEL(:dump_dir, :file_name, :model_name);"
        cursor.execute(sql1, dump_dir=onnx_dir, file_name=onnx_file, model_name=db_model_name)
    except Exception as e:
        st.warning(f"Model Couldn't Loaded via SQL API: {e}")
        st.stop()
        