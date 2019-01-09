import csv
import requests
import os
import commonFile

def run():
    PATH_ROOT = os.path.dirname(os.getcwd())

    INPUT_FILE = PATH_ROOT + "/Save/cocktails.csv"


    cocktails = set()
    recipes = set()
    ingredients = set()

    add_cocktail_queries = ""
    add_recipce_queries = ""
    add_ingredient_queries = ""

    count_cocktails = 0
    # define sql queries
    add_cocktail = "INSERT INTO COCKTAIL_RECIPES (recipe_id, cocktail_id, is_alcoholic, cocktail_details) VALUES ({},{},{},'{}');"

    add_recipce = """INSERT INTO ALL_RECIPES (recipe_id, recipe_name, picture) VALUES ({}, '{}','{}');"""

    add_ingredient = """INSERT INTO RECIPE2INGREDIENTS (recipe_id, ingredient_id, servings, full_ingredient_line) VALUES ({},{},{},'{}');"""


    with open(INPUT_FILE, 'r') as fin:
        reader = csv.reader(fin, lineterminator='\n')
        for row in reader:
            if row[1] == 'cocktail_id':
                continue
            cocktail_id = row[1]
            cocktail_name = row[2].replace("'","''")
            is_alcoholic = 1 if row[3] == 'Alcoholic' else 0
            serving_glass = row[4]  # what to do with this
            picture = row[5].replace("'","''")
            cocktail_details = row[6].replace("'","''")

            if ((cocktail_id, cocktail_details, is_alcoholic) in cocktails) or (cocktail_id == 17233):
                continue
            else:
                # adding new cocktail to set
                if count_cocktails > 0:
                    cocktails.add((commonFile.recipe_id, cocktail_id, cocktail_details, is_alcoholic))
                    add_cocktail_queries += add_cocktail.format(commonFile.recipe_id, cocktail_id, is_alcoholic, str(cocktail_details))
                    add_recipce_queries += add_recipce.format(commonFile.recipe_id, str(cocktail_name), str(picture))
                count_cocktails += 1

            num_ingredients = (len(row) - 7)/4
            for ingredient_index in range(0, num_ingredients):

                ingredient_name = str(row[7 + 3*ingredient_index]).replace("'","''")
                servings = row[8 + 3*ingredient_index]
                full_ingredient_line = str(row[9 + 3*ingredient_index]).replace("'","''")

                if (commonFile.ingredient_id, servings, full_ingredient_line) not in ingredients:
                    add_ingredient_queries += add_ingredient.format(commonFile.recipe_id, commonFile.ingredient_id, servings, str(full_ingredient_line))
                    ingredients.add((commonFile.ingredient_id, servings, full_ingredient_line))
                    commonFile.ingredient_id += 1
            if count_cocktails > 1:
                commonFile.recipe_id += 1

    cocktail_sql = open('insert_to_cocktail_recipes_from_cocktails.sql', 'w')
    cocktail_sql.write(add_cocktail_queries)

    recipes_sql = open('insert_all_recipes_from_cocktails.sql', 'w')
    recipes_sql.write(add_recipce_queries)

    ingredients_sql = open('insert_recipe2ingredients_from_cocktails.sql', 'w')
    ingredients_sql.write(add_ingredient_queries)

