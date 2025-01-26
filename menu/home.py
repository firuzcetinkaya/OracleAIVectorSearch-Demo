import streamlit as st
import utils.db_connection as db
import utils.env_file as env

st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.subheader("",divider="red")
st.title("Oracle AI Vector Search")
st.subheader("",divider="red")

def main():
    env.read_env_file()
    if (st.session_state.is_docker == "True"):
        st.session_state['host'] = "host.docker.internal"
        env.write_env_file()
    else:
        st.session_state['host'] = "localhost"
        env.write_env_file()
    env.read_env_file()
    db.init_db_connections()

try:
    main()
except Exception as e:
    st.warning(f"An error occurred: {e}")
    st.write("Please check App Settings for more details...")
