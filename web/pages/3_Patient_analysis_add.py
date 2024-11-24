import streamlit as st
from google.cloud.sql.connector import Connector
import random
import uuid
from datetime import datetime, timedelta
from os import environ

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
    
    

def generate_registers(n):
    """
    Generate n random registers with specific attributes: sex, age, weight, and a unique identifier.
    
    :param n: Number of registers to generate.
    :return: List of registers, where each register is a dictionary.
    """
    registers_list = []
    delta = datetime(2023,12,31) - datetime(2018,1,1)

    for _ in range(n):


        register_aux = {
            'id': str(uuid.uuid4()),
            'analysis_datetime': datetime(2018,1,1) + timedelta(seconds = random.randint(0, int(delta.total_seconds()))),
            'is_smoker':  random.choice(['y', 'n']),
            'alcohol': int(random.randint(0, 100)),
            'hours_sitdown': random.randint(0, 20),
            'physical_activity': random.randint(0, 20),
            'fam_cardiovascular_dis': random.choice(['y', 'n']),
            'age': random.randint(18, 80),
            'sex': random.choice(['m', 'f']),
            'body_weight': random.randint(40, 200),
            'height': round(random.uniform(1.40, 2.10), 2),
            'waist': random.randint(65, 150),
            'heart_rate': random.randint(30, 150),
            'diastolic_pressure':  random.randint(20, 140),
            'systolic_pressure': random.randint(50, 240),
            'total_choles': random.randint(100, 1000),
            'triglycerides': random.randint(10, 2000),
            'HDL_chol': random.randint(10, 100),
            'LDL_chol': random.randint(10, 700),
            'creatinine': round(random.uniform(0.1, 10), 2),
            'albumin': round(random.uniform(1, 5.5), 2),
            'hba1c': random.randint(4, 14),
            'fasting_glucose': random.randint(40, 300),
            'test_glucose': random.randint(40, 400)
        }

        
        registers_list.append(register_aux)
    
    return registers_list

def write_patient_register(register_list):

    conn = postgresql_connect()
    cur = conn.cursor()
    insert_query = """
    INSERT INTO r3bp360.users_analytics (id, analysis_datetime, is_smoker, alcohol, hours_sitdown, physical_activity, fam_cardiovascular_dis, 
                              age, sex, body_weight, height, waist, heart_rate, diastolic_pressure, systolic_pressure,
                              total_choles, triglycerides, HDL_chol, LDL_chol, creatinine, albumin, hba1c, 
                              fasting_glucose, test_glucose)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    for register in register_list:
        values = (
            register['id'], register['analysis_datetime'], register['is_smoker'], register['alcohol'], register['hours_sitdown'], 
            register['physical_activity'], register['fam_cardiovascular_dis'], register['age'], register['sex'],
            register['body_weight'], register['height'], register['waist'], register['heart_rate'], 
            register['diastolic_pressure'], register['systolic_pressure'], register['total_choles'], 
            register['triglycerides'], register['HDL_chol'], register['LDL_chol'], register['creatinine'], 
            register['albumin'], register['hba1c'], register['fasting_glucose'], register['test_glucose']
        )

        # Execute insert statement for the current register
        cur.execute(insert_query, values)

    conn.commit()
    print("Data inserted successfully!")

st.set_page_config(page_title="Add new patient", page_icon=":material/group_add:")

st.title("Add/Update patient info")
st.write("In this page you can add or modify the patient info, to keep up-to-date!")

#### Mockup Data
st.header("Add a random register!")
st.write("""With this functionality, you can create random registers as examples! This can ease you how this tool works
             and what can you do with all the new data!""")
nr_col1, nr_col2 = st.columns(2, vertical_alignment="bottom")
with nr_col1:
    number_patients = st.number_input("Insert the number of mockup patients to write in the DB",
                                  value=None,
                                  placeholder="Type a number...",
                                  step=1)
    

with nr_col2:
    if st.button("Submit"):
        register_list = generate_registers(number_patients)
        write_patient_register(register_list)
        st.write(f"A total of {number_patients} new mockup patients have been created!")

#### Create new register
st.header("Create a new analysis register!")
st.write("""With this functionality, you can create a register!""")

with st.form("add_patient"):
    new_patient = {}

    new_patient['id'] = st.selectbox("Patient_id", list(get_patients_list_id()))[0]
    
    ad_col1, ad_col2 = st.columns(2, vertical_alignment="top")
    with ad_col1:
        new_analysis_date = st.date_input("analysis_date")
    with ad_col2:
        new_analysis_time = st.time_input("analysis_time")
    
    new_patient['analysis_datetime'] = datetime.combine(new_analysis_date, new_analysis_time)
    
    st.write(":blue[Personal parameters]")
    fc_pp_col1, fc_pp_col2 = st.columns(2, vertical_alignment="top")

    with fc_pp_col1:
        new_patient['sex'] = st.selectbox("sex", ["f", "m"])
        new_patient['body_weight'] = st.number_input("body_weight", min_value=40, max_value=200, step=1)
        new_patient['waist'] = st.number_input("waist", min_value=65, max_value=150, step=1)
    
    with fc_pp_col2:
        new_patient['age'] = st.number_input("age", min_value=18, max_value=80, step=1)
        new_patient['height'] = st.number_input("height", min_value=1.4, max_value=2.1, step=0.01)
        new_patient['fam_cardiovascular_dis'] = st.selectbox("fam_cardiovascular_dis", ["y", "n"])
    
    st.write(":blue[Daily habits]")
    fc_dh_col1, fc_dh_col2 = st.columns(2, vertical_alignment="top")

    with fc_dh_col1:
        new_patient['is_smoker'] = st.selectbox("is_smoker", ["y", "n"])
        new_patient['physical_activity'] = st.number_input("physical_activity", min_value=0, max_value=20, step=1)
    
    with fc_dh_col2:
        new_patient['alcohol'] = st.number_input("alcohol", min_value=0, max_value=100, step=1)
        new_patient['hours_sitdown'] = st.number_input("hours_sitdown", min_value=0, max_value=20, step=1)
    
    st.write(":blue[[Heart analysis]")
    fc_ha_col1, fc_ha_col2, fc_ha_col3 = st.columns(3, vertical_alignment="top")

    with fc_ha_col1:
        new_patient['heart_rate'] = st.number_input("heart_rate", min_value=30, max_value=150, step=1)
    with fc_ha_col2:
        new_patient['diastolic_pressure'] = st.number_input("diastolic_pressure", min_value=20, max_value=140, step=1)
    with fc_ha_col3:
        new_patient['systolic_pressure'] = st.number_input("systolic_pressure", min_value=50, max_value=240, step=1)
    
    st.write(":blue[Chem analysis]")
    fc_ca_col1, fc_ca_col2 = st.columns(2, vertical_alignment="top")

    with fc_ca_col1:
        new_patient['total_choles'] = st.number_input("total_choles", min_value=100, max_value=1000, step=1)
        new_patient['HDL_chol'] = st.number_input("HDL_chol", min_value=10, max_value=100, step=1)
        new_patient['creatinine'] = st.number_input("creatinine", min_value=0.1, max_value=10.0, step=0.01)
        new_patient['albumin'] = st.number_input("albumin", min_value=1.0, max_value=5.5, step=0.01)
        new_patient['test_glucose'] = st.number_input("test_glucose", min_value=40, max_value=400, step=1)
    
    with fc_ca_col2:
        new_patient['triglycerides'] = st.number_input("triglycerides", min_value=10, max_value=2000, step=1)
        new_patient['LDL_chol'] = st.number_input("LDL_chol", min_value=10, max_value=700, step=1)
        new_patient['hba1c'] = st.number_input("hba1c", min_value=4.0, max_value=14.0, step=0.01)
        new_patient['fasting_glucose'] = st.number_input("fasting_glucose", min_value=40, max_value=300, step=1)


    submitted = st.form_submit_button("Submit new analysis")
    if submitted:
        write_patient_register([new_patient])
        st.write("New analysis written")
