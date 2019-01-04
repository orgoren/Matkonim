import csv
import requests
import os

INPUT_FILE = os.path.dirname(os.getcwd()) + "/API-DATA-RETRIVAL/ingredients.csv"

ingredients = set()
nutrition = set()

add_ingredient_queries = ""
add_nutrition_queries = ""

ingredient_id = 0
# define sql queries
add_ingredient = "INSERT INTO INGREDIENTS (ingredient_name, serving_quantity, serving_unit, serving_weight) VALUES ('{}',{},'{}',{});"

add_nutrition = """INSERT INTO INGREDIENTS_NUTRITION (ingredient_name, suger_mg, iron_mg , calcium_mg, sodium_mg, protein_mg, cholesterol_mg, potassium_mg, lactose_mg, vitamin_C_mg, staurated_fat_mg, trans_fat_mg, dietart_fiber_mg, calories_kcal, alcohol_mg, magnesium_mg, zinc_mg) VALUES ('{}',{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{});"""



with open(INPUT_FILE, 'r') as fin:
    reader = csv.reader(fin, lineterminator='\n')

    for row in reader:
        if row[1] == 'ingredient_name':
            continue
        ingredient_name = row[1].replace("'","''")
        serving_quantity = row[2]
        serving_unit = row[3].replace("'","''")
        serving_weight = row[4]
        suger_mg = row[5]
        iron_mg = row[6]
        calcium_mg = row[7]
        sodium_mg = row[8]
        protein_mg = row[9]
        cholesterol_mg = row[10]
        potassium_mg = row[11]
        lactose_mg = row[12]
        vitamin_C_mg = row[13]
        staurated_fat_mg = row[14]
        trans_fat_mg = row[15]
        dietart_fiber_mg = row[16]
        calories_kcal = row[17]
        alcohol_mg = row[18]
        magnesium_mg = row[19]
        zinc_mg = row[20]

        if (ingredient_name, serving_quantity, serving_unit, serving_weight) in ingredients:
            continue
        else:
            # adding new ingredient to set
            ingredients.add((ingredient_name, serving_quantity, serving_unit, serving_weight))
            add_ingredient_queries += add_ingredient.format(str(ingredient_name), serving_quantity, str(serving_unit), serving_weight)

        if ((ingredient_name, suger_mg, iron_mg , calcium_mg, sodium_mg, protein_mg, cholesterol_mg, potassium_mg, lactose_mg, vitamin_C_mg, staurated_fat_mg, trans_fat_mg, dietart_fiber_mg, calories_kcal, alcohol_mg, magnesium_mg, zinc_mg)) in nutrition:
            continue
        else:
            nutrition.add((ingredient_name, suger_mg, iron_mg, calcium_mg, sodium_mg, protein_mg, cholesterol_mg, potassium_mg, lactose_mg, vitamin_C_mg, staurated_fat_mg, trans_fat_mg, dietart_fiber_mg, calories_kcal, alcohol_mg, magnesium_mg, zinc_mg))
            add_nutrition_queries += add_nutrition.format(ingredient_name, suger_mg, iron_mg, calcium_mg, sodium_mg, protein_mg, cholesterol_mg, potassium_mg, lactose_mg, vitamin_C_mg, staurated_fat_mg, trans_fat_mg, dietart_fiber_mg, calories_kcal, alcohol_mg, magnesium_mg, zinc_mg)

ingredients_sql = open('insert_ingredients.sql', 'w')
ingredients_sql.write(add_ingredient_queries)

ingredients_nutrition_sql = open('insert_ingredients_nutrition.sql', 'w')
ingredients_nutrition_sql.write(add_nutrition_queries)
