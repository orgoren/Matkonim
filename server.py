#!/usr/bin/env python
import os
import sys
# import MySQLdb as mdb
from flask import Flask, render_template, redirect, url_for, request, make_response, session, g, abort, flash
import datetime

# Create the application instance
app = Flask(__name__)
SERVER_NAME = ""
SERVER_PORT = 3306
DB_USERNAME = "DbMysql11"
DB_PASSWORD = "DbMysql11"  # Maybe don't need password  - ""
DB_NAME = "DbMysql11"
VALID_RANDOM_PORT = 44444


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
        	return redirect('/find_recipes_by_allergies')


@app.route('/cocktails_by_nutritional', methods=['GET', 'POST'])
def cocktails_by_nutritional():
    if request.method == 'GET':
        return render_template('cocktails_by_nutritional.html')
    if request.method == 'POST':
        if "Back to Main Menu" == request.form['submit']:
            return redirect('/')


@app.route('/cocktails_results', methods=['GET', 'POST'])
def cocktails_by_nutritional_results():
    if request.method == 'GET':
        return render_template('cocktails_by_nutritional_results.html')
    if request.method == 'POST':
        if "Back to Main Menu" == request.form['submit']:
            return redirect('/')


@app.route('/daily_meal', methods=['GET', 'POST'])
def daily_meal_plan():
    if request.method == 'GET':
        return render_template('daily_meal_plan.html')
    if request.method == 'POST':
        if "Back to Main Menu" == request.form['submit']:
            return redirect('/')


@app.route('/daily_meal_results', methods=['GET', 'POST'])
def daily_meal_plan_results():
    if request.method == 'GET':
        return render_template('daily_meal_plan_results.html')
    if request.method == 'POST':
        if "Back to Main Menu" == request.form['submit']:
            return redirect('/')


@app.route('/find_recipes_by_allergies', methods=['GET', 'POST'])
def recipes_by_allergies():
    if request.method == 'GET':
        return render_template('recipes_by_allergies.html')
    if request.method == 'POST':
        if "Back to Main Menu" == request.form['submit']:
            return redirect('/')
        if "Find me a recipe!" == request.form['find_recipe']:
            _inlineFormAllergan1 = request.form["inlineFormAllergan1"]
            _inlineFormAllergan2 = request.form["inlineFormAllergan2"]
            _inlineFormAllergan3 = request.form["inlineFormAllergan3"]
            return redirect('/recipes_results')


@app.route('/recipes_results', methods=['GET', 'POST'])
def allergies_results():
    if request.method == 'GET':
        return render_template('recipes_by_allergies_results.html')
    if request.method == 'POST':
        if "Back to Main Menu" == request.form['submit']:
            return redirect('/')


@app.route('/recipes_by_nutritional', methods=['GET', 'POST'])
def recipes_by_nutritional():
    if request.method == 'GET':
        return render_template('recipes_by_nutritional.html')
    if request.method == 'POST':
    	print request.form
        if "Back to Main Menu" == request.form['submit']:
            return redirect('/')


@app.route('/recipes_by_nutritional_results', methods=['GET', 'POST'])
def recipes_by_nutritional_results():
    if request.method == 'GET':
        return render_template('recipes_by_nutritional_results.html')
    if request.method == 'POST':
        if "Back to Main Menu" == request.form['submit']:
            return redirect('/')

# @app.route('/something_to_get/<param>', methods=['Get'])
# def get_something(param):
#     res = []
#     if request.method == 'GET':
#         try:
#             con = mdb.connect(host=SERVER_NAME, port=SERVER_PORT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME)
#             with con:
#                 cur = con.cursor(mdb.cursors.DictCursor)
#                 query1 = "Select * from Some_table where x = {}".format(param)
#                 cur.execute(query1)
#                 res = [item['something'] for item in cur.fetchall()]
#                 cur.close()
#                 cur = con.cursor(mdb.cursors.DictCursor)
#         except Exception as e:
#             return render_template('homepage.html', error=str(e))ba
#     return render_template('homepage.html', attribyte=res)


if __name__ == '__main__':
    app.run(port=8888, host="0.0.0.0", debug=True)
    # http_server = WSGIServer(('0.0.0.0', VALID_RANDOM_PORT), app)
    # http_server.serve_forever()
