import csv
from connectionInfo import *
import MySQLdb

INPUT_FILE = os.path.dirname(os.getcwd()) + "/API-DATA-RETRIVAL/ingredients.csv"

ingredients = set()
nutrition = set()

# define sql queries
add_ingredient = """INSERT INTO INGREDIENTS (ingredient_name, serving_quantity, serving_unit, serving_weight_grams) VALUES ('{}',{},'{}',{});"""

add_nutrition = """INSERT INTO INGREDIENT_NUTRITION (ingredient_id, nutrition_id, weight_mg_from_ingredient) VALUES ({},{},{});"""

# Open database connection
db = MySQLdb.connect(host=SERVER_NAME, port=SERVER_PORT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME)

# prepare a cursor object using cursor() method
cursor = db.cursor()

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
        if row[1] == 'ingredient_name':
            continue
        ingredient_name = row[1].replace("'","''")
        serving_quantity = row[2]
        serving_unit = row[3].replace("'","''")
        serving_weight_grams = row[4]

        ingredient_id = get_foreign_key(get_ingredient_id, ingredient_name)
        if (ingredient_name, serving_quantity, serving_unit, serving_weight_grams) in ingredients:
            continue
        else:
            # adding new ingredient to set
            ingredients.add((ingredient_name, serving_quantity, serving_unit, serving_weight_grams))
            try:
                cursor.execute(add_ingredient, (str(ingredient_name), serving_quantity, str(serving_unit), serving_weight_grams))
                db.commit()
            except Exception as e:
                print("error")
                print(e)
                db.rollback()
                break
        offset = 5
        for index in range(0, len(row[5:])):
            weight_mg_from_ingredient = row[offset + index]

            if (ingredient_id, nutrition_id, weight_mg_from_ingredient) in nutrition:
                continue
            else:
                nutrition.add(ingredient_id, nutrition_id, weight_mg_from_ingredient)
    	        try:
    		        cursor.execute(add_nutrition, (ingredient_id, nutrition_id, weight_mg_from_ingredient))
    		        db.commit()
    		    except Exception as e:
    		        print("error")
    		        print(e)
    		        db.rollback()
    		        break

# disconnect from server
db.close()
