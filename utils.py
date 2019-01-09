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
				"lactose", "vitaminC", "satfat",  "fiber",  "alcohol", "calories"]

MEAL_OPTIONS = ["Main Dishes", "Side Dishes", "Appetizers", "Lunch", "Breakfast and Brunch", 
				"Snacks", "Soups", "Salads", "Breads", "Condiments and Sauce", "Desserts"]

VALUES = {"None" : "None", "1" : "None", "d": "dont care", "2" : "less than 5%", "3" : "over 30%"}


def get_username_and_password():
	username = raw_input("enter username (for nova): ")
	password = getpass.getpass("enter password (for nova): ")
	return username, password

def get_nutritions_values(form, is_food=True):
	nutritions_values = {}
	nutritions = NUTRITIONS
	if is_food:
		nutritions.remove("alcohol"
			)
	for nutrition in nutritions:
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





