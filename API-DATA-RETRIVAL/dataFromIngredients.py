import csv
import requests
import os
import commonFile

def run():

    INPUT_FILE = os.path.dirname(os.getcwd()) + "/API-DATA-RETRIVAL/ingredients.csv"

    ingredients = set()
    nutrition = set()

    add_ingredient_queries = ""
    add_nutrition_queries = ""

    # define sql queries
    add_ingredient = """INSERT INTO INGREDIENTS (ingredient_id, ingredient_name, serving_quantity, serving_unit, serving_weight_grams) VALUES ({},'{}',{},'{}',{});"""

    add_nutrition = """INSERT INTO INGREDIENT_NUTRITION (ingredient_id, nutrition_id, weight_mg_from_ingredient) VALUES ({},{},{});"""

    with open(INPUT_FILE, 'r') as fin:
        reader = csv.reader(fin, lineterminator='\n')
        for row in reader:
            if row[1] == 'ingredient_name':
                continue
            ingredient_name = row[1].replace("'","''")
            serving_quantity = row[2]
            serving_unit = row[3].replace("'","''")
            serving_weight_grams = row[4]

            if (ingredient_name, serving_quantity, serving_unit, serving_weight_grams) in ingredients:
                continue
            else:
                # adding new ingredient to set
                ingredients.add((ingredient_name, serving_quantity, serving_unit, serving_weight_grams))
                add_ingredient_queries += add_ingredient.format(commonFile.ingredient_id, str(ingredient_name), serving_quantity, str(serving_unit), serving_weight_grams)

            offset = 5
            nutrition_id = 1
            for index in range(0, len(row[5:])):
                weight_mg_from_ingredient = row[offset + index]
                if (commonFile.ingredient_id, nutrition_id, weight_mg_from_ingredient) in nutrition:
                    continue
                else:
                    nutrition.add((commonFile.ingredient_id, nutrition_id, weight_mg_from_ingredient))
                    add_nutrition_queries += add_nutrition.format(commonFile.ingredient_id, nutrition_id, weight_mg_from_ingredient)
                    nutrition_id += 1
                    commonFile.ingredient_id += 1

    ingredients_sql = open('insert_ingredients_from_ingredients.sql', 'w')
    ingredients_sql.write(add_ingredient_queries)

    ingredients_nutrition_sql = open('insert_ingredients_nutrition.sql', 'w')
    ingredients_nutrition_sql.write(add_nutrition_queries)
