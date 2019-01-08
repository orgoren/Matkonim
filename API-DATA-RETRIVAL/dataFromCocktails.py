import csv
import requests
import os

INPUT_FILE = os.path.dirname(os.getcwd()) + "/API-DATA-RETRIVAL/cocktails.csv"

cocktails = set()
recipes = set()
ingredients = set()

add_cocktail_queries = ""
add_recipce_queries = ""
add_ingredient_queries = ""

ingredient_id = 0
count_cocktails = 0
# define sql queries
add_cocktail = "INSERT INTO COCKTAIL_RECIPES (cocktail_id, is_alcoholic, cocktail_details) VALUES ({},{},'{}');"

add_recipce = """INSERT INTO ALL_RECIPES (recipe_name, picture) VALUES ('{}','{}');"""

add_ingredient = """INSERT INTO RECIPE2INGREDIENTS (ingredient_id, ingredient_name, servings, full_ingredient_line) VALUES ({},'{}',{},'{}');"""


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
            if count_cocktails > 0 and cocktail_id != 17233 and 'Willie' not in str(cocktail_details):
                cocktails.add((cocktail_id, cocktail_details, is_alcoholic))
                add_cocktail_queries += add_cocktail.format(cocktail_id, is_alcoholic, str(cocktail_details))
                add_recipce_queries += add_recipce.format(str(cocktail_name), str(picture))
            count_cocktails += 1

        num_ingredients = (len(row) - 7)/4
        for ingredient_index in range(0, num_ingredients):

            ingredient_name = str(row[7 + 3*ingredient_index]).replace("'","''")
            servings = row[8 + 3*ingredient_index]
            full_ingredient_line = str(row[9 + 3*ingredient_index]).replace("'","''")

            if (ingredient_name, servings, full_ingredient_line) not in ingredients:
                ingredient_id += 1
                add_ingredient_queries += add_ingredient.format(int(ingredient_id), str(ingredient_name), servings, str(full_ingredient_line))
                ingredients.add((ingredient_name, servings, full_ingredient_line))


cocktail_sql = open('insert_to_cocktail_recipes_from_cocktails.sql', 'w')
cocktail_sql.write(add_cocktail_queries)

recipes_sql = open('insert_all_recipes_from_cocktails.sql', 'w')
recipes_sql.write(add_recipce_queries)

ingredients_sql = open('insert_recipe2ingredients_from_cocktails.sql', 'w')
ingredients_sql.write(add_ingredient_queries)

