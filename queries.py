#!/usr/bin/env python
import re
from utils import *
#FOOD_NUTRITIONS = [	"sugar",   "iron",     "calcium", "sodium", "protein", "cholesterol", "potassium",
#					"lactose", "vitaminC", "satfat",  "fiber", "calories"]

#VALUES = {"None" : "None", "1" : "None", "d": "dont care", "2" : "less than 5%", "3" : "over 30%"}

weights_view_old= """
CREATE VIEW RECIPE_WEIGHTS AS
SELECT ar.recipe_id as recipe_id, SUM(st.tot_weight) as weight
FROM 	ALL_RECIPES          as ar, 
		INGREDIENTS          as i, 
		RECIPE2INGREDIENTS   as r2i,
		(
			SELECT (r2i.servings * i.serving_weight) as tot_weight, ar.recipe_id as recipe_id
			FROM  	ALL_RECIPES          as ar, 
					INGREDIENTS          as i, 
					RECIPE2INGREDIENTS   as r2i
			WHERE
					ar.recipe_id = r2i.recipe_id
		) as st
WHERE
	ar.recipe_id = r2i.recipe_id AND
	st.recipe_id = r2i.recipe_id
GROUP BY 
	ar.recipe_id
"""

weights_view = """
CREATE VIEW RECIPE_WEIGHTS AS
SELECT SUM(r2i.servings * i.serving_weight_grams) as tot_weight, r2i.recipe_id as recipe_id
FROM 		RECIPE2INGREDIENTS r2i
INNER JOIN 	INGREDIENTS i on i.ingredient_id = r2i.ingredient_id
GROUP BY r2i.recipe_id
"""

recipe_nutritions_view_old = """
CREATE VIEW RECIPE_NUTRITIONS_WEIGHTS AS
SELECT ar.recipe_id as recipe_id, inn.nutrition_id as nutrition_id, SUM(r2i.servings * inn.weight_mg) as weight
FROM	ALL_RECIPES as ar,
		RECIPE2INGREDIENTS as r2i,
		INGREDIENT_NUTRITION as inn
WHERE
	ar.recipe_id = r2i.recipe_id AND
	inn.ingredient_id = r2i.ingredient_id
GROUP BY
	ar.recipe_id, inn.nutrition_id
"""

recipe_nutritions_view = """
CREATE VIEW RECIPE_NUTRITIONS_WEIGHTS AS
SELECT r2i.recipe_id as recipe_id, inn.nutrition_id as nutrition_id, SUM(r2i.servings * inn.weight_mg_from_ingredient) as weight
FROM		RECIPE2INGREDIENTS r2i 
INNER JOIN 	INGREDIENT_NUTRITION inn on inn.ingredient_id = r2i.ingredient_id
GROUP BY r2i.recipe_id, inn.nutrition_id
"""

daily_meals_view_old = """
CREATE VIEW DAILY_MEALS AS
SELECT 	breakfast_r.recipe_id AS breakfast_id, lunch_r.recipe_id AS lunch_id, dinner_r.recipe_id AS dinner_id
FROM	( SELECT recipe_id FROM ALL_RECIPES where course="Breakfast and Brunch") as breakfast_r
		( SELECT recipe_id FROM ALL_RECIPES where course="Lunch") as lunch_r
		( SELECT recipe_id FROM ALL_RECIPES where course="Main Dishes") as dinner_r
"""

daily_meals_view = """
CREATE VIEW DAILY_MEALS AS
SELECT 	breakfast_r.recipe_id AS breakfast_id, lunch_r.recipe_id AS lunch_id, dinner_r.recipe_id AS dinner_id
FROM	( SELECT recipe_id FROM FOOD_RECIPES where course="Breakfast and Brunch") as breakfast_r,
		( SELECT recipe_id FROM FOOD_RECIPES where course="Lunch") as lunch_r,
		( SELECT recipe_id FROM FOOD_RECIPES where course="Main Dishes") as dinner_r
"""
#	<OTHER QUERIES OF THE FORM OF:
#		n.nutrition_name = {} and rnw.nutrition_id = {} and rnw.weight > 0.3 AND
#		rnw.nutrition_id = {} & rnw.weight < 0.05 AND
#		rnw.nutrition_id = {} & rnw.weight = 0
#	>


ineffective_inner_query_for_query3 = """
AND ar.recipe_id in  (
	SELECT DISTINCT ar.recipe_id as recipe_id 
	FROM ALL_RECIPES ar inner join RECIPE_NUTRITIONS_WEIGHTS rnw on ar.recipe_id = rnw.recipe_id
		inner join RECOMMEND_BY_AGE_GENDER rbag on rbag.nutrition_id = rnw.nutrition_id,
		NUTRITIONS as n
	WHERE
		n.nutrition_name = <NUT_KEY> AND
		rnw.weight / rbag.weight_mg <NUT_IF>
)
"""

################################
########### QUERY 1 ############
################################

# food recipes by nutritional values
query1 = """
SELECT ar.recipe_name
FROM		ALL_RECIPES ar
INNER JOIN 	FOOD_RECIPES fr on ar.recipe_id = fr.recipe_id
WHERE
	fr.course = \"<MEAL_OPTION>\"
"""

inner_query_for_query1_2 = """
<AND> ar.recipe_id IN (
SELECT 	rw.recipe_id as recipe_id
FROM 	RECIPE_NUTRITIONS_WEIGHTS as rnw,
		RECIPE_WEIGHTS as rw,
		NUTRITIONS as n
WHERE
		rw.recipe_id = rnw.recipe_id AND
		rnw.nutrition_id = n.nutrition_id AND
		n.nutrition_name = \"<NUT_KEY>\" AND
		rnw.weight / rw.weight <NUT_IF>
)
"""

def get_query1(nutritions_values, meal_option):
	q = re.sub("<MEAL_OPTION>", meal_option, query1, re.MULTILINE)

	for nut in NUTRITIONS:
		if nut == "alcohol":
			continue

		if nutritions_values[nut] != "":
			nline = inner_query_for_query1_2
			nline = re.sub("<NUT_KEY>", nut, nline)
			nline = re.sub("<AND>", "AND", nline)

			if nut == "calories":
				if nutritions_values[nut] != "d":
					nline = re.sub("rnw.weight / rw.weight <NUT_IF>", "rnw.weight <= " + nutritions_values[nut], nline, re.MULTILINE)
					q += nline + "\n"
					print nline
			else:
				if VALUES[nutritions_values[nut]] == "over 30%":
					nline = re.sub("<NUT_IF>", ">= 0.3", nline, re.MULTILINE)
					q += nline + "\n"
				elif VALUES[nutritions_values[nut]] == "less than 5%":
					nline = re.sub("<NUT_IF>", "<= 0.05", nline, re.MULTILINE)
					q += nline + "\n"
				elif VALUES[nutritions_values[nut]] == "None":
					nline = re.sub("<NUT_IF>", "= 0", nline, re.MULTILINE)
					q += nline + "\n"
				elif  VALUES[nutritions_values[nut]] != "dont care":
					print "ERROR - invalid value (" + str(nutritions_values[nut]) + ") for (" + nut + ")"
	return q


################################
########### QUERY 2 ############
################################

# cocktails recipes by nutritional values
query2 = """
SELECT ar.recipe_name
FROM		ALL_RECIPES ar
INNER JOIN 	COCKTAIL_RECIPES cr on ar.recipe_id = cr.recipe_id
WHERE
	<IS_ALCOHOLIC>
"""

def get_query2(nutritions_values):

	first = False
	q = query2
	print "nutritions_values:", nutritions_values

	if "alcohol" in nutritions_values:
		if nutritions_values["alcohol"] == "d":
			q = re.sub("<IS_ALCOHOLIC>", "", q, re.MULTILINE)
			first = True
		elif nutritions_values["alcohol"] == "1" or nutritions_values["alcohol"] == "0":
			q = re.sub("<IS_ALCOHOLIC>", "cr.is_alcoholic = " + nutritions_values["alcohol"], q, re.MULTILINE)
		else:
			print "ERROR"

	for nut in NUTRITIONS:
		if nut == "alcohol":
			continue

		if nutritions_values[nut] != "":
			nline = inner_query_for_query1_2
			nline = re.sub("<NUT_KEY>", nut, nline)

			if nut == "calories":
				if nutritions_values[nut] != "d":

					if first:
						nline = re.sub("<AND>", "", nline, re.MULTILINE)
						first = False
					else:
						nline = re.sub("<AND>", "AND", nline, re.MULTILINE)

					nline = re.sub("rnw.weight / rw.weight <NUT_IF>", "rnw.weight <= " + nutritions_values[nut], nline, re.MULTILINE)
					q += nline + "\n"
			else:
				if VALUES[nutritions_values[nut]] != "dont care":
					if first:
						nline = re.sub("<AND>", "", nline, re.MULTILINE)
						first = False
					else:
						nline = re.sub("<AND>", "AND", nline, re.MULTILINE)

					if VALUES[nutritions_values[nut]] == "over 30%":
						nline = re.sub("<NUT_IF>", ">= 0.3", nline, re.MULTILINE)
						q += nline + "\n"
					elif VALUES[nutritions_values[nut]] == "less than 5%":
						nline = re.sub("<NUT_IF>", "<= 0.05", nline, re.MULTILINE)
						q += nline + "\n"
					elif VALUES[nutritions_values[nut]] == "None":
						nline = re.sub("<NUT_IF>", "= 0", nline, re.MULTILINE)
						q += nline + "\n"
					else:
						print "ERROR - invalid value (" + str(nutritions_values[nut]) + ") for (" + nut + ")"
	return q

################################
########### QUERY 3 ############
################################

query3_old = """
SELECT 	DISTINCT fr.recipe_id
FROM 	RECOMMEND_BY_AGE_GENDER as rbag,
		FOOD_RECIPES as fr,
		ALL_RECIPES as ar
WHERE
		rbag.gender = \"<GENDER>\" AND
		rbag.age = <AGE> AND
		fr.recipe_id = ar.recipe_id AND
		fr.course = \"<MEAL_OPTION>\"
"""

# one recipe by daily values
query3 = """
SELECT 	DISTINCT fr.recipe_id
FROM 	RECOMMEND_BY_AGE_GENDER as rbag,
		FOOD_RECIPES as fr
WHERE
		rbag.gender = \"<GENDER>\" AND
		rbag.age = <AGE> AND
		fr.course = \"<MEAL_OPTION>\"
"""

inner_query_for_query3 = """
AND fr.recipe_id in  (
	SELECT DISTINCT ar.recipe_id as recipe_id 
	FROM 		ALL_RECIPES ar 
	INNER JOIN 	RECIPE_NUTRITIONS_WEIGHTS rnw 
				on ar.recipe_id = rnw.recipe_id
	INNER JOIN 	RECOMMEND_BY_AGE_GENDER rbag 
				on rbag.nutrition_id = rnw.nutrition_id
	INNER JOIN NUTRITIONS n
	WHERE
		n.nutrition_name = \"<NUT_KEY>\" AND
		(
			(
				n.max_or_min = \"min\" AND
				rnw.weight / rbag.weight_mg >= <NUT_VAL>
			)
			OR
			(
				n.max_or_min = \"max\" AND
				rnw.weight / rbag.weight_mg <= <NUT_VAL>
			)
		)
)
"""

def get_query3(nutritions_values, meal_option, age, gender):
	# If it's FullDay then need to use query #4
	if meal_option == "Full Day":
		return get_query4(nutritions_values, age, gender)

	q = re.sub("<MEAL_OPTION>", meal_option, query3, re.MULTILINE)
	q = re.sub("<GENDER>", gender, q, re.MULTILINE)
	q = re.sub("<AGE>", age, q, re.MULTILINE)

	for nut in NUTRITIONS:
		if nut == "alcohol":
			continue

		if nutritions_values[nut] != "" and nutritions_values[nut] != "Don't Care" and nutritions_values[nut] != "d":
			nline = inner_query_for_query3
			nline = re.sub("<NUT_KEY>", nut, nline)
			try:
				val = float(nutritions_values[nut]) / float(100)
			except:
				val = nutritions_values[nut]
				print "ERROR: expected int value, but for:", nut, "got:", val
				return ""

			nline = re.sub("<NUT_VAL>", str(val), nline, re.MULTILINE)

			q += nline

	return q

################################
########### QUERY 4 ############
################################

# all day recipes by daily values
query4 = """
SELECT	*
FROM 	RECOMMEND_BY_AGE_GENDER as rbag,
		DAILY_MEALS as dm,
WHERE	
		rbag.gender = \"<GENDER>\" AND
		rbag.age = <AGE>
"""

inner_query_for_query4 = """
AND dm.breakfast_id, dm.lunch_id, dm.dinner_id IN (
	SELECT dm2.breakfast_id, dm2.lunch_id, dm2.dinner_id
	FROM 		DAILY_MEALS as dm2
		  JOIN 	NUTRITIONS n
	INNER JOIN	RECIPE_NUTRITIONS_WEIGHTS rnw_b on rnw_b.recipe_id = dm2.breakfast_id, rnw_b.nutrition_id = n.nutrition_id
	INNER JOIN	RECIPE_NUTRITIONS_WEIGHTS rnw_l on rnw_l.recipe_id = dm2.lunch_id, rnw_l.nutrition_id = n.nutrition_id
	INNER JOIN	RECIPE_NUTRITIONS_WEIGHTS rnw_d on rnw_d.recipe_id = dm2.dinner_id, rnw_d.nutrition_id = n.nutrition_id
	INNER JOIN 	RECOMMEND_BY_AGE_GENDER rbag on rbag.nutrition_id = n.nutrition_id
	WHERE
		rbag.age = <AGE> AND
		rbag.gender = <GENDER> AND
		n.nutrition_name = \"<NUT_KEY>\" AND
		(
			n.max_or_min = \"min\" AND
			(rnw_b.weight + rnw_l.weight + rnw_d.weight) / rbag.weight_mg >= <NUT_VAL>
		)
		OR
		(
			n.max_or_min = \"max\" AND
			r(rnw_b.weight + rnw_l.weight + rnw_d.weight) / rbag.weight_mg <= <NUT_VAL>
		)
)
"""

def get_query4(nutritions_values, age, gender):
	# If it's FullDay then need to use query #4

	q = re.sub("<GENDER>", gender, query4, re.MULTILINE)
	q = re.sub("<AGE>", age, q, re.MULTILINE)

	for nut in NUTRITIONS:

		if nutritions_values[nut] != "" or nutritions_values[nut] == "Don't Care" or nutritions_values[nut] == "d":
			nline = inner_query_for_query4
			nline = re.sub("<NUT_KEY>", nut, nline)
			try:
				val = float(nutritions_values[nut]) / float(100)
			except:
				val = nutritions_values[nut]
				print "ERROR: expected int value, but got:", val
				return ""

			nline = re.sub("<NUT_IF>", str(val), nline, re.MULTILINE)

			q += nline

	return q

################################
########### QUERY 5 ############
################################

allergies_query = """SELECT DISTINCT ar.recipe_id AS recipe_id, ar.recipe_name AS recipe_name
FROM 
		ALL_RECIPES AS ar,
		RECIPE2INGREDIENTS AS r2i,
		<FOOD_DRINK>
WHERE
		<FOOD_DRINK_FIELDS>
		AND ar.recipe_id = r2i.recipe_id
		<ALG_QUERY_1>
		<ALG_QUERY_2>
		<ALG_QUERY_3>
GROUP BY
		ar.recipe_id"""

alg_query = """AND ar.recipe_id NOT IN (
	SELECT r2i.recipe_id
	FROM
			RECIPE2INGREDIENTS AS r2i,
			INGREDIENTS AS ing
	WHERE
			r2i.ingredient_id = ing.ingredient_id AND
			ing.ingredient_name LIKE \"%<ALG>%\"
)"""

food_fields = """ar.recipe_id = fr.recipe_id
		AND fr.course = \"<MEAL_OPTION>\""""

cocktail_fields = """ar.recipe_id = cr.recipe_id"""


def get_query5(allergans, option):
	if option == "Cocktail":
		query = re.sub("<FOOD_DRINK>", "COCKTAIL_RECIPES AS cr", allergies_query, re.MULTILINE)
		query = re.sub("<FOOD_DRINK_FIELDS>", cocktail_fields, query, re.MULTILINE)
	else:
		query = re.sub("<FOOD_DRINK>", "FOOD_RECIPES AS fr", allergies_query, re.MULTILINE)
		my_food_fields = re.sub("<MEAL_OPTION>", option, food_fields, re.MULTILINE)
		query = re.sub("<FOOD_DRINK_FIELDS>", my_food_fields, query, re.MULTILINE)

	if allergans[0] != "":
		alg_query1 = re.sub("<ALG>", allergans[0], alg_query, re.MULTILINE)
	else:
		alg_query1 = ""

	if allergans[1] != "":
		alg_query2 = re.sub("<ALG>", allergans[1], alg_query, re.MULTILINE)
	else:
		alg_query2 = ""

	if allergans[2] != "":
		alg_query3 = re.sub("<ALG>", allergans[2], alg_query, re.MULTILINE)
	else:
		alg_query3 = ""

	query = re.sub("<ALG_QUERY_1>", alg_query1, query, re.MULTILINE)
	query = re.sub("<ALG_QUERY_2>", alg_query2, query, re.MULTILINE)
	query = re.sub("<ALG_QUERY_3>", alg_query3, query, re.MULTILINE)

	return query

