import csv
from connectionInfo import *
import MySQLdb

INPUT_FILE = PATH_ROOT + "/API-DATA-RETRIVAL/recipes.csv"

food_set = set()
recipe_set = set()
ingredient_set = set()
ingredient_id = 1

# define sql queries
add_food = """INSERT INTO FOOD_RECIPES (food_id, course, prep_time_in_minutes, food_details) VALUES ({},'{}',{},'{}');"""

add_recipce = """INSERT INTO ALL_RECIPES (recipe_name, picture) VALUES ('{}','{}');"""

add_ingredient = """INSERT INTO RECIPE2INGREDIENTS (ingredient_id, ingredient_name, servings, full_ingredient_line) VALUES ({},'{}',{},'{}');"""

# Open database connection
db = MySQLdb.connect(host=SERVER_NAME, port=SERVER_PORT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME)

# prepare a cursor object using cursor() method
cursor = db.cursor()


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
            food_set.add((food_id, course, prep_time_minutes, food_details))
            recipe_set.add((food_name, picture))
            try:
                cursor.execute(add_food, (food_id, course, prep_time_minutes, str(food_details)))
                db.commit()
            except Exception as e:
                print("error")
                print(e)
                db.rollback()
                break;
            try:
                cursor.execute(add_recipce, (food_name, picture))
                db.commit()
            except Exception as e:
                print("error")
                print(e)
                db.rollback()
                break

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
                try:
                    cursor.execute(add_ingredient, (ingredient_id, str(ingredient_name), servings, str(full_ingredient_line)))
                    db.commit()
                except Exception as e:
                    print("error")
                    print(e)
                    db.rollback()
                    break
                ingredient_id += 1

# disconnect from server
db.close()