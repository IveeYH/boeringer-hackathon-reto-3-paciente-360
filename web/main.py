import streamlit as st
from google.cloud.sql.connector import Connector
import os

APP_TITLE = 'Care360'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:/Users/ruben/Documents/GCP_SA/reto-3-boehringer-paciente-360-f6971bde1c10.json"

def postgresql_connect():
    """
    Returns the connection to the PSQL database, for further queries.
    """
    connector = Connector()
    psql_conn = connector.connect(
        "reto-3-boehringer-paciente-360:europe-west1:r3bp360-cloudsql-main-database",
        "pg8000",
        user =  "streamlit",
        password =  "streamlit",
        db = "postgres"
    )

    return psql_conn
    
def get_patients_list():
    """
    Returns the patients data list.
    """

    conn = postgresql_connect()

    cur = conn.cursor()
    sql = "SELECT * FROM r3bp360.users_analytics;"
    cur.execute(sql)
    result = cur.fetchall()
    return result


st.title(APP_TITLE)


st.write(get_patients_list())



