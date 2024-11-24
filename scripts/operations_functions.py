


class PatientAnalysisClass():

    def __init__(self, patient_data):
        """
        Check if the values input exist.
        """
        self.height = patient_data['height'][0]
        self.weight = patient_data['weight'][0]
        self.systolic_pressure = patient_data['systolic_pressure'][0]
        self.diastolic_pressure = patient_data['diastolic_pressure'][0]
        self.fasting_glucose = patient_data['fasting_glucose'][0]
        self.hba1c = patient_data['hba1c'][0]
        self.ogtt = patient_data['ogtt'][0]
        self.waist = patient_data['waist'][0]
        self.sex = patient_data['sex'][0]
        self.triglycerides = patient_data['triglycerides'][0]
        self.HDL_chol = patient_data['HDL_chol'][0]
        self.creatinine = patient_data['creatinine'][0]
        self.age = patient_data['age'][0]
        self.albumin = patient_data['albumin'][0]
        self.smoking = patient_data['is_smoker'][0]
        self.fam_cardiovascularDis = patient_data['fam_cardiovascular_dis'][0]

# Función para calcular el IMC
    def BMI(self):
        return round(self.weight / (self.height ** 2), 2)

# Función para clasificar el IMC
    def classification_BMI(self):
        BMI = self.BMI()
        if BMI < 16:
            return "Severe malnutrition"
        elif 16 <= BMI < 17:
            return "Moderate malnutrition"
        elif 17 <= BMI < 18.5:
            return "Mild malnutrition"
        elif 18.5 <= BMI < 25:
            return "Normal weight"
        elif 25 <= BMI < 30:
            return "Overweight"
        elif 30 <= BMI < 35:
            return "Obese I"
        elif 35 <= BMI < 40:
            return "Obese II"
        else:
            return "Obese III"
        
    def classification_hta(self):
        systolic_pressure = self.systolic_pressure
        diastolic_pressure = self.diastolic_pressure

        if systolic_pressure < 120 and diastolic_pressure < 80:
            return "Normal pressure"
        elif 120 <= systolic_pressure < 130 and diastolic_pressure < 80:
            return "High pressure (Prehypertension)"
        elif 130 <= systolic_pressure < 140 or 80 <= diastolic_pressure < 90:
            return "Hypertension 1"
        elif 140 <= systolic_pressure < 180 or 90 <= diastolic_pressure < 120:
            return "Hypertension 2"
        elif systolic_pressure >= 180 or diastolic_pressure >= 120:
            return "High Hypertesion"
        else:
            return "No hypertension"
        
    def classification_fasting_glucose(self):
        fasting_glucose = self.fasting_glucose
        if fasting_glucose  < 100:
            return "Normal Glucose"
        elif 100 <= fasting_glucose <= 125:
            return "Prediabetes"
        else:  # glucosa_ayuno >= 126
            return "Diabetes"

    # Función para clasificar según HbA1c
    def classification_hba1c(self):
        hba1c = self.hba1c
        if hba1c < 5.7:
            return "normal HbA1c"
        elif 5.7 <= hba1c <= 6.4:
            return "Prediabetes"
        else:  # hba1c >= 6.5
            return "Diabetes"

    # Función para clasificar según OGTT
    def classification_ogtt(self):
        ogtt = self.ogtt
        if ogtt < 140:
            return "Nomral OGTT "
        elif 140 <= ogtt <= 199:
            return "Prediabetes"
        else:  # ogtt >= 200
            return "Diabetes"

    def Metabolic_syndrome(self):
        criteria = 0
        #Criterios
        if self.waist >= (102 if self.sex == "m" else 88):
            criteria += 1
        if self.triglycerides >= 150:
            criteria += 1
        if self.HDL_chol < (40 if self.sex == "m" else 50):
            criteria += 1
        if self.systolic_pressure >= 130 or self.diastolic_pressure >= 85:
            criteria += 1
        if self.fasting_glucose >= 100:
            criteria += 1

    # Diagnóstico
        if criteria >= 3:
            return "You have metabolic syndrome"
        else:
            return "You are ok"
    
    # Definir eGFR
    def egfr(self):
        if self.sex == "w":
            kappa, alpha, factor_sex = 0.7, -0.329, 1.018
        else:  # hombre
            kappa, alpha, factor_sex = 0.9, -0.411, 1.0
        min_ratio = min(self.creatinine / kappa, 1) ** alpha
        max_ratio = max(self.creatinine / kappa, 1) ** -1.209
        egfr_value = 141 * min_ratio * max_ratio * (0.993 ** self.age) * factor_sex
        return round(egfr_value, 2)

    # Función para clasificar albuminuria
    def classify_albuminuria(self):
        if self.albumin < 30:
            return "A1 (<30 mg/g)"
        elif 30 <= self.albumin <= 300:
            return "A2 (30-300 mg/g)"
        else:
            return "A3 (>300 mg/g)"

    # Función para clasificar la CKD basada en eGFR
    def classify_egfr(self):
        egfr = self.egfr()
        if egfr >= 90:
            return "G1 (≥90)"
        elif 60 <= egfr < 90:
            return "G2 (60-89)"
        elif 45 <= egfr < 60:
            return "G3a (45-59)"
        elif 30 <= egfr < 45:
            return "G3b (30-44)"
        elif 15 <= egfr < 30:
            return "G4 (15-29)"
        else:  # egfr < 15
            return "G5 (<15)"



    # Función para evaluar el riesgo KDIGO
    def evaluate_kdigo_risk(self):
        # Matriz de riesgo KDIGO
        kdigo_matrix = {
            "G1 (≥90)": ["Bajo", "Moderado", "Alto"],
            "G2 (60-89)": ["Bajo", "Moderado", "Alto"],
            "G3a (45-59)": ["Moderado", "Alto", "Muy alto"],
            "G3b (30-44)": ["Alto", "Muy alto", "Muy alto"],
            "G4 (15-29)": ["Muy alto", "Muy alto", "Muy alto"],
            "G5 (<15)": ["Muy alto", "Muy alto", "Muy alto"]
        }

        # Índice de albuminuria para la matriz KDIGO
        albuminuria_index = {"A1 (<30 mg/g)": 0, "A2 (30-300 mg/g)": 1, "A3 (>300 mg/g)": 2}

        egfr_category = self.classify_egfr()
        albumin_category = self.classify_albuminuria(self.albumin)
        risk = kdigo_matrix[egfr_category][albuminuria_index[albumin_category]]
        return egfr_category, albumin_category, risk