import os
import csv
import requests
import MySQLdb

INPUT_FILE = os.path.dirname(os.getcwd()) + "/API-DATA-RETRIVAL/recipes.csv"

food_set = set()
recipe_set = set()
ingredient_set = set()
recipe_id = 1
ingredient_id = 1

ingredient_num = 1
add_ingredient_queries = ""
add_food_recipe_queries = ""
add_all_recipes_queries = ""

# define sql queries
add_food = """INSERT INTO FOOD_RECIPES (food_id, course, prep_time_in_minutes, food_details) VALUES ({},'{}',{},'{}');"""

add_recipce = """INSERT INTO ALL_RECIPES (recipe_name, picture) VALUES ('{}','{}');"""

add_ingredient = """INSERT INTO RECIPE2INGREDIENTS (ingredient_id, ingredient_name, servings, full_ingredient_line) VALUES ({},'{}',{},'{}');"""

with open(INPUT_FILE, 'r') as fin:
    reader = csv.reader(fin, lineterminator='\n')
    file_number = 1
    row_counter = 1
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
            food_set.add((food_id, course, recipe_id, prep_time_minutes, food_details))
            recipe_set.add((food_name, picture))
            add_food_recipe_queries += add_food.format(food_id, course, prep_time_minutes, str(food_details))
            add_all_recipes_queries += add_recipce.format(food_name, picture)
        num_ingredients = (len(row) - 7)/3
        for ingredient_index in range(0, num_ingredients):

            ingredient_name = row[7 + 3*ingredient_index].replace("'","''")
            servings = row[8 + 3*ingredient_index]
            full_ingredient_line = row[9 + 3*ingredient_index]

            if (ingredient_name, servings, full_ingredient_line) in ingredient_set:
                continue
            else:
                # adding new ingredient to set
                ingredient_set.add((ingredient_name, servings, full_ingredient_line))
                add_ingredient_queries += add_ingredient.format(ingredient_num, str(ingredient_name), servings, str(full_ingredient_line))
                ingredient_num += 1

            if row_counter % 1000 == 0:
                recipe_ingredient_sql = open('insert_recipe_ingredient_from_recipes{}.sql'.format(file_number), 'w')
                recipe_ingredient_sql.write(add_ingredient_queries)

                food_recipe_sql = open('insert_food_recipe_from_recipes{}.sql'.format(file_number), 'w')
                food_recipe_sql.write(add_food_recipe_queries)

                recipes_sql2 = open('insert_all_recipes_from_recipes{}.sql'.format(file_number), 'w')
                recipes_sql2.write(add_all_recipes_queries)
                file_number += 1
                add_ingredient_queries = ""
                add_nutrition_queries = ""
            row_counter += 1

recipe_ingredient_sql = open('insert_recipe_ingredient_from_recipes{}.sql'.format(file_number), 'w')
recipe_ingredient_sql.write(add_ingredient_queries)

food_recipe_sql = open('insert_food_recipe_from_recipes{}.sql'.format(file_number), 'w')
food_recipe_sql.write(add_food_recipe_queries)

recipes_sql2 = open('insert_all_recipes_from_recipes{}.sql'.format(file_number), 'w')
recipes_sql2.write(add_all_recipes_queries)