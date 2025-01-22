import streamlit as st
import oracledb
from utils.env_file import read_env_file


def get_sys_connection():
    if 'conn_sys' not in st.session_state:
        try:
            #Connection will be as SYSDBA to make configuration
            connection_sys = oracledb.connect(user="SYS", password=st.session_state.oracle_passwd, dsn=st.session_state.dsn,mode=oracledb.SYSDBA)
            connection_sys.is_healthy()
            print("\nSYS Connection successful!\n")
            if 'conn_sys' not in st.session_state:
                st.session_state['conn_sys'] = connection_sys
            return connection_sys            
        except Exception as e:
            st.warning(f"SYS Connection failed with error: {e}")
            st.stop()
    elif st.session_state.conn_sys.is_healthy():
         connection_sys = st.session_state.conn_sys    
         return connection_sys 
    else:
        st.warning("Please Check Oracle Database 23ai Container!!!")
        st.stop()
        return None

def check_vector_user_in_db():
    #query to find whether the  vector_user is in db or not
    sql1 = "SELECT username FROM dba_users WHERE username = upper(:uname)"
    with st.session_state.conn_sys.cursor() as cursor:
        cursor.execute(sql1,uname="VECTOR_USER")
        cursor.fetchall()
        rcount=cursor.rowcount
    if rcount>0:
        return True
    else:
        return False
            
def get_vector_user_connection():
    if 'conn_vector_user' not in st.session_state:
        # check if vector_user exists, if this is first run vector_user may not exist, then skip until DB configuration
        if (check_vector_user_in_db()==False):
            print("Vector_User has not been created yet!")
            st.warning("Vector User does not exists, Configure it on Configuration Page")
        else:
            try:
                # Connection will be as VECTOR USER 
                connection_vector_user = oracledb.connect(user=st.session_state.username, password=st.session_state.password, dsn=st.session_state.dsn)
                print("\nVector_User Connection successful!\n")
                if 'conn_vector_user' not in st.session_state:
                    st.session_state['conn_vector_user'] = connection_vector_user
                return connection_vector_user 
            except Exception as e:
                st.warning(f"Vector User Connection failed with error: {e}")
    elif st.session_state.conn_vector_user.is_healthy():
        connection_vector_user = st.session_state.conn_vector_user
        return connection_vector_user  
    else:
        st.warning("Please Check Oracle Database 23ai Container!!!")
        st.stop()
        return None


def init_db_connections():
    read_env_file()
    get_sys_connection()
    get_vector_user_connection()
