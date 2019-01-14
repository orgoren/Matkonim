import csv
from connectionDetails import *
import MySQLdb

INPUT_FILE = PATH_ROOT + "/API-DATA-RETRIVAL/recipes.csv"

food_set = set()
recipe_set = set()
ingredient_set = set()

# define sql queries
add_food = """INSERT INTO FOOD_RECIPES (recipe_id, food_id, course, prep_time_in_minutes, food_details) VALUES ({},{},'{}',{},'{}');"""

add_recipce = """INSERT INTO ALL_RECIPES (recipe_name, picture) VALUES ('{}','{}');"""

add_ingredient = """INSERT INTO RECIPE2INGREDIENTS (recipe_id, ingredient_id, servings, full_ingredient_line) VALUES ({},{},{},'{}');"""

# Open database connection
db = MySQLdb.connect(host=SERVER_NAME, port=SERVER_PORT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME)

# prepare a cursor object using cursor() method
cursor = db.cursor()

get_recipe_id = "Select recipe_id from ALL_RECIPES where recipe_name = %s"

get_ingredient_id = "Select ingredient_id from INGREDIENTS where ingredient_name = %s"

def get_foreign_key(query, value, one_value_flag=True):
    if one_value_flag:
        cursor.execute(query, [value])
    else:
        cursor.execute(query, value)
    data = cursor.fetchall()
    if data == ():
        return None
    return data[0][0]

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
            recipe_id = get_foreign_key(get_recipe_id, food_name)
            food_set.add((food_id, course, prep_time_minutes, food_details))
            recipe_set.add((recipe_id, food_name, picture))
            try:
                cursor.execute(add_food, (recipe_id, food_id, course, prep_time_minutes, str(food_details)))
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
        recipe_id = get_foreign_key(get_recipe_id, food_name)
        for ingredient_index in range(0, num_ingredients):

            ingredient_name = row[7 + 3*ingredient_index].replace("'","''")
            servings = row[8 + 3*ingredient_index]
            full_ingredient_line = row[9 + 3*ingredient_index]

            if (ingredient_name, servings, full_ingredient_line) in ingredient_set:
                continue
            else:
                # adding new ingredient to set
                ingredient_id = get_foreign_key(get_ingredient_id, ingredient_name)
                ingredient_set.add((ingredient_name, servings, full_ingredient_line))
                try:
                    cursor.execute(add_ingredient, (recipe_id, ingredient_id, servings, str(full_ingredient_line)))
                    db.commit()
                except Exception as e:
                    print("error")
                    print(e)
                    db.rollback()
                    break

# disconnect from server
db.close()