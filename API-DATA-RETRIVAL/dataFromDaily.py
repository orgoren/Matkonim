import os
import csv
import requests

INPUT_FILE = os.path.dirname(os.getcwd()) + "/API-DATA-RETRIVAL/daily_intake.csv"

age_gender = set()
nutrition = {
	'sugar' : 1,
	'calcium' : 2,
	'sodium' : 3,
	'protein' : 4,
	'cholesterol' : 5,
	'potassium' : 6,
	'lactose' : 7,
	'vitaminC' : 8,
	'saturated' : 9,
	'dietary_fiber' : 10,
	'calories_kcal' : 11,
	'magnesium' : 12,
	'zinc' : 13,
	'alcohol' : 14
}

age_gender_queries = ""
# define sql queries
add_age_gender = """INSERT INTO RECOMMEND_BY_AGE_GENDER (gender, age, nutrition_id, weight_mg) VALUES ('{}',{},{},{});"""

with open(INPUT_FILE, 'r') as fin:
    reader = csv.reader(fin, lineterminator='\n')
    for row in reader:
        if row[0] != 'male' and row[0] != 'female':
            continue
        gender = row[0]
        age = row[1]
        for nutrition_id in range(0,len(row[2:])):
	        if (gender, age, nutrition_id, row[2+nutrition_id]) not in age_gender:
	            # adding new food to set
	            age_gender.add((gender, age, nutrition_id+1, row[2+nutrition_id]))
	            age_gender_queries += add_age_gender.format(gender, age, nutrition_id+1, row[2+nutrition_id])

recipes_sql2 = open('insert_age_gender.sql', 'w')
recipes_sql2.write(age_gender_queries)