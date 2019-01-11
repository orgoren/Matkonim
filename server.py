#!/usr/bin/env python
import os
import sys
import datetime
import MySQLdb as mdb
from flask import Flask, render_template, redirect, url_for, request, make_response, session, g, abort, flash, jsonify
from gevent.pywsgi import WSGIServer
import sshtunnel
import getpass
import queries
import re
from utils import *

# Create the application instance
app = Flask(__name__)
SERVER_NAME = ""
SERVER_PORT = 3306
DB_USERNAME = "DbMysql11"
DB_PASSWORD = "DbMysql11"
DB_NAME = "DbMysql11"
VALID_RANDOM_PORT = 40326
USERNAME = ""
PASSWORD = ""

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
			nutritions_values = get_nutritions_values(request.form)
				print nutritions_values
			nutritions_values = {}
	
			print nutritions_values

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
			nutritions_values = get_nutritions_values(request.form)
			print nutritions_values

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
			nutritions_values = get_nutritions_values(request.form)
			meal_option = get_meal_option(request.form)

			print "nutritions_values:"
			print nutritions_values
			print "meal_options:"
			print meal_options

			q = queries.get_query1(nutritions_values, meal_option)
			print q
			#ans = connect_to_db(q)
			#print "results:::"
			#print ans

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


@app.route('/nutrivia', methods=['GET', 'POST'])
def nutrivia():
	if request.method == 'GET':
		return render_template('nutrivia.html')
	if request.method == 'POST':
		if "Back to Main Menu" == request.form['submit']:
			return redirect('/')


NEXT_QUESTION = 1		# TODO: remove after making real questions


@app.route('/getQuestion')
def getQuestion():
	########### TODO: REMOVE FROM HERE after making real questions ###############
# format for questions to send to client:
# {'question': question itself, 'answer_a': ..., 'answer_b': ..., 'answer_c': ..., 'answer_d': ..., 'correct': right answer in format "answer_X"}
	question_1 = {'question': 'Some question that server came up with!','answer_a': 'answer_a_from_server', 'answer_b': 'answer_b_from_server',
		      'answer_c': 'answer_c_from_server', 'answer_d': 'answer_d_from_server', 'correct': 'answer_c'}
	question_2 = {'question': 'ANOTHER question that server came up with!', 'answer_a': 'ANOTHER_answer_a_from_server', 'answer_b': 'ANOTHER_answer_b_from_server',
		      'answer_c': 'ANOTHER_answer_c_from_server', 'answer_d': 'ANOTHER_answer_d_from_server', 'correct': 'answer_a'}
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

	
@app.route('/test', methods=['GET'])
def connect_to_db(query=""):#username='', password=''):
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
		#query = "Select * from ALL_RECIPES where recipe_id = {}".format(1)
		#query = "select * from NUTRITIONS"
		if query == "":
			res = {}
			print "ERROR: no query in input"
			return res

		cur.execute(query)
		ans = cur.fetchall()

		#res = [item['recipe_name'] for item in cur.fetchall()]
		cur.close()
		return ans
		#return ','.join(res)

#def get_username_and_password():
#	global PASSWORD
#	USERNAME = raw_input("enter username (for nova): ")
#	PASSWORD = getpass.getpass("enter password (for nova): ")

if __name__ == '__main__':
	# app.run(port=8888, host="0.0.0.0", debug=True)
	http_server = WSGIServer(('0.0.0.0', VALID_RANDOM_PORT), app)
	#global USERNAME
	#global PASSWORD
	USERNAME, PASSWORD = get_username_and_password()
	print "server started"
	http_server.serve_forever()
