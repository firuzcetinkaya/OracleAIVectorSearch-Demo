import streamlit as st
from langchain_community.document_loaders.oracleai import OracleTextSplitter 

supported_languages=["ALBANIAN","AMERICAN","ARABIC","ARMENIAN","AZERBAIJANI","BULGARIAN","CROATIAN","CZECH","DANISH","DUTCH","EGYPTIAN","ENGLISH","ESTONIAN","FINNISH","FRENCH","GEORGIAN","GERMAN","GREEK","HEBREW","HINDI","HUNGARIAN","ICELANDIC","INDONESIAN","IRISH","ITALIAN","JAPANESE","KOREAN","KYRGYZ","LATVIAN","LITHUANIAN","MACEDONIAN","MALAY","NORWEGIAN","PERSIAN","POLISH","PORTUGUESE","PUNJABI","ROMANIAN","RUSSIAN","SIMPLIFIED CHINESE","SLOVAK","SLOVENIAN","SPANISH","SWAHILI","SWEDISH","TAMIL","THAI","TRADITIONAL CHINESE","TURKISH","TURKMEN","UKRAINIAN","URDU","VIETNAMESE"]

def create_splitter():
    splitter_params = {
        "BY" :st.session_state.by, 
        "MAX": st.session_state.max, 
        "OVERLAP": st.session_state.overlap, 
        "SPLIT": st.session_state.split_by, 
        "LANGUAGE": st.session_state.language, 
        "NORMALIZE": st.session_state.normalize}
    splitter = OracleTextSplitter(conn=st.session_state.conn_demo_user, params=splitter_params)    
    return splitter
    
def split_parameters_form():    

    def set_by():
        st.session_state['by'] = by          
    def set_splitby():
        st.session_state['split_by'] = split_by
    def set_max():
        st.session_state['max'] = max 
    def set_overlap():
        st.session_state['overlap'] = overlap 
    def set_language():
        st.session_state['language'] = language 
    def set_normalization():
        st.session_state['normalize'] = normalize 

    by = st.radio(
        "Split Unit",
        ["CHARS", "WORDS", "VOCABULARY"],
        captions=[
            "Chars",
            "Words",
            "Vocabulary",
        ],index=1,
        on_change=set_by,
        horizontal=True,
        help="For the Oracle Split Example visit https://python.langchain.com/v0.2/docs/integrations/document_loaders/oracleai/#split-documents"
    )
    m1,m2 = st.columns(2,gap='medium')
    with m1:
        if by=="CHARS":
            max = st.slider("Max", 50, 4000, 400,on_change=set_max)
        if by=="WORDS":
            max = st.slider("Max", 10, 1000, 25,on_change=set_max)
        if by=="VOCABULARY":
            max = st.slider("Max", 10, 1000, 25,on_change=set_max)  
        split_by = st.selectbox(
            "Split By",
            ("NONE","BY NEWLINE","RECURSIVELY","SENTENCE","CUSTOM (Not Implemented in the Demo)"),
            index=1,
            on_change=set_splitby,
            placeholder="Select split by method...",
            )
        #languages from Oracle DB Supported Langs, refine the language list as desired
        language = st.selectbox(
            "Language ",
            (supported_languages),
            index=11,
            on_change=set_language,
            placeholder="Select language...",
        )
    with m2:
        overlap = st.slider(
            "Overlap", 5, 20, 0,
            on_change=set_overlap,
            help="Valid value: 5% to 20% of MAX, Default value: 0") 
        normalize = st.selectbox(
            "Normalization ",
            ("NONE","ALL"),
            index=1,
            on_change=set_normalization,
            placeholder="Select normalization method...",
            )

    return None