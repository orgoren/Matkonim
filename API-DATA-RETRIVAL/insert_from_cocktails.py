import csv
from connectionDetails import *
import MySQLdb

INPUT_FILE = PATH_ROOT + "/API-DATA-RETRIVAL/cocktails.csv"

cocktails = set()
recipes = set()
ingredients = set()

ingredient_id = 0
count_cocktails = 0
# define sql queries
add_cocktail = "INSERT INTO COCKTAIL_RECIPES (recipe_id, cocktail_id, is_alcoholic, cocktail_details, serving_glass) VALUES ({},{},{},'{}','{}');"

add_recipce = """INSERT INTO ALL_RECIPES (recipe_name, picture) VALUES ('{}','{}');"""

add_ingredient = """INSERT INTO RECIPE2INGREDIENTS (recipe_id, ingredient_id, servings, full_ingredient_line) VALUES ({},{},{},'{}');"""

# Open database connection
db = MySQLdb.connect(host=SERVER_NAME, port=SERVER_PORT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME)

# prepare a cursor object using cursor() method
cursor = db.cursor()

def get_foreign_key(query, value, one_value_flag=True):
    if one_value_flag:
        cursor.execute(query, [value])
    else:
        cursor.execute(query, value)
    data = cursor.fetchall()
    if data == ():
        return None
    return data[0][0]

get_recipe_id = "Select recipe_id from ALL_RECIPES where recipe_name = %s"

get_ingredient_id = "Select ingredient_id from INGREDIENTS where ingredient_name = %s"

with open(INPUT_FILE, 'r') as fin:
    reader = csv.reader(fin, lineterminator='\n')
    for row in reader:
        if row[1] == 'cocktail_id':
            continue
        cocktail_id = row[1]
        cocktail_name = row[2].replace("'","''")
        is_alcoholic = 1 if row[3] == 'Alcoholic' else 0
        serving_glass = row[4].replace("'","''")
        picture = row[5].replace("'","''")
        cocktail_details = row[6].replace("'","''")

        if ((cocktail_id, cocktail_details, is_alcoholic, serving_glass) in cocktails) or (cocktail_id == 17233):
            continue
        else:
            # adding new cocktail to set
            if count_cocktails > 0 and cocktail_id != 17233 and 'Willie' not in str(cocktail_details):
                cocktails.add((cocktail_id, cocktail_details, is_alcoholic, serving_glass))
                recipe_id = get_foreign_key(get_recipe_id, str(cocktail_name))
                try:
                    cursor.execute(add_cocktail, (recipe_id, cocktail_id, is_alcoholic, str(cocktail_details), str(serving_glass)))
                    db.commit()
                except Exception as e:
                    print("error")
                    print(e)
                    db.rollback()
                    break
                try:
                    cursor.execute(add_recipce, (str(cocktail_name), str(picture)))
                    db.commit()
                except Exception as e:
                    print("error")
                    print(e)
                    db.rollback()
                    break
            count_cocktails += 1

        num_ingredients = (len(row) - 7)/4
        recipe_id = get_foreign_key(get_recipe_id, cocktail_name)
        for ingredient_index in range(0, num_ingredients):

            ingredient_name = str(row[7 + 3*ingredient_index]).replace("'","''")
            servings = row[8 + 3*ingredient_index]
            full_ingredient_line = str(row[9 + 3*ingredient_index]).replace("'","''")

            if (ingredient_name, servings, full_ingredient_line) not in ingredients:
                ingredient_id = get_foreign_key(get_ingredient_id, ingredient_name)
                try:
                    cursor.execute(add_ingredient, (recipe_id, int(ingredient_id), servings, str(full_ingredient_line)))
                    db.commit()
                except Exception as e:
                    print("error")
                    print(e)
                    db.rollback()
                    break
                ingredients.add((ingredient_name, servings, full_ingredient_line))

# disconnect from server
db.close()