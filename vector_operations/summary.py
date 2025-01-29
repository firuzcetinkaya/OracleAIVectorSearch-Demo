import streamlit as st
from langchain_community.utilities.oracleai import OracleSummary

supported_languages=["ALBANIAN","AMERICAN","ARABIC","ARMENIAN","AZERBAIJANI","BULGARIAN","CROATIAN","CZECH","DANISH","DUTCH","EGYPTIAN","ENGLISH","ESTONIAN","FINNISH","FRENCH","GEORGIAN","GERMAN","GREEK","HEBREW","HINDI","HUNGARIAN","ICELANDIC","INDONESIAN","IRISH","ITALIAN","JAPANESE","KOREAN","KYRGYZ","LATVIAN","LITHUANIAN","MACEDONIAN","MALAY","NORWEGIAN","PERSIAN","POLISH","PORTUGUESE","PUNJABI","ROMANIAN","RUSSIAN","SIMPLIFIED CHINESE","SLOVAK","SLOVENIAN","SPANISH","SWAHILI","SWEDISH","TAMIL","THAI","TRADITIONAL CHINESE","TURKISH","TURKMEN","UKRAINIAN","URDU","VIETNAMESE"]

def create_summarizer():
    proxy=""
    summary_params  = {"provider": st.session_state.provider, "model": st.session_state.embedding_model} 
    summary = OracleSummary(conn=st.session_state.conn_demo_user, params=summary_params, proxy=proxy)
    return summary
            
def summary_parameters_form():    

    def set_provider():
        st.session_state['provider'] = provider          
    def set_glevel():
        st.session_state['glevel'] = glevel
    def set_max_percent():
        st.session_state['max_percent'] = maxPercent 
    def set_language():
        st.session_state['language'] = language 
    def set_num_paragraphs():
        st.session_state['num_paragraphs'] = numParagraphs 
    def set_num_themes():
        st.session_state['num_themes'] = num_themes 

    provider = st.radio(
        "Summary Embedding Model Provider",
        ["DATABASE", "EXTERNAL"],
        horizontal=True,
        index=0,
        on_change=set_provider,
        help="For the Oracle Split Example visit https://python.langchain.com/v0.2/docs/integrations/document_loaders/oracleai/#split-documents"
    )
    glevel = st.radio(
            "GLevel",
            ["S", "P"],
            captions=[
                "Sentence",
                "Paragraph",
            ],horizontal=True,
            index=0,
            on_change=set_glevel,
            help="For the Oracle Split Example visit https://python.langchain.com/v0.2/docs/integrations/document_loaders/oracleai/#split-documents"
        )
    m1,m2 = st.columns(2,gap='medium')
    with m1:
        maxPercent = st.slider(
            "maxPercent", 0, 100, 10,
            on_change=set_max_percent,
            help="Maximum number of document paragraphs (or sentences) selected for the summary, as a percentage of the total paragraphs (or sentences) in the document. The default value is 10.")
        language = st.selectbox(
            "Language",
            (supported_languages),
            index=11,
            on_change=set_language,
            placeholder="Select language...",
            )   
    with m2:
        numParagraphs = st.text_input(
            "numParagraphs", 16,
            on_change=set_num_paragraphs,
            help="Maximum number of document paragraphs (or sentences) selected for the summary. The default value is 16.") 
        num_themes = st.slider(
            "num_themes", 0, 50, 50,
            on_change=set_num_themes,
            help="Number of theme summaries to produce. For example, if you specify 10, then this function returns the top 10 theme summaries. If you specify 0 or NULL, then this function returns all themes in a document. The default value is 50. If the document contains more than 50 themes, only the top 50 themes show conceptual hierarchy.")

    return None