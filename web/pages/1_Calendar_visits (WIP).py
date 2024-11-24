import streamlit as st
from google.cloud.sql.connector import Connector
import pandas as pd
from datetime import datetime
from os import environ
import matplotlib.pyplot as plt
import july

def postgresql_connect():
    """
    Returns the connection to the PSQL database, for further queries.
    """
    connector = Connector()
    psql_conn = connector.connect(
        "reto-3-boehringer-paciente-360:europe-west1:r3bp360-cloudsql-main-database",
        "pg8000",
        user =  'streamlit',
        password =  'streamlit',
        db = "postgres"
    )

    return psql_conn

def get_visit_data():
    """
    Returns the patients data list.
    """

    columns = ['patient_id', 'visit_datetime', 'is_done']

    conn = postgresql_connect()

    cur = conn.cursor()
    sql = f"SELECT patient_id, visit_datetime, is_done FROM r3bp360.visit_list;"
    cur.execute(sql)
    result = cur.fetchall()
    df = pd.DataFrame(result, columns=columns)
    return df
    

st.set_page_config(page_title="Calendar visits", page_icon=":material/calendar_month:")

st.title("Dashboard")


#######################################################
#                                                     #
#                       SideBar                       #
#                                                     #
#######################################################

visits_data = get_visit_data()
grouped_data = visits_data.groupby(visits_data['visit_datetime'].dt.date).size().reset_index(name = 'counts')
grouped_data.columns = ['visit_date', 'visit_count']
cal_col1, cal_col2 = st.columns(2, vertical_alignment="top")
with cal_col1:
    month_cal = st.selectbox("Month", options=range(1,12))
with cal_col2:
    year_cal = st.selectbox("Year", options=range(2023,2026))
fig, ax = plt.subplots()

july.month_plot(
    dates=grouped_data.visit_date, 
    data=grouped_data.visit_count, 
    month=month_cal,
    year=year_cal,
    value_label=True,
    title=f"{year_cal}-{month_cal}",
    ax=ax)
st.pyplot(fig)