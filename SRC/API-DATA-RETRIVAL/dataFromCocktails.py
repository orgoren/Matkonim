import csv
import requests
import os
import commonFile

def run():
    PATH_ROOT = os.path.dirname(os.getcwd())

    INPUT_FILE = PATH_ROOT + "/API-DATA-RETRIVAL/cocktails.csv"


    cocktails = set()
    recipes = set()
    ingredients = set()

    add_cocktail_queries = ""
    add_recipce_queries = ""
    add_ingredient_queries = ""

    count_cocktails = 0
    # define sql queries
    add_cocktail = "INSERT INTO COCKTAIL_RECIPES (recipe_id, cocktail_id, is_alcoholic, cocktail_details, serving_glass) VALUES ({},{},{},'{}','{}');"

    add_recipce = """INSERT INTO ALL_RECIPES (recipe_name, picture) VALUES ('{}','{}');"""

    add_ingredient = """INSERT INTO RECIPE2INGREDIENTS (recipe_id, ingredient_id, servings, full_ingredient_line) VALUES ({},{},{},'{}');"""


    with open(INPUT_FILE, 'r') as fin:
        reader = csv.reader(fin, lineterminator='\n')
        for row in reader:
            if row[1] == 'cocktail_id':
                continue
            cocktail_id = row[1]
            cocktail_name = row[2].replace("'","''")
            is_alcoholic = 0 if (row[3] == 'Non alcoholic' or row[3] == 'Non Alcoholic') else 1
            serving_glass = row[4]
            picture = row[5].replace("'","''")
            cocktail_details = row[6].replace("'","''")

            if ((commonFile.recipe_id, cocktail_id, cocktail_details, is_alcoholic) in cocktails):
                continue
            else:
                # adding new cocktail to set
                cocktails.add((commonFile.recipe_id, cocktail_id, cocktail_details, is_alcoholic))
                add_cocktail_queries += add_cocktail.format(commonFile.recipe_id, cocktail_id, is_alcoholic, str(cocktail_details), serving_glass)
                add_recipce_queries += add_recipce.format(str(cocktail_name), str(picture))

            num_ingredients = (len(row) - 7)/4
            for ingredient_index in range(0, num_ingredients):

                ingredient_name = str(row[7 + 3*ingredient_index]).replace("'","''")
                servings = row[8 + 3*ingredient_index]
                full_ingredient_line = str(row[9 + 3*ingredient_index]).replace("'","''")
                if servings is None or full_ingredient_line is None or full_ingredient_line == '':
                    break
                if str(ingredient_name) in commonFile.ingredients_dict and (commonFile.recipe_id, commonFile.ingredients_dict[str(ingredient_name)], servings, str(full_ingredient_line)) in ingredients:
                    continue
                if str(ingredient_name) not in commonFile.ingredients_dict:
                    commonFile.ingredients_dict.update({str(ingredient_name): commonFile.ingredient_id})
                    commonFile.ingredient_id += 1
                add_ingredient_queries += add_ingredient.format(commonFile.recipe_id, commonFile.ingredients_dict[str(ingredient_name)], servings, str(full_ingredient_line))
                ingredients.add((commonFile.recipe_id, commonFile.ingredients_dict[str(ingredient_name)], servings, full_ingredient_line))
            commonFile.recipe_id += 1
                    

    cocktail_sql_file = open('insert_data_from_cocktail_csv.sql', 'w')
    cocktail_sql_file.write(add_recipce_queries+add_ingredient_queries+add_cocktail_queries)

