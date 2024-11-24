import streamlit as st
from google.cloud.sql.connector import Connector
import pandas as pd

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
    sql = """
        WITH ranked_rows AS (
            SELECT *,
            ROW_NUMBER() OVER (PARTITION BY id ORDER BY analysis_datetime DESC) AS rn
        FROM r3bp360.users_analytics
        )
        SELECT id, analysis_datetime, is_smoker, alcohol, hours_sitdown, physical_activity, fam_cardiovascular_dis, 
                age, sex, body_weight, height, waist, heart_rate, diastolic_pressure, systolic_pressure,
                total_choles, triglycerides, HDL_chol, LDL_chol, creatinine, albumin, hba1c, 
                fasting_glucose, test_glucose
        FROM ranked_rows
        WHERE rn = 1;    
        """
    cur.execute(sql)
    result = cur.fetchall()
    return result

columns = ['id', 'analysis_datetime', 'is_smoker', 'alcohol', 'hours_sitdown', 'physical_activity', 'fam_cardiovascular_dis', 
                              'age', 'sex', 'body_weight', 'height', 'waist', 'heart_rate', 'diastolic_pressure', 'systolic_pressure',
                              'total_choles', 'triglycerides', 'HDL_chol', 'LDL_chol', 'creatinine', 'albumin', 'hba1c', 
                              'fasting_glucose', 'test_glucose']

st.set_page_config(page_title="Whole Patient List", page_icon=":material/groups:")

st.title("Patients most recent analysis")

df = pd.DataFrame(get_patients_list(), columns=columns)

st.dataframe(df)