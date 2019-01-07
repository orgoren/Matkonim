import os
import MySQLdb as mdb
import requests

INPUT_FILES_FOLDER = os.path.dirname(os.getcwd()) + "/API-DATA-RETRIVAL/"

SERVER_NAME = ""
SERVER_PORT = 3306
DB_USERNAME = "DbMysql11"
DB_PASSWORD = "DbMysql11"
DB_NAME = "DbMysql11"

con = mdb.connect(host='127.0.0.1', user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME, port = SERVER_PORT)

cursor = con.cursor(mdb.cursors.DictCursor)

sql_query = open(INPUT_FILES_FOLDER + "insert_ingredients.sql")
cursor.execute(sql_query)

sql_query = open(INPUT_FILES_FOLDER + "insert_ingredients_nutrition.sql")
cursor.execute(sql_query)

sql_query = open(INPUT_FILES_FOLDER + "insert_age_gender.sql")
cursor.execute(sql_query)

sql_query = open(INPUT_FILES_FOLDER + "insert_all_recipes.sql")
cursor.execute(sql_query)

sql_query = open(INPUT_FILES_FOLDER + "insert_all_recipes2.sql")
cursor.execute(sql_query)

sql_query = open(INPUT_FILES_FOLDER + "insert_food_recipe.sql")
cursor.execute(sql_query)

sql_query = open(INPUT_FILES_FOLDER + "insert_cocktail_recipes.sql")
cursor.execute(sql_query)

sql_query = open(INPUT_FILES_FOLDER + "insert_recipe_ingredient.sql")
cursor.execute(sql_query)

sql_query = open(INPUT_FILES_FOLDER + "insert_recipe2ingredients.sql")
cursor.execute(sql_query)

cursor.close()
