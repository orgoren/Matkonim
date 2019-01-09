import os
import csv
import requests
import MySQLdb
import commonFile

PATH_ROOT = os.path.dirname(os.getcwd())

INPUT_FILE = PATH_ROOT + "/new_srcipts/recipes.csv"

food_set = set()
recipe_set = set()
ingredient_set = set()

commonFile.init()
add_ingredient_queries = ""
add_food_recipe_queries = ""
add_all_recipes_queries = ""

# define sql queries
add_food = """INSERT INTO FOOD_RECIPES (recipe_id, food_id, course, prep_time_in_minutes, food_details) VALUES ({},{},'{}',{},'{}');"""

add_recipce = """INSERT INTO ALL_RECIPES (recipe_id, recipe_name, picture) VALUES ({},'{}','{}');"""

add_ingredient = """INSERT INTO RECIPE2INGREDIENTS (recipe_id, ingredient_id, servings, full_ingredient_line) VALUES ({},{},{},'{}');"""

with open(INPUT_FILE, 'r') as fin:
    reader = csv.reader(fin, lineterminator='\n')
    for row in reader:
        if row[1] == 'food_id':
            continue
        food_id = row[1]
        food_name = row[2].replace("'","''")
        course = row[3]
        prep_time_minutes = row[4]
        picture = row[5]
        food_details = row[6].replace("'","''")

        if (food_id, course, prep_time_minutes, food_details) in food_set:
            continue
        else:
            # adding new food to set
            food_set.add((food_id, commonFile.recipe_id, course, prep_time_minutes, food_details))
            recipe_set.add((food_name, picture))
            add_food_recipe_queries += add_food.format(food_id, commonFile.recipe_id, course, prep_time_minutes, str(food_details))
            add_all_recipes_queries += add_recipce.format(commonFile.recipe_id, food_name, picture)
            commonFile.recipe_id += 1
        num_ingredients = (len(row) - 7)/3
        #recipe_id = get_foreign_key(get_recipe_id, food_name)
        for ingredient_index in range(0, num_ingredients):

            ingredient_name = row[7 + 3*ingredient_index].replace("'","''")
            servings = row[8 + 3*ingredient_index]
            full_ingredient_line = row[9 + 3*ingredient_index]

            if (ingredient_name, servings, full_ingredient_line) in ingredient_set:
                continue
            else:
                # adding new ingredient to set
                ingredient_set.add((commonFile.recipe_id, ingredient_name, servings, full_ingredient_line))
                add_ingredient_queries += add_ingredient.format(commonFile.recipe_id, commonFile.ingredient_id, servings, str(full_ingredient_line))
                commonFile.ingredient_id += 1


recipe_ingredient_sql = open('insert_recipe_ingredient_from_recipes.sql', 'w')
recipe_ingredient_sql.write(add_ingredient_queries)

food_recipe_sql = open('insert_food_recipe_from_recipes.sql', 'w')
food_recipe_sql.write(add_food_recipe_queries)

recipes_sql2 = open('insert_all_recipes_from_recipes.sql', 'w')
recipes_sql2.write(add_all_recipes_queries)