import csv
import requests
import MySQLdb
from connectionDetails import *

INPUT_FILE = PATH_ROOT + "/API-DATA-RETRIVAL/cocktails.csv"


def get_foreign_key_from_table(query, value):
    # execute the SQL query using execute() method.
    cursor.execute(query, [value])
    # fetch all of the rows from the query
    data = cursor.fetchall()
    if data == ():  # not found
        return None
    else:
        return data[0][0]

cocktails = set()

# Open database connection
# db = MySQLdb.connect(host=SERVER_NAME, port=SERVER_PORT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME)

# prepare a cursor object using cursor() method
# cursor = db.cursor()

# to prevent encoding problems
# db.set_character_set('utf8')
# cursor.execute('SET NAMES utf8;')
# cursor.execute('SET CHARACTER SET utf8;')
# cursor.execute('SET character_set_connection=utf8;')


# define sql queries
add_cocktail = """INSERT INTO COCKTAIL_RECIPES (cocktail_id, is_alcoholic, cocktail_details)
                                    VALUES (%s,%s,%s)"""

get_recipe_id = "SELECT recipe_id from ALL_RECIPES WHERE recipe_id = %s"


with open(INPUT_FILE, 'r') as fin:
    reader = csv.reader(fin, lineterminator='\n')

    for row in reader:
        cocktail_id = row[1]
        cocktail_details = row[6]
        is_alcoholic = 1 if row[4] == 'Alcoholic' else 0
        if (cocktail_id, cocktail_details, is_alcoholic) in cocktails:
            continue
        else:
            # adding new cocktail to set
            cocktails.add((cocktail_id, cocktail_details, is_alcoholic))
            try:  # inserting the cocktail
                # cursor.execute(add_cocktail, (cocktail_id, is_alcoholic, cocktail_details))
                # db.commit()
                x=1
            except Exception as e:
                print("error")
                print(e)
                # db.rollback()
                break
print(cocktails)
# disconnect from server
# db.close()
