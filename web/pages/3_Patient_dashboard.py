import streamlit as st
from google.cloud.sql.connector import Connector
import pandas as pd
from datetime import datetime
from os import environ

columns = ['id', 'analysis_datetime', 'is_smoker', 'alcohol', 'hours_sitdown', 'physical_activity', 'fam_cardiovascular_dis', 
           'age', 'sex', 'body_weight', 'height', 'waist', 'heart_rate', 'diastolic_pressure', 
           'systolic_pressure','total_choles', 'triglycerides', 'HDL_chol', 'LDL_chol', 
           'creatinine', 'albumin', 'hba1c', 'fasting_glucose', 'test_glucose']

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
    
def get_last_patient_data(id):
    """
    Returns the patients data list.
    """

    conn = postgresql_connect()

    cur = conn.cursor()
    sql = f"SELECT * FROM r3bp360.users_analytics WHERE id = '{id}' ORDER BY analysis_datetime DESC LIMIT 1;"
    cur.execute(sql)
    result = cur.fetchall()

    df = pd.DataFrame(result, columns=columns)
    return df

def get_patient_data(id):
    """
    Returns the patients data list.
    """

    conn = postgresql_connect()

    cur = conn.cursor()
    sql = f"SELECT * FROM r3bp360.users_analytics WHERE id = '{id}' ORDER BY analysis_datetime DESC;"
    cur.execute(sql)
    result = cur.fetchall()

    df = pd.DataFrame(result, columns=columns)
    df = df.drop('id', axis=1)
    return df

def get_patient_images_data(id):
    """
    Returns the patients data list.
    """

    conn = postgresql_connect()

    cur = conn.cursor()
    sql = f"SELECT images_datetime, url_image FROM r3bp360.users_images WHERE id = '{id}' ORDER BY images_datetime DESC;"
    cur.execute(sql)
    result = cur.fetchall()
    columns_images = ["images_datetime", "url_image"]

    df = pd.DataFrame(result, columns=columns_images)
    return df

def get_patient_last_doctor_comment(id):
    """
    Returns the patients doctor comment list.
    """

    conn = postgresql_connect()

    cur = conn.cursor()
    sql = f"SELECT comment_datetime, comment FROM r3bp360.doctor_comment WHERE id = '{id}' ORDER BY comment_datetime DESC LIMIT 1;"
    cur.execute(sql)
    result = cur.fetchall()
    columns_images = ["comment_datetime", "comment"]

    df = pd.DataFrame(result, columns=columns_images)
    return df


st.set_page_config(page_title="Patient Dashboard", page_icon=":material/person:")

st.title("Dashboard")


#######################################################
#                                                     #
#                       SideBar                       #
#                                                     #
#######################################################

with st.sidebar:
    id_selected = st.selectbox("Select ID patient", list(get_patients_list_id()), placeholder="Choose an ID")
    data = get_last_patient_data(id_selected[0])
    st.write(":blue[Personal parameters]")
    pi_col1, pi_col2 = st.columns(2, vertical_alignment="top")
    with pi_col1:
        st.write(f"Sex: {'Male' if data['sex'][0] == 'm' else 'Female'}")
        st.write(f"Weight: {data['body_weight'][0]} kg")
        st.write(f"Waist: {data['waist'][0]} cm")
    with pi_col2:
        st.write(f"Age: {data['age'][0]}")
        st.write(f"Height: {data['height'][0]} m")
        st.write(f"Family with cardio dis.?: {'Yes' if data['fam_cardiovascular_dis'][0] == 'y' else 'No'}")

    st.write(":blue[Daily habits]")
    dh_col1, dh_col2 = st.columns(2, vertical_alignment="top")
    with dh_col1:
        st.write(f"Smoker: {'Yes' if data['is_smoker'][0] == 'y' else 'No'}")
        st.write(f"Physical activity: {data['physical_activity'][0]} h")
        
    with dh_col2:
        st.write(f"Alcohol: {data['alcohol'][0]}")
        st.write(f"Hours sitdown: {data['hours_sitdown'][0]} h")
    
    st.write(":blue[Heart analysis]")
    ha_col1, ha_col2, ha_col3 = st.columns(3, vertical_alignment="top")
    with ha_col1:
        st.write(f"Heart rate: {data['heart_rate'][0]}") 
    with ha_col2:
        st.write(f"Diastolic pressure: {data['diastolic_pressure'][0]}")
    with ha_col3:
        st.write(f"Systolic pressure: {data['systolic_pressure'][0]}")
    
    st.write(":blue[Chem analysis]")
    ca_col1, ca_col2 = st.columns(2, vertical_alignment="top")
    with ca_col1:
        st.write(f"Total Chol: {data['total_choles'][0]}")
        st.write(f"HDL Chol: {data['HDL_chol'][0]}")
        st.write(f"Creatinine: {data['creatinine'][0]}")
        st.write(f"Albumin: {data['albumin'][0]}")
        st.write(f"Test glucose: {data['test_glucose'][0]}")
        
    with ca_col2:
        st.write(f"Triglycerides: {data['triglycerides'][0]}")
        st.write(f"LDL Chol: {data['LDL_chol'][0]}")
        st.write(f"HBA1C: {data['hba1c'][0]}")
        st.write(f"Fasting glucose: {data['fasting_glucose'][0]}")


#######################################################
#                                                     #
#                     MainBoard                       #
#                                                     #
#######################################################

tab1, tab2, tab3 = st.tabs(["Overview", "Medical history", "Graph details"])
whole_data = get_patient_data(id_selected[0])
whole_data.analysis_datetime = pd.to_datetime(whole_data.analysis_datetime)
last_analysis_date = whole_data.analysis_datetime.max()
time_between = datetime.now() - last_analysis_date


with tab1:

    st.write("The patient has irregular evolution!")
    if time_between.days > 365:
        st.warning(f"Alert, last analysis was done in {last_analysis_date}, which is more than one year ago!", icon="⚠️")

    ov_col1, ov_col2 = st.columns(2, vertical_alignment="top")
    whole_data = whole_data.set_index("analysis_datetime")
    # Weight plot
    ov_col1.subheader("Weight")
    data_weight = whole_data.body_weight
    ov_col1.line_chart(data_weight, use_container_width=True, height=150)
    # Systolic plot
    ov_col1.subheader("Systolic")
    data_systolic = whole_data.systolic_pressure
    ov_col1.line_chart(data_systolic, use_container_width=True, height=150)
    # Triglycerides plot
    ov_col1.subheader("Triglycerides")
    data_triglycerides = whole_data.triglycerides
    ov_col1.line_chart(data_triglycerides, use_container_width=True, height=150)
    # LDL_chol plot
    ov_col2.subheader("LDL_chol")
    data_LDL_chol = whole_data.LDL_chol
    ov_col2.line_chart(data_LDL_chol, use_container_width=True, height=150)
    # creatinine plot
    ov_col2.subheader("Creatinine")
    data_creatinine = whole_data.creatinine
    ov_col2.line_chart(data_creatinine, use_container_width=True, height=150)
    # LDL_chol plot
    ov_col2.subheader("Fasting glucose")
    data_fasting_glucose = whole_data.fasting_glucose
    ov_col2.line_chart(data_fasting_glucose, use_container_width=True, height=150)

with tab2:

    st.subheader("Analysis list")
    st.dataframe(whole_data)

    comments_df = get_patient_last_doctor_comment(id_selected[0])
    st.subheader("Last doctor comment")
    if len(comments_df) > 0:
        st.write(comments_df.comment[0])
    else:
        st.write("No doctor comments yet.")
    
    images_df = get_patient_images_data(id_selected[0])
    st.subheader("Images list")
    if len(images_df) > 0:
        st.markdown(images_df.to_html(render_links=True, escape=False, index=False), unsafe_allow_html=True)
    else:
        st.write("No images yet.")
    

with tab3:
    columns_clean =  columns.copy()
    columns_clean.remove('analysis_datetime')
    options = st.multiselect("Choose the desired variables", columns_clean)
    
    options_col1 = options[::2]
    options_col2 = options[1::2]
    last_option = []
    
    if len(options) % 2 != 0:
        last_option = options[-1]
        options_col1 = options_col1[:-1]
        options_col2 = options_col2[:-1]
    
    gr_col1, gr_col2 = st.columns(2, vertical_alignment="top")

    with gr_col1:
        for option in options_col1:
            st.subheader(option)
            st.line_chart(whole_data[option], use_container_width=True )
    
    with gr_col2:
        for option in options_col2:
            st.subheader(option)
            st.line_chart(whole_data[option], use_container_width=True )
    
    if last_option:
        st.subheader(last_option)
        st.line_chart(whole_data[last_option], use_container_width=True )

    