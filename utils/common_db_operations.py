import streamlit as st
import utils.db_connection as db
import pandas as pd


def get_embedding_models_table():
    db.get_vector_user_connection()
    connection=st.session_state.conn_vector_user
    #query to find the vector embedding models that currently exists in DB

    sql1 = """SELECT MODEL_NAME, MINING_FUNCTION, ALGORITHM,
            ALGORITHM_TYPE, ROUND((MODEL_SIZE/1024/1024/1024),2) MODEL_SIZE_GB
            FROM all_mining_models where mining_function =:m_func
            """
    r_count=0
    cursor = connection.cursor()
    try:
        cursor.execute(sql1,m_func="EMBEDDING")
        rows = cursor.fetchall()
        r_count=cursor.rowcount       
    except Exception as e:
        st.warning(f"Loaded Models Couldn't be retrieved from DB: {e}")
    finally:
        cursor.close()
    if (r_count>0):
        embedding_models_list=[[row[0],row[1],row[2],row[3],row[4]] for row in rows]
        df=pd.DataFrame(embedding_models_list,columns=["Model Name", "Mining Function", "Algorithm","Algorithm Type", "Model Size (GB)"],index=None)
        st.dataframe(df)
    else:
        st.write("There are no embedding models exist in database")

def get_embedding_models_list():
    db.get_vector_user_connection()
    connection=st.session_state.conn_vector_user
    #query to find the vector embedding models that currently exists in DB
    sql1 = """SELECT model_name, vector_info
    FROM user_mining_model_attributes
    WHERE attribute_type = :atype
    ORDER BY model_name
    """
    r_count=0
    cursor = connection.cursor()
    try:
        cursor.execute(sql1,atype="VECTOR")
        rows = cursor.fetchall()
        r_count=cursor.rowcount;
    except Exception as e:
        st.warning(f"Loaded Models Couldn't be retrieved from DB: {e}")
    finally:
        cursor.close()
    if (r_count>0):        
        embedding_models_list=[row[0] for row in rows]
    else:
        st.write("There are no embedding models exist in database")
        embedding_models_list=[]
    return embedding_models_list

def get_vector_stores_list():
    db.get_vector_user_connection()
    connection=st.session_state.conn_vector_user
    #query to find the vector embedding models that currently exists in DB
    sql1 = "SELECT distinct table_name FROM user_tab_columns where data_type=:dtype"
    r_count=0
    cursor = connection.cursor()
    try:
        cursor.execute(sql1,dtype="VECTOR")
        rows = cursor.fetchall()
        r_count=cursor.rowcount

    except Exception as e:
        st.warning(f"Vector Stores Couldn't be retrieved from DB: {e}")
    finally:
        cursor.close()
    if (r_count>0):
        vector_store_list=[row[0] for row in rows]
    else:
        st.write("There are no Vector Store in Database")
        vector_store_list=[]
    return vector_store_list

def get_tables_list():
    db.get_vector_user_connection()
    connection=st.session_state.conn_vector_user
    #query to find the vector embedding models that currently exists in DB
    sql1 = """SELECT distinct table_name
    FROM user_tables where table_name not like '%$%'
    ORDER BY table_name
    """
    r_count=0
    cursor = connection.cursor()
    try:
        cursor.execute(sql1)
        rows = cursor.fetchall()
        r_count=cursor.rowcount;        
    except Exception as e:
        st.warning(f"Tables Couldn't be retrieved from DB: {e}")
    finally:
        cursor.close()
    if (r_count>0):
        table_list=[row[0] for row in rows]
    else:
        st.write("There are no tables in Database")
        table_list=[]
    return table_list

def get_columns_list(table_name):
    db.get_vector_user_connection()
    connection=st.session_state.conn_vector_user
    #query to find the vector embedding models that currently exists in DB
    sql1 = """SELECT distinct column_name
    FROM user_tab_columns
    WHERE table_name = :tname
    ORDER BY table_name
    """
    r_count=0
    cursor = connection.cursor()
    try:
        cursor.execute(sql1,tname=table_name)
        rows = cursor.fetchall()
        r_count=cursor.rowcount;        
    except Exception as e:
        st.warning(f"Columns Couldn't be retrieved from DB: {e}")
    finally:
        cursor.close()
    if (r_count>0):
        columns_list=[row[0] for row in rows]
    else:
        st.write("There are no columns in table")
        columns_list=[]
    return columns_list

def configure_vector_user():
    try:
        #Connection will be as SYS to make configuration
        #connection = oracledb.connect(user="SYS", password=st.session_state.oracle_passwd, dsn=st.session_state.dsn,mode=oracledb.SYSDBA)
        db.get_sys_connection()
        connection=st.session_state.conn_sys
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                begin
                    -- Drop user
                    begin
                        execute immediate 'drop user VECTOR_USER cascade';
                    exception
                        when others then
                            dbms_output.put_line('Error dropping user: ' || SQLERRM);
                    end;
                    
                    -- Create user and grant privileges
                    execute immediate 'create user VECTOR_USER identified by Oracle123';
                    execute immediate 'grant connect, unlimited tablespace, create credential, create any table, create procedure, create any index to VECTOR_USER';
                    execute immediate 'create or replace directory DEMO_PY_DIR as ''/tmp/oracle_volume''';
                    execute immediate 'grant read, write on directory DEMO_PY_DIR to public';
                    execute immediate 'grant create mining model to VECTOR_USER';
                    
                    -- Network access
                    begin
                        DBMS_NETWORK_ACL_ADMIN.APPEND_HOST_ACE(
                            host => '*',
                            ace => xs$ace_type(privilege_list => xs$name_list('connect'),
                                            principal_name => 'VECTOR_USER',
                                            principal_type => xs_acl.ptype_db)
                        );
                    end;
                end;
                """
            )
            st.write("User setup done")
            db.get_vector_user_connection()
            return True
        except Exception as e:
            st.warning(f"User setup failed with error: {e}")
        finally:
            cursor.close()
        #st.stop()
    except Exception as e:
        print(f"Connection failed with error: {e}")
        st.stop()

