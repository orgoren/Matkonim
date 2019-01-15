#!/usr/bin/env python
import os
import sys
import datetime
import MySQLdb as mdb
from flask import Flask, render_template, redirect, url_for, request, make_response, session, g, abort, flash
from gevent.pywsgi import WSGIServer
import sshtunnel
import getpass
import queries
import re
import random

SERVER_NAME = ""
SERVER_PORT = 3306
DB_USERNAME = "DbMysql11"
DB_PASSWORD = "DbMysql11"
DB_NAME = "DbMysql11"
VALID_RANDOM_PORT = 40326
USERNAME = ""
PASSWORD = ""

BREAKFAST_PRECANTAGE = 0.3
LUNCH_PRECENTAGE = 0.4
DINNER_PRECENTAGE = 0.3

NUTRITIONS = [	"sugar",   "iron",     "calcium", "sodium", "protein", "cholesterol", "potassium",
				"lactose", "vitaminC", "saturated",  "dietary_fiber",  "alcohol", "calories"]

MEAL_OPTIONS = ["Main Dishes", "Side Dishes", "Appetizers", "Lunch", "Breakfast and Brunch", 
				"Snacks", "Soups", "Salads", "Breads", "Condiments and Sauce", "Desserts", "Full Day"]

VALUES = {"None" : "None", "1" : "None", "d": "dont care", "2" : "less than 5%", "3" : "over 30%"}

AGE_RANGES = {"14_18" : "0", "19_30" : "1", "31_40" : "2", "41_50" : "3", "51_60" : "4", "61_70" : "5", "71" : "6"}

PREP_TIMES = {"d" : "dont care", "1" : "30", "2" : "45", "3" : "60", "4" : "90", "5" : "120", "6" : "180"}

GENDERS = ["female", "male"]

FULL_DAY_MEALS = {	"breakfast" : {"meal" : "Breakfast and Brunch", "precentage" : BREAKFAST_PRECANTAGE}, 
					"lunch"     : {"meal" : "Lunch",                "precentage" : LUNCH_PRECENTAGE}, 
					"dinner"    : {"meal" : "Main Dishes",          "precentage" : DINNER_PRECENTAGE}}

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
			print "ERROR: no query in input"
			cur.close()
			return None

		try:
			cur.execute(query)
			ans = cur.fetchall()
		except Exception as e:
			print "ERROR: couldn't execute and fetch from db:", e
			cur.close()
			return None

		#res = [item['recipe_name'] for item in cur.fetchall()]
		cur.close()
		return ans
		#return ','.join(res)


def get_username_and_password():
	global USERNAME
	global PASSWORD
	USERNAME = raw_input("enter username (for nova): ")
	PASSWORD = getpass.getpass("enter password (for nova): ")


def get_nutritions_values(form, is_food=True):
	nutritions_values = {}

	for nutrition in NUTRITIONS:
		if is_food and nutrition == "alcohol":
			continue

		nutritions_values[nutrition] = str(form.get(nutrition))
		if nutritions_values[nutrition] == "":
			nutritions_values[nutrition] = "d"
		if nutrition == "calories" and nutritions_values[nutrition] == "None":
			nutritions_values[nutrition] = "d"
	return nutritions_values


def get_meal_option(form):	
	for mo in MEAL_OPTIONS:
		if str(form.get(mo)) == "on":
			return mo
	# looks like it's chosen
	return "Main Dishes"

def get_gender(form):
	for gender in GENDERS:
		if str(form.get(gender)) == "on":
			return gender
	return "female"

def get_prep_time(form):
	b = str(form.get("prep"))
	if b == "":
		b = "d"
	return PREP_TIMES[b]

def get_age(form):
	for age in AGE_RANGES:
		if str(form.get(age)) == "on":
			return AGE_RANGES[age]
	return AGE_RANGES["14_18"]

def get_food_type_or_cocktail(form):
	if str(form.get("option_cocktail")) == "on":
		return "Cocktail"

	if str(form.get("option_food")) == "on":
		return get_meal_option(form)

	rand_num = random.randint(0,1)
	if rand_num == 0:
		return "Cocktail"
	else:
		return random.choice(MEAL_OPTIONS)

def get_query_results(query, option):
	nutritions = {}
	ingredients = []
	ans = connect_to_db(query)
	if ans is None or len(ans) == 0:
		print("No result from query!")
		return None
	recipe_id = ans[0]["recipe_id"]
	ingredients_query = re.sub("<RECIPE_ID>", str(recipe_id), queries.get_ingredients_query, re.MULTILINE)
	nutritions_query = re.sub("<RECIPE_ID>", str(recipe_id), queries.get_nutritionals_query, re.MULTILINE)
	ingredients_ans = connect_to_db(ingredients_query)
	nutritions_ans = connect_to_db(nutritions_query)
	for line in ingredients_ans:
		found_ingredient = 0
		for ing in ingredients:
			if ing == line["ingredient_name"]:
				found_ingredient = 1
				break
		if found_ingredient == 0:
			ingredients.append(line["ingredient_name"])
	for line in nutritions_ans:
		found_nutrition = 0
		for nut, val in nutritions.iteritems():
			if nut == line["nutrition_name"]:
				found_nutrition = 1;
				break
		if found_nutrition == 0:
			nutritions[line["nutrition_name"]] = line["weight"]

	if option == "Cocktail":
		details_query = re.sub("<RECIPE_ID>", str(recipe_id), queries.get_cocktail_details_query, re.MULTILINE)
		details_ans = connect_to_db(details_query)

		return (details_ans[0]["recipe_name"], details_ans[0]["is_alcoholic"], details_ans[0]["serving_glass"],
				details_ans[0]["picture"], details_ans[0]["cocktail_details"], ingredients, nutritions)

	else:
		details_query = re.sub("<RECIPE_ID>", str(recipe_id), queries.get_food_details_query, re.MULTILINE)
		details_ans = connect_to_db(details_query)

		return (details_ans[0]["recipe_name"], option, details_ans[0]["prep_time"],
				details_ans[0]["picture"], details_ans[0]["food_details"], ingredients, nutritions)