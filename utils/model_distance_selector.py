import streamlit as st
import utils.common_db_operations as db_ops
from langchain_community.vectorstores.utils import DistanceStrategy


            
def selector_form():    

    def get_selected_embedding():
        if (selected_embedding_model):
            return selected_embedding_model  
        else:
            st.warning("Select an Embedding Model")
            return None

    def get_selected_distance():
        if (selected_distance_method):
            match selected_distance_method:
                case "COSINE":
                    distance_strategy=DistanceStrategy.COSINE
                    return distance_strategy
                case "DOT_PRODUCT":
                    distance_strategy=DistanceStrategy.DOT_PRODUCT
                    return distance_strategy
                case "EUCLIDEAN_DISTANCE":
                    distance_strategy=DistanceStrategy.EUCLIDEAN_DISTANCE
                    return distance_strategy
                case "JACCARD":
                    distance_strategy=DistanceStrategy.JACCARD
                    return distance_strategy
                case "MAX_INNER_PRODUCT":
                    distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT
                    return distance_strategy
                case _:
                    st.write("Choose Distance Metric")
                    return ""  
        else:
            st.warning("Select a Distance Metric")
            return None

    def get_selected_vector_store():
        if (selected_vector_store):
            return selected_vector_store  
        else:
            st.warning("Select a Vector Store or Create a New Vector Store First")
            return None     

    def set_embedding_model():
        st.session_state['embedding_model'] = get_selected_embedding()          
    def set_distance_metric():
        st.session_state['distance_metric'] = get_selected_distance()
    def set_vector_store():
        st.session_state['vector_store'] = get_selected_vector_store() 

    selected_embedding_model = st.selectbox(
        label="Embedding Model",
        options=db_ops.get_embedding_models_list(),
        index=0,
        on_change=set_embedding_model,
        placeholder="Select an Embedding Model...",
    )
    selected_distance_method = st.selectbox(
        label="Distance Strategy ",
        options=("COSINE","DOT_PRODUCT","EUCLIDEAN_DISTANCE","JACCARD","MAX_INNER_PRODUCT"),
        index=0,
        on_change=set_distance_metric,
        placeholder="Select a Distance Metric...",
        help="Choose your metric according to your embedding model, For the details of the Distance Metrics https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/vector-distance-metrics.html"
    )
    selected_vector_store = st.selectbox(
        label="Vector Store",
        options=db_ops.get_vector_stores_list(),
        index=0,
        on_change=set_vector_store,
        placeholder="Select a Vector Store...",
    )

    set_embedding_model()
    set_distance_metric()
    set_vector_store()
    return None


