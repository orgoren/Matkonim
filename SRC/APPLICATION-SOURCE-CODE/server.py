#!/usr/bin/env python
import os
import sys
import datetime
import MySQLdb as mdb
from flask import Flask, render_template, redirect, url_for, request, make_response, session, g, abort, flash, jsonify
from gevent.pywsgi import WSGIServer
import queries
import re
import random
from utils import *
import json


# Create the application instance
app = Flask(__name__)


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
			return redirect('/daily_meal_plan')

		if request.form['submit'] == "rcps-by-alrgs":
			return redirect('/recipes_by_allergies')

		if request.form['submit'] == "nutrivia":
			return redirect('/nutrivia')


@app.route('/cocktails_by_nutritional', methods=['GET', 'POST'])
def cocktails_by_nutritional():
	if request.method == 'GET':
		return render_template('cocktails_by_nutritional.html')
	if request.method == 'POST':
		if "Back to Main Menu" == request.form['submit']:
			return redirect('/')
		if "Find me a cocktail!" == request.form['submit']:
			nutritions_values = get_nutritions_values(request.form, False)

			# Build query from our inputs
			q = queries.get_query2(nutritions_values)

			# Get query results from DB
			res = get_query_results(q, "Cocktail")
			return redirect(url_for('cocktails_by_nutritional_results', query_res=json.dumps(res)))


@app.route('/cocktails_by_nutritional_results', methods=['GET', 'POST'])
def cocktails_by_nutritional_results():
	query_res = request.args['query_res']
	if request.method == 'GET':
		return render_template('cocktails_by_nutritional_results.html', query_res=json.loads(query_res))
	if request.method == 'POST':
		if "Back to Main Menu" == request.form['submit']:
			return redirect('/')
		if "New search" == request.form['submit']:
			return redirect('/cocktails_by_nutritional')


@app.route('/daily_meal_plan', methods=['GET', 'POST'])
def daily_meal_plan():
	if request.method == 'GET':
		return render_template('daily_meal_plan.html')
	if request.method == 'POST':
		if "Back to Main Menu" == request.form['submit']:
			return redirect('/')
		if "Find me a meal plan!" == request.form['submit']:
			nutritions_values = get_nutritions_values(request.form)
			meal_option = get_meal_option(request.form, is_meal_plan=True)
			gender = get_gender(request.form)
			age = get_age(request.form)

			# Build query from our inputs
			q = queries.get_query3(nutritions_values, meal_option, age, gender)

			# Get query results from DB
			res = get_query_results(q, meal_option)
			return redirect(url_for('daily_meal_plan_results', query_res=json.dumps(res)))


@app.route('/daily_meal_plan_results', methods=['GET', 'POST'])
def daily_meal_plan_results():
	query_res = request.args['query_res']
	if request.method == 'GET':
		return render_template('daily_meal_plan_results.html', query_res=json.loads(query_res))
	if request.method == 'POST':
		if "Back to Main Menu" == request.form['submit']:
			return redirect('/')
		if "New search" == request.form['submit']:
			return redirect('/daily_meal_plan')


@app.route('/recipes_by_allergies', methods=['GET', 'POST'])
def recipes_by_allergies():
	if request.method == 'GET':
		return render_template('recipes_by_allergies.html')
	if request.method == 'POST':
		if "Back to Main Menu" == request.form['submit']:
			return redirect('/')
		if "Find me a recipe!" == request.form['submit']:
			allergans = []
			allergans.append(request.form["inlineFormAllergan1"])
			allergans.append(request.form["inlineFormAllergan2"])
			allergans.append(request.form["inlineFormAllergan3"])
			meal_or_drink_option = get_food_type_or_cocktail(request.form)

			# Build query from our inputs
			q = queries.get_query5(allergans, meal_or_drink_option)

			# Get query results from DB
			res = get_query_results(q, meal_or_drink_option)
			return redirect(url_for('recipes_by_allergies_results', query_res=json.dumps(res)))


@app.route('/recipes_by_allergies_results', methods=['GET', 'POST'])
def recipes_by_allergies_results():
	query_res = request.args['query_res']
	if request.method == 'GET':
		return render_template('recipes_by_allergies_results.html', query_res=json.loads(query_res))
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
			nutritions_values = get_nutritions_values(request.form)
			meal_option = get_meal_option(request.form)
			prep_time = get_prep_time(request.form)

			# Build query from our inputs
			q = queries.get_query1(nutritions_values, meal_option, prep_time)

			# Get query results from DB
			res = get_query_results(q, meal_option)
			return redirect(url_for('recipes_by_nutritional_results', query_res=json.dumps(res)))


@app.route('/recipes_by_nutritional_results', methods=['GET', 'POST'])
def recipes_by_nutritional_results():
	query_res = request.args['query_res']
	if request.method == 'GET':
		return render_template('recipes_by_nutritional_results.html', query_res=json.loads(query_res))
	if request.method == 'POST':
		if "Back to Main Menu" == request.form['submit']:
			return redirect('/')
		if "New search" == request.form['submit']:
			return redirect('/recipes_by_nutritional')


@app.route('/nutrivia', methods=['GET', 'POST'])
def nutrivia():
	if request.method == 'GET':
		return render_template('nutrivia.html')
	if request.method == 'POST':
		if "Back to Main Menu" == request.form['submit']:
			return redirect('/')


NEXT_QUESTION = 1  # TODO: remove after making real questions


@app.route('/getQuestion')
def getQuestion():
	question = get_random_question()

	try:
		return jsonify(question=question)
	except Exception as e:
		return str(e)


if __name__ == '__main__':
	http_server = WSGIServer(('0.0.0.0', VALID_RANDOM_PORT), app)
	print "server started"
	http_server.serve_forever()
