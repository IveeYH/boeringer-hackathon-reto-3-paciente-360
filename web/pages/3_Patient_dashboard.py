import streamlit as st
from google.cloud.sql.connector import Connector
import pandas as pd
from datetime import datetime
import openai
from os import environ
import matplotlib.pyplot as plt

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

def prevent_risk_with_ckd(row):
    """
    Calcula el riesgo cardiovascular a 10 años basado en el modelo PREVENT actualizado.
    Incluye enfermedad renal (eGFR) como un factor adicional. Devuelve un % de riesgo.
    También convierte `is_smoker` de "Yes/No" (str) a 1/0 (int) dentro de la función.
    """

    # Coeficientes del modelo PREVENT con eGFR
    if row['sex'] == "women":
        coeffs = {
            "age": 0.0562,
            "systolic_pressure": 0.0188,
            "is_smoker": 0.265,
            "diabetes": 0.33,
            "cholesterol_ratio": 0.182,
            "fam_cardiovascular_dis": 0.42,
            "eGFR": -0.015,
        }
        intercept = -6.72
    else:
        coeffs = {
            "age": 0.0726,
            "systolic_pressure": 0.0212,
            "is_smoker": 0.343,
            "diabetes": 0.39,
            "cholesterol_ratio": 0.201,
            "fam_cardiovascular_dis": 0.47,
            "eGFR": -0.017,
        }
        intercept = -6.11
    
    if row['is_smoker'] == 'y':
        is_smoker = 1
    else:
        is_smoker = 0
    if row['fam_cardiovascular_dis'] == 'y':
        fam_cardiovascular_dis = 1
    else:
        fam_cardiovascular_dis = 0

    # Cálculo de la puntuación
    score = (
        coeffs["age"] * row['age'] +
        coeffs["systolic_pressure"] * row['systolic_pressure'] +
        coeffs["is_smoker"] * is_smoker +
        coeffs["diabetes"] * 0 +
        coeffs["cholesterol_ratio"] * (row['total_choles'] / row['HDL_chol']) +
        coeffs["fam_cardiovascular_dis"] * fam_cardiovascular_dis
    ) + intercept

    # Conversión a probabilidad de riesgo (función logística)
    risk = 1 / (1 + 2.71828 ** -score)  # Función sigmoidal
    cvd_risk = round(risk * 100, 2)
    return cvd_risk

    
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


def bmi(body_weight, height):
    return round(body_weight / (height ** 2), 2)


def summary_generator(sex, age, bmi, total_chol, ldl_chol, creatinine, albumin, fasting_glucose, min_words=30, max_words=50):

    prompt = f"""
        You are a medical professional. You are examining a patient and have been provided with their analytical data. Each variable impacts the patient's health. Do not make any predictions, only describe the current state. If any variable is null, do not mention or consider it.

        Once done, generate a summary of 30 to 50 words based on the following variables:

        Sex: {sex}
        Age: {age}
        Body Mass Index: {bmi}
        Total Cholesterol: {total_chol}
        LDL Cholesterol: {ldl_chol}
        Urinary Creatinine: {creatinine}
        Blood Albumin: {albumin}
        Fasting Glucose: {fasting_glucose}
        Here is an example of the expected output:
        A 35-year-old woman with obesity (BMI of 35), elevated cholesterol (total 215 mg/dl, LDL 170 mg/dl), fasting glucose near the upper normal limit (102 mg/dl), low albumin (22 g/l), and urinary creatinine in the low range (0.5 mg/dl).
    """

    client = openai.OpenAI()

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": prompt
                }
            ]
        )

        resumen = response.choices[0].message.content
        return resumen
    
    except Exception as e:
        print(f"Error al generar el resumen: {e}")
        return ""


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

    st.write(summary_generator(
        sex=data.sex,
        age=data.age,
        bmi=bmi(body_weight=data.body_weight, height=data.height),
        total_chol=data.total_choles,
        ldl_chol=data.LDL_chol,
        creatinine=data.creatinine,
        albumin=data.albumin,
        fasting_glucose=data.fasting_glucose
    ))

    if time_between.days > 365:
        st.warning(f"Alert, last analysis was done in {last_analysis_date}, which is more than one year ago!", icon="⚠️")
    
    whole_data["risk_ckd"] =  whole_data.apply(prevent_risk_with_ckd, axis=1)



    graph1_data = whole_data[['total_choles', 'triglycerides', 'HDL_chol', 'LDL_chol', 'analysis_datetime']].copy()
    graph2_data = whole_data[['sex', 'age', 'albumin', 'creatinine', 'diastolic_pressure', 'systolic_pressure', 'analysis_datetime']].copy()
    
    # Calculations
    graph1_data['total_choles'] = graph1_data['total_choles'] * 0.0259
    graph1_data['triglycerides'] = graph1_data['triglycerides'] * 0.0113
    graph1_data['HDL_chol'] = graph1_data['HDL_chol'] * 0.0259
    graph1_data['LDL_chol'] = graph1_data['LDL_chol'] * 0.0259

    graph2_data['creatinine'] = graph2_data['creatinine'].astype(float) * 88.4

    ov_col1, ov_col2 = st.columns(2, vertical_alignment="top")
    
    with ov_col1:
        p = graph1_data.plot(x='analysis_datetime', y=['total_choles', 'triglycerides', 'HDL_chol', 'LDL_chol'], ylabel="mmol/l", xlabel="Analysis date")
        st.pyplot(p.figure)
    
    with ov_col2:
        p2 = graph2_data.plot(x='analysis_datetime', y=['albumin', 'creatinine', 'diastolic_pressure', 'systolic_pressure'], xlabel="Analysis date")
        st.pyplot(p2.figure)
    
    most_recent_row = whole_data.loc[whole_data.index.max()]
    if most_recent_row['risk_ckd'] > 80:
        st.warning(f"Alert, last analysis showed a CKD risk higher than 80!", icon="⚠️")

    column_risk = most_recent_row['risk_ckd']
    remaining_value = 100 - column_risk

    fig, ax = plt.subplots()
    ax.pie(
        [column_risk, remaining_value],
        autopct='%1.1f%%',
    )

    st.pyplot(fig)

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

    