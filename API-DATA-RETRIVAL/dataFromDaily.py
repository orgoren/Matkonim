import os
import csv
import requests

INPUT_FILE = os.path.dirname(os.getcwd()) + "/API-DATA-RETRIVAL/daily_intake.csv"

age_gender = set()

age_gender_queries = ""
# define sql queries
add_age_gender = """INSERT INTO RECOMMEND_BY_AGE_GENDER (gender, age, protein_mg, cholesterol_mg_MAX, potassium_mg, lactose_mg, vitaminC_mg, saturated_fat_mg_MAX, dietary_fiber_mg, calories_kcal, alcohol_mg_MAX, magnesium_mg, zinc_mg) VALUES ('{}',{},{},{},{},{},{},{},{},{},{},{},{});"""

with open(INPUT_FILE, 'r') as fin:
    reader = csv.reader(fin, lineterminator='\n')

    for row in reader:
        if row[1] == 'age':
            continue
        gender = row[1]
        age = row[2]
        protein_mg = row[3]
        cholesterol_mg_MAX = row[4]
        potassium_mg = row[5]
        lactose_mg = row[6]
        vitaminC_mg = row[7]
        saturated_fat_mg_MAX = row[8]
        dietary_fiber_mg = row[9]
        calories_kcal = row[10]
        alcohol_mg_MAX = row[11]
        magnesium_mg = row[12]
        zinc_mg = row[13]

        if (gender, age, protein_mg, cholesterol_mg_MAX, potassium_mg, lactose_mg, vitaminC_mg, saturated_fat_mg_MAX, dietary_fiber_mg, calories_kcal, alcohol_mg_MAX, magnesium_mg, zinc_mg) in age_gender:
            continue
        else:
            # adding new food to set
            age_gender.add((gender, age, protein_mg, cholesterol_mg_MAX, potassium_mg, lactose_mg, vitaminC_mg, saturated_fat_mg_MAX, dietary_fiber_mg, calories_kcal, alcohol_mg_MAX, magnesium_mg, zinc_mg))
            age_gender_queries += add_age_gender.format(gender, age, protein_mg, cholesterol_mg_MAX, potassium_mg, lactose_mg, vitaminC_mg, saturated_fat_mg_MAX, dietary_fiber_mg, calories_kcal, alcohol_mg_MAX, magnesium_mg, zinc_mg)

recipes_sql2 = open('insert_age_gender.sql', 'w')
recipes_sql2.write(age_gender_queries)