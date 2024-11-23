import streamlit as st
from google.cloud.sql.connector import Connector
import os
import random
import uuid

APP_TITLE = 'Care360'

st.title(APP_TITLE)

st.markdown("""
            
    Welcome to :red[Care360], your all-in-one healthcare management tool. With our platform, you can effortlessly:

    - Check Patient Stats: Access and review up-to-date health information for your patients in real-time. 
    - Create and Modify Patient Stats: Easily input or update patient data to keep records accurate and current.
    - LLM Drug Recommender: Utilize our advanced language model to get intelligent drug recommendations tailored to each patient’s unique needs.
    - Streamline your workflow, improve patient care, and make data-driven decisions with :red[Care360].

            """)






