#!/usr/bin/env python
import os
import sys
import datetime
import MySQLdb as mdb
from flask import Flask, render_template, redirect, url_for, request, make_response, session, g, abort, flash
from gevent.pywsgi import WSGIServer
import sshtunnel
import getpass

# Create the application instance
app = Flask(__name__)
SERVER_NAME = ""
SERVER_PORT = 3306
DB_USERNAME = "DbMysql11"
DB_PASSWORD = "DbMysql11"
DB_NAME = "DbMysql11"
VALID_RANDOM_PORT = 40326
USERNAME = "orgoren1"
PASSWORD = ""
NUTRITIONS = [	"sugar",   "iron",     "calcium", "sodium", "protein", "cholesterol", "potassium",
        		"lactose", "vitaminC", "satfat",  "fiber",  "alcohol", "calories"]

VALUES = {"1" : "none", "": "dont care", "2" : "less than 5%", "3" : "over 30%"}

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template('homepage.html')

    elif request.method == 'POST':
        if request.form['submit'] == "rcps-by-ntrtnl":
            return redirect('/recipes_by_nutritional')

        if request.form['submit'] == "ccktl-by-ntrtnl":
            return redirect('/cocktails_by_nutritional')

        if request.form['submit'] == "dly-ml-pln":
            return redirect('/daily_meal')

        if request.form['submit'] == "rcps-by-alrgs":
            return redirect('/recipes_by_allergies')


@app.route('/cocktails_by_nutritional', methods=['GET', 'POST'])
def cocktails_by_nutritional():
    if request.method == 'GET':
        return render_template('cocktails_by_nutritional.html')
    if request.method == 'POST':
        if "Back to Main Menu" == request.form['submit']:
            return redirect('/')
        if "Find me a cocktail!" == request.form['submit']:
        	nutritions_values = {}
        	for nutrition_value in NUTRITIONS:
        		nutritions_values[nutrition_value] = request.form.get(nutrition_value + "-form")

        	print nutritions_values

        	deleta = """
        	_inlineFormSugar = request.form.get("sugar-form")
        	_inlineFormIron = request.form.get("iron-form")
        	_inlineFormCalcium = request.form.get("calcium-form")
        	_inlineFormSodium = request.form.get("sodium-form")
        	_inlineFormProtein = request.form.get("protein-form")
        	_inlineFormCholesterol = request.form.get("cholesterol-form")
        	_inlineFormPotassium = request.form.get("potassium-form")
        	_inlineFormLactose = request.form.get("lactose-form")
        	_inlineFormVitaminC = request.form.get("vitaminC-form")
        	_inlineFormSaturatedFat = request.form.get("satfat-form")
        	_inlineFormDietaryFiber = request.form.get("fiber-form")
        	_inlineFormAlcoholic = request.form.get("alcohol-form")
        	_inlineFormMaxCalories = request.form.get("calories-form")
        	"""
        	# TODO - get query values
        	return redirect('/cocktails_results')


@app.route('/cocktails_results', methods=['GET', 'POST'])
def cocktails_by_nutritional_results():
    if request.method == 'GET':
        return render_template('cocktails_by_nutritional_results.html')
    if request.method == 'POST':
        if "Back to Main Menu" == request.form['submit']:
            return redirect('/')
        if "New search" == request.form['submit']:
            return redirect('/cocktails_by_nutritional')


@app.route('/daily_meal', methods=['GET', 'POST'])
def daily_meal_plan():
    if request.method == 'GET':
        return render_template('daily_meal_plan.html')
    if request.method == 'POST':
        if "Back to Main Menu" == request.form['submit']:
            return redirect('/')
        if "Find me a meal plan!" == request.form['submit']:
        	nutritions_values = {}
        	for nutrition_value in NUTRITIONS:
        		nutritions_values[nutrition_value] = request.form.get(nutrition_value + "-form")

        	print nutritions_values

        	delete = """
        	_inlineFormSugar = request.form.get("sugar-form")
        	_inlineFormIron = request.form.get("iron-form")
        	_inlineFormCalcium = request.form.get("calcium-form")
        	_inlineFormSodium = request.form.get("sodium-form")
        	_inlineFormProtein = request.form.get("protein-form")
        	_inlineFormCholesterol = request.form.get("cholesterol-form")
        	_inlineFormPotassium = request.form.get("potassium-form")
        	_inlineFormLactose = request.form.get("lactose-form")
        	_inlineFormVitaminC = request.form.get("vitaminC-form")
        	_inlineFormSaturatedFat = request.form.get("satfat-form")
        	_inlineFormDietaryFiber = request.form.get("fiber-form")
        	_inlineFormMaxCalories = request.form.get("calories-form")
        	"""
        	# TODO - get query values
        	return redirect('/daily_meal_results')


@app.route('/daily_meal_results', methods=['GET', 'POST'])
def daily_meal_plan_results():
    if request.method == 'GET':
        return render_template('daily_meal_plan_results.html')
    if request.method == 'POST':
        if "Back to Main Menu" == request.form['submit']:
            return redirect('/')
        if "New search" == request.form['submit']:
            return redirect('/daily_meal')


@app.route('/recipes_by_allergies', methods=['GET', 'POST'])
def recipes_by_allergies():
    if request.method == 'GET':
        return render_template('recipes_by_allergies.html')
    if request.method == 'POST':
        if "Back to Main Menu" == request.form['submit']:
            return redirect('/')
        if "Find me a recipe!" == request.form['submit']:
            _inlineFormAllergan1 = request.form["inlineFormAllergan1"]
            _inlineFormAllergan2 = request.form["inlineFormAllergan2"]
            _inlineFormAllergan3 = request.form["inlineFormAllergan3"]
            # TODO - get query values and handle insufficient input case
            return redirect('/recipes_by_allergies_results')


@app.route('/recipes_by_allergies_results', methods=['GET', 'POST'])
def allergies_results():
    if request.method == 'GET':
        return render_template('recipes_by_allergies_results.html')
    if request.method == 'POST':
        if "Back to Main Menu" == request.form['submit']:
            return redirect('/')
        if "New search" == request.form['submit']:
            return redirect('/recipes_by_allergies')


@app.route('/recipes_by_nutritional', methods=['GET', 'POST'])
def recipes_by_nutritional():
    if request.method == 'GET':
        return render_template('recipes_by_nutritional.html')
    if request.method == 'POST':
        if "Back to Main Menu" == request.form['submit']:
            return redirect('/')
        if "Find me a recipe!" == request.form['submit']:
        	nutritions_values = {}
        	for nutrition_value in NUTRITIONS:
        		nutritions_values[nutrition_value] = request.form.get(nutrition_value + "-form")

        	print nutritions_values

        	delete = """
        	_inlineFormSugar = request.form.get("sugar-form")
        	_inlineFormIron = request.form.get("iron-form")
        	_inlineFormCalcium = request.form.get("calcium-form")
        	_inlineFormSodium = request.form.get("sodium-form")
        	_inlineFormProtein = request.form.get("protein-form")
        	_inlineFormCholesterol = request.form.get("cholesterol-form")
        	_inlineFormPotassium = request.form.get("potassium-form")
        	_inlineFormLactose = request.form.get("lactose-form")
        	_inlineFormVitaminC = request.form.get("vitaminC-form")
        	_inlineFormSaturatedFat = request.form.get("satfat-form")
        	_inlineFormTransFat = request.form.get("transfat-form")
        	_inlineFormDietaryFiber = request.form.get("fiber-form")
        	_inlineFormMaxCalories = request.form.get("calories-form")
        	_inlineFormMaxPrepTime = request.form.get("prep-form")
        	"""
        	# TODO - get query values
        	return redirect('/recipes_by_nutritional_results')


@app.route('/recipes_by_nutritional_results', methods=['GET', 'POST'])
def recipes_by_nutritional_results():
    if request.method == 'GET':
        return render_template('recipes_by_nutritional_results.html')
    if request.method == 'POST':
        if "Back to Main Menu" == request.form['submit']:
            return redirect('/')
        if "New search" == request.form['submit']:
            return redirect('/recipes_by_nutritional')

@app.route('/test', methods=['GET'])
def connect_to_db():#username='', password=''):
	with sshtunnel.SSHTunnelForwarder(
	        ('nova.cs.tau.ac.il', 22),
	        ssh_username=USERNAME,
	        ssh_password=PASSWORD,
	        remote_bind_address=("mysqlsrv1.cs.tau.ac.il", 3306),
	        local_bind_address=("127.0.0.1", 3307)
	) as tunnel:
	    con = mdb.connect(host='127.0.0.1',    # your host, usually localhost
	                         user=DB_USERNAME,         # your username
	                         passwd=DB_PASSWORD,  # your password
	                         db=DB_NAME,
	                         port = 3307)        # name of the data base
	    cur = con.cursor(mdb.cursors.DictCursor)
	    #query1 = "Select * from ALL_RECIPES where recipe_id = {}".format(1)
	    query1 = "select * from ALL_RECIPES"
	    cur.execute(query1)
	    print cur.fetchall()
	    #res = [item['recipe_name'] for item in cur.fetchall()]
	    cur.close()
	    return ','.join(res)

def get_username_and_password():
	global PASSWORD
	USERNAME = raw_input("enter username (for nova): ")
	PASSWORD = getpass.getpass("enter password (for nova): ")

if __name__ == '__main__':
    # app.run(port=8888, host="0.0.0.0", debug=True)
    http_server = WSGIServer(('0.0.0.0', VALID_RANDOM_PORT), app)
    get_username_and_password()
    http_server.serve_forever()
