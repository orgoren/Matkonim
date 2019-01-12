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

NUTRITIONS = [	"sugar",   "iron",     "calcium", "sodium", "protein", "cholesterol", "potassium",
				"lactose", "vitaminC", "saturated",  "dietary_fiber",  "alcohol", "calories"]

MEAL_OPTIONS = ["Main Dishes", "Side Dishes", "Appetizers", "Lunch", "Breakfast and Brunch", 
				"Snacks", "Soups", "Salads", "Breads", "Condiments and Sauce", "Desserts", "FullDay"]

VALUES = {"None" : "None", "1" : "None", "d": "dont care", "2" : "less than 5%", "3" : "over 30%"}

AGE_RANGES = {"14_18" : "0", "19_30" : "1", "31_40" : "2", "41_50" : 3, "51_60" : 4, "61_70" : 5, "71" : 6}

def get_username_and_password():
	username = raw_input("enter username (for nova): ")
	password = getpass.getpass("enter password (for nova): ")
	return username, password


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
	return "ERROR"





