import streamlit as st
import oracledb
from utils.env_file import read_env_file


def get_sys_connection():
    if 'conn_sys' not in st.session_state:
        try:
            #Connection will be as SYSDBA to make configuration
            connection_sys = oracledb.connect(user=st.session_state.username, password=st.session_state.password, host=st.session_state.host, port=st.session_state.db_expose_port, service_name=st.session_state.service_name, mode=oracledb.SYSDBA)
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


def check_demo_user_in_db():
    #query to find whether the  demo_user is in db or not
    sql1 = "SELECT username FROM dba_users WHERE username = upper(:uname)"
    with st.session_state.conn_sys.cursor() as cursor:
        cursor.execute(sql1,uname=st.session_state.demo_username)
        cursor.fetchall()
        rcount=cursor.rowcount
    if rcount>0:
        return True
    else:
        return False


def create_demo_user():
    try:
        get_sys_connection()
        connection=st.session_state.conn_sys
        cursor = connection.cursor()
        try:       
            sql1=(
                """
                begin
                    -- Drop user
                    begin
                        execute immediate 'drop user {demo_uname} cascade';
                    exception
                        when others then
                            dbms_output.put_line('Error dropping user: ' || SQLERRM);
                    end;
                    
                    -- Create user and grant privileges
                    execute immediate 'create user {demo_uname} identified by {demo_pwd}';
                    execute immediate 'grant connect, unlimited tablespace, create credential, create any table, create procedure, create any index to {demo_uname}';
                    execute immediate 'create or replace directory DEMO_PY_DIR as ''/tmp/oracle_volume''';
                    execute immediate 'grant read, write on directory DEMO_PY_DIR to public';
                    execute immediate 'grant create mining model to {demo_uname}';
                    
                    -- Network access
                    begin
                        DBMS_NETWORK_ACL_ADMIN.APPEND_HOST_ACE(
                            host => '*',
                            ace => xs$ace_type(privilege_list => xs$name_list('connect'),
                                            principal_name => '{demo_uname}',
                                            principal_type => xs_acl.ptype_db)
                        );
                    end;
                end;
                """
            ).format(demo_uname=st.session_state.demo_username,demo_pwd=st.session_state.demo_password)
            cursor.execute(sql1)
        except Exception as e:
            st.warning(f"Demo User setup failed with error: {e}")
        finally:
            cursor.close()
        #st.stop()
    except Exception as e:
        print(f"Connection failed with error: {e}")
        st.stop()
            
            
def get_demo_user_connection():
    if 'conn_demo_user' not in st.session_state:
        # check if demo_user exists
        if (check_demo_user_in_db()==False):
            create_demo_user()
        try:
            # Connection will be as DEMO USER 
            connection_demo_user = oracledb.connect(user=st.session_state.demo_username, password=st.session_state.demo_password, host=st.session_state.host, port=st.session_state.db_expose_port, service_name=st.session_state.service_name)
            print("\nDemo_user Connection successful!\n")
            if 'conn_demo_user' not in st.session_state:
                st.session_state['conn_demo_user'] = connection_demo_user
            return connection_demo_user 
        except Exception as e:
            st.warning(f"Demo User Connection failed with error: {e}")
    elif st.session_state.conn_demo_user.is_healthy():
        connection_demo_user = st.session_state.conn_demo_user
        return connection_demo_user  
    else:
        st.warning("Please Check Oracle Database 23ai Container!!!")
        st.stop()
        return None


def init_db_connections():
    read_env_file()
    get_sys_connection()
    get_demo_user_connection()
