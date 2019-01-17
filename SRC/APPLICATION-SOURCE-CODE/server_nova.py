#!/usr/bin/env python
import os
import sys
import datetime
import MySQLdb as mdb
from flask import Flask, render_template, redirect, url_for, request, make_response, session, g, abort, flash, jsonify
from gevent.pywsgi import WSGIServer
import queries_nova
import re
from utils_nova import *
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
			# print q

			# Get query results from DB
			res = get_query_results(q, "Cocktail")
			# print(res)
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
			print "age=", age, "gender=", gender, "meal_options=", meal_option

			# Build query from our inputs
			q = queries.get_query3(nutritions_values, meal_option, age, gender)

			# For daily meal plan, we get a dictionary, otherwise a single query
			if type(q) == dict:
				res = {}
				for meal in q:
					query = q[meal]
					meal_option = FULL_DAY_MEALS[meal]["meal"]
					print query
					# Get query results from DB
					res[meal] = get_query_results(query, meal_option)
				print(res)
			else:
				print q
				# Get query results from DB
				res = get_query_results(q, meal_option)
				print(res)
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
			print(q)

			# Get query results from DB
			res = get_query_results(q, meal_or_drink_option)
			print(res)
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
			print "nutritions_values:"
			print nutritions_values
			print "meal_option:"
			print meal_option

			# Build query from our inputs
			q = queries.get_query1(nutritions_values, meal_option, prep_time)
			print q

			# Get query results from DB
			res = get_query_results(q, meal_option)
			print(res)
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
	########### TODO: REMOVE FROM HERE after making real questions ###############
	# format for questions to send to client:
	# {'question': question itself, 'answer_a': ..., 'answer_b': ..., 'answer_c': ..., 'answer_d': ..., 'correct': right answer in format "answer_X"}
	question_1 = {'question': 'Some question that server came up with!', 'answer_a': 'answer_a_from_server',
				  'answer_b': 'answer_b_from_server',
				  'answer_c': 'answer_c_from_server', 'answer_d': 'answer_d_from_server', 'correct': 'answer_c'}
	question_2 = {'question': 'ANOTHER question that server came up with!', 'answer_a': 'ANOTHER_answer_a_from_server',
				  'answer_b': 'ANOTHER_answer_b_from_server',
				  'answer_c': 'ANOTHER_answer_c_from_server', 'answer_d': 'ANOTHER_answer_d_from_server',
				  'correct': 'answer_a'}
	global NEXT_QUESTION
	if NEXT_QUESTION == 1:
		question = question_1
		NEXT_QUESTION = 2
	else:
		question = question_2
		NEXT_QUESTION = 1
	########### TODO: REMOVE UNTIL HERE after making real questions ###############

	try:
		return jsonify(question=question)
	except Exception as e:
		return str(e)


if __name__ == '__main__':
	http_server = WSGIServer(('0.0.0.0', VALID_RANDOM_PORT), app)
	print "server started"
	http_server.serve_forever()
