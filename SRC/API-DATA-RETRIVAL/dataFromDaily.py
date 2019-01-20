import os
import csv
import requests

INPUT_FILE = os.path.dirname(os.getcwd()) + "/API-DATA-RETRIVAL/daily_intake.csv"

age_gender = set()
nutrition = {
	'sugar' : 1,
	'iron' : 2,
	'calcium' : 3,
	'sodium' : 4,
	'protein' : 5,
	'cholesterol' : 6,
	'potassium' : 7,
	'lactose' : 8,
	'vitaminC' : 9,
	'saturated' : 10,
	'dietary_fiber' : 11,
	'calories_kcal' : 12,
	'alcohol' : 13
}

age_gender_queries = ""
# define sql queries
add_age_gender = """INSERT INTO RECOMMEND_BY_AGE_GENDER (is_female, age, nutrition_id, weight_mg) VALUES ({},{},{},{});"""

with open(INPUT_FILE, 'r') as fin:
    reader = csv.reader(fin, lineterminator='\n')
    for row in reader:
        if row[0] != 'male' and row[0] != 'female':
            continue
        gender = 1 if row[0] == 'female' else 0
        age = row[1]
        for nutrition_id in range(0,len(row[2:])):
	        if (gender, age, nutrition_id, row[2+nutrition_id]) not in age_gender:
	            # adding new food to set
	            age_gender.add((gender, age, nutrition_id+1, row[2+nutrition_id]))
	            age_gender_queries += add_age_gender.format(gender, age, nutrition_id+1, row[2+nutrition_id])

recipes_sql2 = open('insert_age_gender.sql', 'w')
recipes_sql2.write(age_gender_queries)