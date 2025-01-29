import streamlit as st

def search_main_form():
    #default values
    if 'search_method' not in st.session_state:
        st.session_state['search_method']="Similarity Search"
    if 'use_filter' not in st.session_state:
        st.session_state['use_filter']='False'
    if 'filter_criteria' not in st.session_state:
        st.session_state['filter_criteria'] = {}    
    if 'k' not in st.session_state:
        st.session_state['k'] = "4"
    if 'score_threshold' not in st.session_state:
        st.session_state['score_threshold'] = "0.90"    
    if 'fetch_k' not in st.session_state:
        st.session_state['fetch_k'] = "20" 
    if 'lambda_mult' not in st.session_state:
        st.session_state['lambda_mult'] = "0.5" 

    def set_search_method():
        st.session_state['search_method'] = search_method    
    
    search_method = st.radio(
            "Similarity Search Method",
            ['Similarity Search','Search with Relevance Threshold','MMR Search'],
            captions=[
                "Returns similar docs",
                "Returns similar docs which have similarit above threhold with relevance scores",
                "Maximal Marginal Relevance Search, Returns most similar docs by Maximal Marginal Relevance",
            ],
            horizontal=False,
            index=0,
            on_change=set_search_method,
            help=""
        )

    return None

def search_params_form():

    def set_use_filter():
        print(use_filter)
        if use_filter:    
            st.session_state['use_filter']='True'
        else:    
            st.session_state['use_filter']='False'
    def set_filter_criteria():
        st.session_state['filter_criteria'] = filter_criteria    
    def set_k():
        st.session_state['k'] = k    
    def set_sscore_threshold():
        st.session_state['score_threshold'] = score_threshold    
    def set_fetch_k():
        st.session_state['fetch_k'] = fetch_k    
    def set_lambda_mult():
        st.session_state['lambda_mult'] = lambda_mult    

    with st.expander("Similarity Search Parameters",expanded=True):
        use_filter=st.checkbox("Use filter",on_change=set_use_filter)
        if use_filter:
            filter_criteria=st.text_input("Filter Criteria",placeholder="Enter Your Filter Values",help="Provide Some Help")
            set_filter_criteria()
        match st.session_state.search_method:
            case "Similarity Search":                        
                k = st.slider(
                    "k", 1, 10, 4,
                    on_change=set_k,
                    help="Amount of documents to return (Default: 4)") 
            case "Search with Relevance Threshold":              
                k = st.slider(
                    "k", 1, 10, 4,
                    on_change=set_k,
                    help="Amount of documents to return (Default: 4)") 
                score_threshold=st.slider(
                    "score_threshold", 0.00, 1.00, 0.90,
                    on_change=set_sscore_threshold,
                    help="Minimum relevance threshold; Only retrieve documents that have a relevance score above a certain threshold")
            case "MMR Search":
                k = st.slider(
                    "k", 1, 10, 4,
                    on_change=set_k,
                    help="Amount of documents to return (Default: 4)") 
                fetch_k = st.slider(
                    "fetch_k", 1, 100, 20, 
                    on_change=set_fetch_k,
                    help="Amount of documents to pass to MMR algorithm; (Default: 20)") 
                lambda_mult = st.slider(
                    "lambda_mult", 0.0, 1.0, 0.5,
                    on_change=set_lambda_mult,
                    help="Diversity of results returned by MMR; 1 for minimum diversity and 0 for maximum. (Default: 0.5)")

    return None