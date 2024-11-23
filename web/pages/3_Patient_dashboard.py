import streamlit as st
from google.cloud.sql.connector import Connector
import pandas as pd
from os import environ

columns = ['id', 'is_smoker', 'alcohol', 'hours_sitdown', 'physical_activity', 'fam_cardiovascular_dis', 
                              'age', 'sex', 'body_weight', 'height', 'waist', 'heart_rate', 'diastolic_pressure', 'systolic_pressure',
                              'total_choles', 'triglycerides', 'HDL_chol', 'LDL_chol', 'creatinine', 'albumin', 'hba1c', 
                              'fasting_glucose', 'test_glucose']

def postgresql_connect():
    """
    Returns the connection to the PSQL database, for further queries.
    """
    connector = Connector()
    psql_conn = connector.connect(
        "reto-3-boehringer-paciente-360:europe-west1:r3bp360-cloudsql-main-database",
        "pg8000",
        user =  environ["POSTGRES_USER"],
        password =  environ["POSTGRES_PASS"],
        db = "postgres"
    )

    return psql_conn

def get_patients_list_id():
    """
    Returns the patients data list.
    """

    conn = postgresql_connect()

    cur = conn.cursor()
    sql = f"SELECT DISTINCT id FROM r3bp360.users_analytics;"
    cur.execute(sql)
    result = cur.fetchall()
    return result
    
def get_patient_data(id):
    """
    Returns the patients data list.
    """

    conn = postgresql_connect()

    cur = conn.cursor()
    sql = f"SELECT * FROM r3bp360.users_analytics WHERE id = '{id}';"
    cur.execute(sql)
    result = cur.fetchall()

    df = pd.DataFrame(result, columns=columns)
    return df



st.set_page_config(page_title="Patient Dashboard", page_icon=":material/person:")

st.title("Dashboard")
st.subheader("Patient's main info")
with st.sidebar:
    id_selected = st.selectbox("Select ID patient", list(get_patients_list_id()), placeholder="Choose an ID")
    data = get_patient_data(id_selected[0])
    st.write(f"Sex: {data['sex'][0]}")
    st.write(f"Age: {data['age'][0]}")