import random
import uuid


def generate_registers(n):
    """
    Generate n random registers with specific attributes: sex, age, weight, and a unique identifier.
    
    :param n: Number of registers to generate.
    :return: List of registers, where each register is a dictionary.
    """
    registers_list = []

    for _ in range(n):

        register_aux = {
            'id': str(uuid.uuid4()),
            'is_smoker':  random.choice(['y', 'n']),
            'alcohol': random.randint(0, 100),
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

        print(register_aux)
        
        registers_list.append(register_aux)
    
    return registers_list

generate_registers(10)