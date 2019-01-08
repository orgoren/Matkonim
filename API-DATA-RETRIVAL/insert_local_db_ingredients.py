import csv
from connectionInfo import *
import MySQLdb

INPUT_FILE = os.path.dirname(os.getcwd()) + "/API-DATA-RETRIVAL/ingredients.csv"

ingredients = set()
nutrition = set()

# define sql queries
add_ingredient = """INSERT INTO INGREDIENTS (ingredient_name, serving_quantity, serving_unit, serving_weight_grams) VALUES ('{}',{},'{}',{});"""

add_nutrition = """INSERT INTO INGREDIENTS_NUTRITION (ingredient_name, suger_mg, iron_mg , calcium_mg, sodium_mg, protein_mg, cholesterol_mg, potassium_mg, lactose_mg, vitamin_C_mg, staurated_fat_mg, trans_fat_mg, dietart_fiber_mg, calories_kcal, alcohol_mg, magnesium_mg, zinc_mg) VALUES ('{}',{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{});"""

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
        suger_mg = row[5]
        iron_mg = row[6]
        calcium_mg = row[7]
        sodium_mg = row[8]
        protein_mg = row[9]
        cholesterol_mg = row[10]
        potassium_mg = row[11]
        lactose_mg = row[12]
        vitamin_C_mg = row[13]
        staurated_fat_mg = row[14]
        trans_fat_mg = row[15]
        dietart_fiber_mg = row[16]
        calories_kcal = row[17]
        alcohol_mg = row[18]
        magnesium_mg = row[19]
        zinc_mg = row[20]

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

        if ((ingredient_name, suger_mg, iron_mg , calcium_mg, sodium_mg, protein_mg, cholesterol_mg, potassium_mg, lactose_mg, vitamin_C_mg, staurated_fat_mg, trans_fat_mg, dietart_fiber_mg, calories_kcal, alcohol_mg, magnesium_mg, zinc_mg)) in nutrition:
            continue
        else:
            nutrition.add((ingredient_name, suger_mg, iron_mg, calcium_mg, sodium_mg, protein_mg, cholesterol_mg, potassium_mg, lactose_mg, vitamin_C_mg, staurated_fat_mg, trans_fat_mg, dietart_fiber_mg, calories_kcal, alcohol_mg, magnesium_mg, zinc_mg))
	        try:
		        cursor.execute(add_nutrition.format(ingredient_name, suger_mg, iron_mg, calcium_mg, sodium_mg, protein_mg, cholesterol_mg, potassium_mg, lactose_mg, vitamin_C_mg, staurated_fat_mg, trans_fat_mg, dietart_fiber_mg, calories_kcal, alcohol_mg, magnesium_mg, zinc_mg))
		        db.commit()
		    except Exception as e:
		        print("error")
		        print(e)
		        db.rollback()
		        break

# disconnect from server
db.close()
