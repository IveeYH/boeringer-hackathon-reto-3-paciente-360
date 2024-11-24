import streamlit as st

APP_TITLE = 'Care360'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:/Users/ruben/Documents/GCP_SA/reto-3-boehringer-paciente-360-f6971bde1c10.json"
os.environ['OPENAI_API_KEY'] = "sk-svcacct-rqbdXVCV81GPr1gYrex7HUwjfnmnBnUsyWs8CQREIWwpEZC7fnsstGNY5jLLLHK1b7AT3BlbkFJ1PBRBXgI4jzvtBzQ5aqyY-BoqVp5Aq7EZitIA_e2Xpi-k3WXPcn-bJr8TO5WIi1seRAA"
st.title(APP_TITLE)

st.markdown("""
            
    Welcome to :red[Care360], your all-in-one healthcare management tool. With our platform, you can effortlessly:

    - Check Patient Stats: Access and review up-to-date health information for your patients in real-time. 
    - Create and Modify Patient Stats: Easily input or update patient data to keep records accurate and current.
    - LLM Drug Recommender: Utilize our advanced language model to get intelligent drug recommendations tailored to each patient’s unique needs.
    - Streamline your workflow, improve patient care, and make data-driven decisions with :red[Care360].

            """)






