#!/usr/bin/env python
import re
from utils import *

################################
############ VIEWS #############
################################

weights_view = """CREATE VIEW VIEW_RECIPE_WEIGHTS AS
SELECT DISTINCT ROUND(SUM(r2i.servings * i.serving_weight_grams),2) as weight, r2i.recipe_id as recipe_id
FROM 		INGREDIENTS i
INNER JOIN RECIPE2INGREDIENTS r2i on i.ingredient_id = r2i.ingredient_id
GROUP BY r2i.recipe_id"""

recipe_nutritions_view = """CREATE VIEW VIEW_RECIPE_NUTRITIONS_WEIGHTS AS
SELECT DISTINCT r2i.recipe_id as recipe_id, inn.nutrition_id as nutrition_id, ROUND(SUM(r2i.servings * inn.weight_mg_from_ingredient),2) as weight,
				ROUND((SUM(r2i.servings * inn.weight_mg_from_ingredient) / (vrw.weight * 1000)),2) as precentage
FROM		INGREDIENT_NUTRITION inn 
INNER JOIN 	RECIPE2INGREDIENTS r2i on inn.ingredient_id = r2i.ingredient_id
INNER JOIN 	VIEW_RECIPE_WEIGHTS vrw on vrw.recipe_id = r2i.recipe_id
GROUP BY r2i.recipe_id, inn.nutrition_id"""


################################
####### General Queries ########
################################

# A query to get the ingredients of a certain recipe
get_ingredients_query = """SELECT DISTINCT r2i.full_ingredient_line
FROM		INGREDIENTS AS i
INNER JOIN	RECIPE2INGREDIENTS r2i on r2i.ingredient_id = i.ingredient_id
WHERE		r2i.recipe_id = <RECIPE_ID>"""

# A query to get the nutritional values of a certain recipe
get_nutritionals_query = """SELECT DISTINCT n.nutrition_name as nutrition_name, SUM(r2i.servings * inn.weight_mg_from_ingredient) as weight
FROM		INGREDIENT_NUTRITION inn
INNER JOIN 	NUTRITIONS n on n.nutrition_id = inn.nutrition_id
INNER JOIN	RECIPE2INGREDIENTS r2i on inn.ingredient_id = r2i.ingredient_id
WHERE 		r2i.recipe_id = <RECIPE_ID>
GROUP BY 	r2i.recipe_id, inn.nutrition_id"""

# A query to get the full details of a certain cocktail recipe
get_cocktail_details_query = """SELECT DISTINCT ar.recipe_name AS recipe_name, ar.picture AS picture,
cr.is_alcoholic AS is_alcoholic, cr.cocktail_details AS cocktail_details, cr.serving_glass AS serving_glass
FROM		COCKTAIL_RECIPES cr
INNER JOIN	ALL_RECIPES ar on cr.recipe_id = ar.recipe_id
WHERE		ar.recipe_id = <RECIPE_ID>"""

# A query to get the full details of a certain food recipe
get_food_details_query = """SELECT DISTINCT ar.recipe_name AS recipe_name, ar.picture AS picture,
fr.food_details AS food_details, fr.prep_time_in_minutes AS prep_time
FROM		FOOD_RECIPES fr
INNER JOIN	ALL_RECIPES ar on fr.recipe_id = ar.recipe_id
WHERE		ar.recipe_id = <RECIPE_ID>"""


################################
########### QUERY 1 ############
################################

# The query if no nutritional preferences are chosen
query1_no_nutritions = """SELECT DISTINCT fr.recipe_id
FROM	FOOD_RECIPES as fr
WHERE	MATCH(fr.course) AGAINST(\"<MEAL_OPTION>\") 
<PREP_TIME_LINE>"""

# The query for food recipes by given nutritional preferences
query1 = """SELECT DISTINCT fr.recipe_id
FROM 		FOOD_RECIPES as fr
INNER JOIN	(SELECT DISTINCT COUNT(fr.recipe_id) as cnt, fr.recipe_id as recipe_id
FROM		FOOD_RECIPES fr
INNER JOIN	VIEW_RECIPE_NUTRITIONS_WEIGHTS vrnw on fr.recipe_id = vrnw.recipe_id
INNER JOIN	NUTRITIONS n on vrnw.nutrition_id = n.nutrition_id
WHERE
	MATCH(fr.course) AGAINST(\"<MEAL_OPTION>\") 
	<PREP_TIME_LINE>
<FILTER_BY_NUTRITIONS>
<NUTRITIONS_CHECK>
GROUP BY fr.recipe_id
) RECIPE_COUNTERS on RECIPE_COUNTERS.recipe_id = fr.recipe_id
WHERE RECIPE_COUNTERS.cnt = <NUT_NUM>"""

FILTER_BY_NUTRITIONS_for_query1_2 = "MATCH(n.nutrition_name) AGAINST(\"<NUT_KEY>\")"

NUTRITIONS_CHECK_for_query1_2 = """AND	(NOT MATCH(n.nutrition_name) AGAINST(\"<NUT_KEY>\") OR vrnw.precentage <NUT_IF>)"""

prep_time_line = "AND fr.prep_time_in_minutes <= <PREP_TIME>"

# A function that receives nutritional values, meal option and prep time, and returns the query
# for foods by nutritional values.
def get_query1(nutritions_values, meal_option, prep_time):
	q = re.sub("<MEAL_OPTION>", meal_option, query1, re.MULTILINE)

	if prep_time == "dont care":
		q = re.sub("<PREP_TIME_LINE>", "", q, re.MULTILINE)
	else:
		p = re.sub("<PREP_TIME>", prep_time, prep_time_line, re.MULTILINE)
		q = re.sub("<PREP_TIME_LINE>", p, q, re.MULTILINE)

	filter_by_nutritions = "AND (<NUTS>)"	
	nuts_filter = []
	nuts_check = []

	for nut in NUTRITIONS:
		if nut == "alcohol":
			continue

		if nutritions_values[nut] != "":
			nline1 = FILTER_BY_NUTRITIONS_for_query1_2
			nline2 = NUTRITIONS_CHECK_for_query1_2
			nline2 = re.sub("<NUT_KEY>", nut, nline2)

			if nut == "calories_kcal":
				if nutritions_values[nut] != "d":
					nline2 = re.sub("vrnw.precentage <NUT_IF>", "vrnw.weight <= " + nutritions_values[nut], nline2, re.MULTILINE)
					nuts_filter.append(re.sub("<NUT_KEY>", nut, nline1))
					nuts_check.append(nline2)
			else:
				if VALUES[nutritions_values[nut]] == "over 15%":
					nline2 = re.sub("<NUT_IF>", ">= 0.15", nline2, re.MULTILINE)
					nuts_filter.append(re.sub("<NUT_KEY>", nut, nline1))
					nuts_check.append(nline2)

				elif VALUES[nutritions_values[nut]] == "less than 5%":
					nline2 = re.sub("<NUT_IF>", "<= 0.05", nline2, re.MULTILINE)					
					nuts_filter.append(re.sub("<NUT_KEY>", nut, nline1))
					nuts_check.append(nline2)

				elif VALUES[nutritions_values[nut]] == "None":
					nline2 = re.sub("<NUT_IF>", "= 0", nline2, re.MULTILINE)
					nuts_filter.append(re.sub("<NUT_KEY>", nut, nline1))
					nuts_check.append(nline2)

				elif  VALUES[nutritions_values[nut]] != "dont care":
					print "ERROR - invalid value (" + str(nutritions_values[nut]) + ") for (" + nut + ")"

	# no nutritions
	if len(nuts_filter) == 0:
		q = query1_no_nutritions
		q = re.sub("<MEAL_OPTION>", meal_option, q, re.MULTILINE)
		if prep_time == "dont care":
			q = re.sub("<PREP_TIME_LINE>", "", q, re.MULTILINE)
		else:
			p = re.sub("<PREP_TIME>", prep_time, prep_time_line, re.MULTILINE)
			q = re.sub("<PREP_TIME_LINE>", p, q, re.MULTILINE)
		return q

	q = re.sub("<NUT_NUM>", str(len(nuts_filter)), q, re.MULTILINE)

	filter_by_nutritions = re.sub("<NUTS>", " OR ".join(nuts_filter), filter_by_nutritions, re.MULTILINE)

	q = re.sub("<FILTER_BY_NUTRITIONS>", filter_by_nutritions, q, re.MULTILINE)

	q = re.sub("<NUTRITIONS_CHECK>", "\n".join(nuts_check), q, re.MULTILINE)

	return q


################################
########### QUERY 2 ############
################################

# The query if no nutritional preferences are chosen
query2_no_nutritions = """SELECT DISTINCT cr.recipe_id
FROM COCKTAIL_RECIPES as cr
<IS_ALCOHOLIC>"""

# The query for cocktail recipes by given nutritional preferences
query2 = """SELECT DISTINCT cr.recipe_id
FROM		COCKTAIL_RECIPES cr
INNER JOIN	(SELECT DISTINCT COUNT(cr.recipe_id) as cnt, cr.recipe_id as recipe_id
FROM		COCKTAIL_RECIPES cr
INNER JOIN	VIEW_RECIPE_NUTRITIONS_WEIGHTS vrnw on cr.recipe_id = vrnw.recipe_id
INNER JOIN	NUTRITIONS n on vrnw.nutrition_id = n.nutrition_id
WHERE
<IS_ALCOHOLIC>
<FILTER_BY_NUTRITIONS>
<NUTRITIONS_CHECK>
GROUP BY cr.recipe_id
) RECIPE_COUNTERS on RECIPE_COUNTERS.recipe_id = cr.recipe_id
WHERE RECIPE_COUNTERS.cnt = <NUT_NUM>"""

# A function that receives nutritional values, and returns the query
# for cocktails by nutritional values.
def get_query2(nutritions_values):
	q = query2
	q2 = query2_no_nutritions
	is_alcoholic_filter = False

	if "alcohol" in nutritions_values:
		if nutritions_values["alcohol"] == "d":
			q = re.sub("<IS_ALCOHOLIC>", "", q, re.MULTILINE)
			q2 = re.sub("<IS_ALCOHOLIC>", "", q2, re.MULTILINE)
		elif nutritions_values["alcohol"] == "1" or nutritions_values["alcohol"] == "0":
			q = re.sub("<IS_ALCOHOLIC>", "cr.is_alcoholic = " + nutritions_values["alcohol"], q, re.MULTILINE)
			q2 = re.sub("<IS_ALCOHOLIC>", "WHERE cr.is_alcoholic = " + nutritions_values["alcohol"], q2, re.MULTILINE)
			is_alcoholic_filter = True
		else:
			print "ERROR"

	if is_alcoholic_filter:
		filter_by_nutritions = "AND (<NUTS>)"
	else:
		filter_by_nutritions = "(<NUTS>)"

	nuts_filter = []
	nuts_check = []

	for nut in NUTRITIONS:
		if nut == "alcohol":
			continue

		if nutritions_values[nut] != "":
			nline1 = FILTER_BY_NUTRITIONS_for_query1_2
			nline2 = NUTRITIONS_CHECK_for_query1_2
			nline2 = re.sub("<NUT_KEY>", nut, nline2)

			if nut == "calories_kcal":
				if nutritions_values[nut] != "d":
					nline2 = re.sub("vrnw.precentage <NUT_IF>", "vrnw.weight <= " + nutritions_values[nut], nline2, re.MULTILINE)
					nuts_filter.append(re.sub("<NUT_KEY>", nut, nline1))
					nuts_check.append(nline2)
			else:
				if VALUES[nutritions_values[nut]] == "over 15%":
					nline2 = re.sub("<NUT_IF>", ">= 0.15", nline2, re.MULTILINE)
					nuts_filter.append(re.sub("<NUT_KEY>", nut, nline1))
					nuts_check.append(nline2)

				elif VALUES[nutritions_values[nut]] == "less than 5%":
					nline2 = re.sub("<NUT_IF>", "<= 0.05", nline2, re.MULTILINE)					
					nuts_filter.append(re.sub("<NUT_KEY>", nut, nline1))
					nuts_check.append(nline2)

				elif VALUES[nutritions_values[nut]] == "None":
					nline2 = re.sub("<NUT_IF>", "= 0", nline2, re.MULTILINE)
					nuts_filter.append(re.sub("<NUT_KEY>", nut, nline1))
					nuts_check.append(nline2)

				elif  VALUES[nutritions_values[nut]] != "dont care":
					print "ERROR - invalid value (" + str(nutritions_values[nut]) + ") for (" + nut + ")"

	# no nutritions
	if len(nuts_filter) == 0:
		return q2

	q = re.sub("<NUT_NUM>", str(len(nuts_filter)), q, re.MULTILINE)

	filter_by_nutritions = re.sub("<NUTS>", " OR ".join(nuts_filter), filter_by_nutritions, re.MULTILINE)

	q = re.sub("<FILTER_BY_NUTRITIONS>", filter_by_nutritions, q, re.MULTILINE)

	q = re.sub("<NUTRITIONS_CHECK>", "\n".join(nuts_check), q, re.MULTILINE)

	return q



################################
########### QUERY 3 ############
################################

# The query for getting food recipe by meal option if no daily values are chosen
query3_no_nutritions = """SELECT DISTINCT fr.recipe_id
FROM FOOD_RECIPES as fr
WHERE MATCH(fr.course) AGAINST(\"<MEAL_OPTION>\")"""

# The query for getting a food recipe given daily values by specific meal, gender, age
# and nutritional values requested
query3 = """SELECT DISTINCT fr.recipe_id
FROM 	FOOD_RECIPES as fr
INNER JOIN (
SELECT 		DISTINCT COUNT(fr.recipe_id) as cnt, fr.recipe_id as recipe_id
FROM 		FOOD_RECIPES fr 
INNER JOIN 	VIEW_RECIPE_NUTRITIONS_WEIGHTS vrnw on fr.recipe_id = vrnw.recipe_id
INNER JOIN 	RECOMMEND_BY_AGE_GENDER rbag on rbag.nutrition_id = vrnw.nutrition_id
INNER JOIN 	NUTRITIONS n on n.nutrition_id = rbag.nutrition_id
WHERE
rbag.gender = \"<GENDER>\" AND
rbag.age = <AGE> AND
MATCH(fr.course) AGAINST(\"<MEAL_OPTION>\") 
<FILTER_BY_NUTRITIONS>
<NUTRITIONS_CHECK>
GROUP by fr.recipe_id
) RECIPE_COUNTERS on RECIPE_COUNTERS.recipe_id = fr.recipe_id
WHERE RECIPE_COUNTERS.cnt = <NUT_NUM>"""

FILTER_BY_NUTRITIONS_for_query3_4 = "MATCH(n.nutrition_name) AGAINST(\"<NUT_KEY>\")"

NUTRITIONS_CHECK_for_query3_4 = """AND	(	n.nutrition_name <> \"<NUT_KEY>\" OR 
		(
			(
				n.max_or_min = \"min\" AND
				vrnw.weight / rbag.weight_mg >= <NUT_VAL>
			)
			OR
			(
				n.max_or_min = \"max\" AND
				vrnw.weight / rbag.weight_mg <= <NUT_VAL>
			)
		)
	)"""

# A function that receives meal option, age, gender and nutritional values, and returns the query
# for food recipes by daily values.
def get_query3(nutritions_values, meal_option, age, gender):
	# If it's FullDay then need to use query #4
	if meal_option == "Full Day":
		return get_query4(nutritions_values, age, gender)

	q = re.sub("<MEAL_OPTION>", meal_option, query3, re.MULTILINE)
	q = re.sub("<GENDER>", gender, q, re.MULTILINE)
	q = re.sub("<AGE>", age, q, re.MULTILINE)

	nuts_filter = []
	nuts_check = []

	for nut in NUTRITIONS:
		if nut == "alcohol":
			continue

		if nutritions_values[nut] != "" and nutritions_values[nut] != "Don't Care" and nutritions_values[nut] != "d":
			nline1 = NUTRITIONS_CHECK_for_query3_4
			nline1 = re.sub("<NUT_KEY>", nut, nline1)
			try:
				val = float(nutritions_values[nut]) / float(100)
			except:
				val = nutritions_values[nut]
				print "ERROR: expected int value, but for:", nut, "got:", val
				return ""

			nline1 = re.sub("<NUT_VAL>", str(val), nline1, re.MULTILINE)
			nline2 = re.sub("<NUT_KEY>", nut, FILTER_BY_NUTRITIONS_for_query3_4)

			nuts_filter.append(nline2)
			nuts_check.append(nline1)

	if len(nuts_filter) == 0:
		q = query3_no_nutritions
		q = re.sub("<MEAL_OPTION>", meal_option, q, re.MULTILINE)
		return q

	nutritions_filter = " OR ".join(nuts_filter)
	nutritions_filter = "AND (" + nutritions_filter + ")"
	nutritions_check = "\n".join(nuts_check)

	q = re.sub("<FILTER_BY_NUTRITIONS>", nutritions_filter, q, re.MULTILINE)
	q = re.sub("<NUTRITIONS_CHECK>", nutritions_check, q, re.MULTILINE)
	q = re.sub("<NUT_NUM>", str(len(nuts_filter)), q, re.MULTILINE)
	return q

################################
########### QUERY 4 ############
################################

# The query for getting food recipe by meal option if no daily values are chosen
query4_no_nutritions = """SELECT DISTINCT fr.recipe_id as recipe_id
FROM FOOD_RECIPES fr
WHERE MATCH(fr.course) AGAINST(\"<MEAL_OPTION>\")  """

# The query for getting a food recipe given daily values by specific meal, gender, age
# and nutritional values requested
query4 = """SELECT DISTINCT fr.recipe_id as recipe_id
FROM FOOD_RECIPES fr 
INNER JOIN VIEW_RECIPE_NUTRITIONS_WEIGHTS vrnw on fr.recipe_id = vrnw.recipe_id
INNER JOIN RECOMMEND_BY_AGE_GENDER rbag on rbag.nutrition_id = vrnw.nutrition_id
INNER JOIN NUTRITIONS n on rbag.nutrition_id = n.nutrition_id
WHERE
rbag.age = <AGE> AND
rbag.gender = "<GENDER>" AND
MATCH(fr.course) AGAINST(\"<MEAL_OPTION>\") 
<FILTER_BY_NUTRITIONS>
<NUTRITIONS_CHECK>"""

# A function that receives the nutritional preferences, age, and gender,
# and build the queries for getting a full day meal plan according to them.
def get_query4(nutritions_values, age, gender):
	q = query4

	q = re.sub("<GENDER>", gender, q, re.MULTILINE)
	q = re.sub("<AGE>", age, q, re.MULTILINE)
	
	nuts_filter = []
	nuts_check = []

	for nut in NUTRITIONS:
		if nut == "alcohol":
			continue

		if nutritions_values[nut] != "" and nutritions_values[nut] != "Don't Care" and nutritions_values[nut] != "d":
			nline1 = NUTRITIONS_CHECK_for_query3_4
			nline1 = re.sub("<NUT_KEY>", nut, nline1)
			try:
				val = float(nutritions_values[nut]) / float(100)
			except:
				val = nutritions_values[nut]
				print "ERROR: expected int value, but for:", nut, "got:", val
				return ""

			nline1 = re.sub("<NUT_VAL>", "<PRECENTAGE> * " + str(val), nline1, re.MULTILINE)
			nline2 = re.sub("<NUT_KEY>", nut, FILTER_BY_NUTRITIONS_for_query3_4)

			nuts_filter.append(nline2)
			nuts_check.append(nline1)

	if len(nuts_filter) == 0:
		q = query4_no_nutritions
	else:

		nutritions_filter = " OR ".join(nuts_filter)
		nutritions_filter = "AND (" + nutritions_filter + ")"
		nutritions_check = "\n".join(nuts_check)

		q = re.sub("<FILTER_BY_NUTRITIONS>", nutritions_filter, q, re.MULTILINE)
		q = re.sub("<NUTRITIONS_CHECK>", nutritions_check, q, re.MULTILINE)
		q = re.sub("<NUT_NUM>", str(len(nuts_filter)), q, re.MULTILINE)

	queries = {}

	for meal in FULL_DAY_MEALS:
		meal_q = q
		meal_option = FULL_DAY_MEALS[meal]["meal"]
		meal_precentage = FULL_DAY_MEALS[meal]["precentage"]
		meal_q = re.sub("<MEAL_OPTION>", meal_option, meal_q, re.MULTILINE)
		meal_q = re.sub("<PRECENTAGE>", str(meal_precentage), meal_q, re.MULTILINE)
		queries[meal] = meal_q

	return queries


################################
########### QUERY 5 ############
################################

allergies_query_old_2 = """SELECT DISTINCT ar.recipe_id AS recipe_id, ar.recipe_name AS recipe_name
FROM 		ALL_RECIPES ar 
INNER JOIN 	RECIPE2INGREDIENTS r2i on ar.recipe_id = r2i.recipe_id,
			<FOOD_DRINK>
WHERE
		<FOOD_DRINK_FIELDS>
		<ALG_QUERY_1>
		<ALG_QUERY_2>
		<ALG_QUERY_3>
GROUP BY
		ar.recipe_id"""

# The query for getting food or cocktail recipes according to unwanted ingredients
allergies_query = """SELECT DISTINCT ar.recipe_id AS recipe_id, ar.recipe_name AS recipe_name
FROM 		ALL_RECIPES AS ar 
INNER JOIN 	RECIPE2INGREDIENTS r2i on ar.recipe_id = r2i.recipe_id
INNER JOIN  <FOOD_DRINK>
WHERE
		<FOOD_DRINK_FIELDS>
		<ALG_QUERY_1>
		<ALG_QUERY_2>
		<ALG_QUERY_3>
GROUP BY
		ar.recipe_id"""

alg_query = """<AND> ar.recipe_id NOT IN (
	SELECT DISTINCT r2i.recipe_id
	FROM		RECIPE2INGREDIENTS r2i 
	INNER JOIN 	INGREDIENTS ing on r2i.ingredient_id = ing.ingredient_id
	WHERE MATCH(
				ing.ingredient_name
	)
	AGAINST(
				\"<ALG>\"
	)
)"""

food_fields_old = """ar.recipe_id = fr.recipe_id
		AND MATCH(fr.course) AGAINST(\"<MEAL_OPTION>\")  """

food_fields = """MATCH(fr.course) AGAINST(\"<MEAL_OPTION>\")  """

cocktail_fields = """ar.recipe_id = cr.recipe_id"""

# A function that receives an array of ingredients to be ruled out of our recipe, and a meal option or cocktail,
# and builds the query for getting recipes according to them.
def get_query5(allergans, option):
	first = False
	algqueries = []

	if option == "Cocktail":
		query = re.sub("<FOOD_DRINK>", "COCKTAIL_RECIPES cr on r2i.recipe_id = cr.recipe_id", allergies_query, re.MULTILINE)
		first = True
		query = re.sub("<FOOD_DRINK_FIELDS>", "", query, re.MULTILINE)
	else:
		query = re.sub("<FOOD_DRINK>", "FOOD_RECIPES fr on r2i.recipe_id = fr.recipe_id", allergies_query, re.MULTILINE)
		my_food_fields = re.sub("<MEAL_OPTIONS>", option, food_fields, re.MULTILINE)
		query = re.sub("<FOOD_DRINK_FIELDS>", my_food_fields, query, re.MULTILINE)

	for allergan in allergans:
		if allergan != "":
			if first:
				alg_query_t = re.sub("<AND>", "", alg_query, re.MULTILINE)
				first = False
			else:
				alg_query_t = re.sub("<AND>", "AND", alg_query, re.MULTILINE)		

			algqueries.append(re.sub("<ALG>", allergan, alg_query_t, re.MULTILINE))
		else:
			algqueries.append("")


	print "============================="
	print algqueries
	print "-============================"

	query = re.sub("<ALG_QUERY_1>", algqueries[0], query, re.MULTILINE)
	query = re.sub("<ALG_QUERY_2>", algqueries[1], query, re.MULTILINE)
	query = re.sub("<ALG_QUERY_3>", algqueries[2], query, re.MULTILINE)

	return query

################################
###########  TRIVIA1 ###########
################################

trivia_1_get_max_nutrition = """
SELECT DISTINCT n.nutrition_id, n.nutrition_name
FROM NUTRITIONS n
INNER JOIN
(
	SELECT DISTINCT r2i.recipe_id as recipe_id, inn.nutrition_id as nutrition_id, SUM(r2i.servings * inn.weight_mg_from_ingredient) as weight
	FROM		RECIPE2INGREDIENTS r2i 
	INNER JOIN 	INGREDIENT_NUTRITION inn on inn.ingredient_id = r2i.ingredient_id
	WHERE		r2i.recipe_id = <RECIPE_ID>
	GROUP BY r2i.recipe_id, inn.nutrition_id
) vrnw on n.nutrition_id = vrnw.nutrition_id
INNER JOIN(
			SELECT DISTINCT v.recipe_id, MAX(v.weight) as max_weight
			FROM (SELECT DISTINCT r2i.recipe_id as recipe_id, inn.nutrition_id as nutrition_id, SUM(r2i.servings * inn.weight_mg_from_ingredient) as weight
				FROM		RECIPE2INGREDIENTS r2i 
				INNER JOIN 	INGREDIENT_NUTRITION inn on inn.ingredient_id = r2i.ingredient_id
				WHERE		r2i.recipe_id = <RECIPE_ID>
				GROUP BY r2i.recipe_id, inn.nutrition_id) AS v
			GROUP BY v.recipe_id 
) max_nut_table on vrnw.weight = max_nut_table.max_weight
"""

trivia_1_get_random_recipe = """
SELECT DISTINCT recipe_id, recipe_name from ALL_RECIPES order by rand() limit 1
"""

trivia_1_get_random_nutritions = """
SELECT DISTINCT nutrition_id, nutrition_name
FROM NUTRITIONS
WHERE nutrition_id <> <ANS_NUTRITION_ID>
order by rand()
Limit 3
"""

def get_query_trivia_1(recipe_id):
	return re.sub("<RECIPE_ID>", str(recipe_id), trivia_1_get_max_nutrition, re.MULTILINE)

def get_query_trivia_1_random_nutritions(nutrition_id):
	return re.sub("<ANS_NUTRITION_ID>", str(nutrition_id), trivia_1_get_random_nutritions, re.MULTILINE)

################################
###########  TRIVIA2 ###########
################################
trivia_2_get_recipe_of_max_nutrition = """
SELECT 		DISTINCT r2i.recipe_id as recipe_id, inn.nutrition_id as nutrition_id, SUM(r2i.servings * inn.weight_mg_from_ingredient) as weight
FROM		RECIPE2INGREDIENTS r2i 
INNER JOIN 	INGREDIENT_NUTRITION inn on inn.ingredient_id = r2i.ingredient_id
WHERE		inn.nutrition_id = <NUTRITION_ID> AND
			(
				r2i.recipe_id = <RECIPE_ID1> OR
				r2i.recipe_id = <RECIPE_ID2> OR
				r2i.recipe_id = <RECIPE_ID3> OR
				r2i.recipe_id = <RECIPE_ID4>
			)
GROUP BY 	r2i.recipe_id, inn.nutrition_id
HAVING weight >= ALL
(
	SELECT 		DISTINCT SUM(r2i.servings * inn.weight_mg_from_ingredient) as weight
	FROM		RECIPE2INGREDIENTS r2i 
	INNER JOIN 	INGREDIENT_NUTRITION inn on inn.ingredient_id = r2i.ingredient_id
	WHERE		inn.nutrition_id = <NUTRITION_ID> AND
				(
					r2i.recipe_id = <RECIPE_ID1> OR
					r2i.recipe_id = <RECIPE_ID2> OR
					r2i.recipe_id = <RECIPE_ID3> OR
					r2i.recipe_id = <RECIPE_ID4>
				)
	GROUP BY r2i.recipe_id, inn.nutrition_id
)
"""

trivia_2_get_random_nutrition = """
SELECT DISTINCT nutrition_id, nutrition_name FROM NUTRITIONS ORDER BY RAND() LIMIT 1
"""

trivia_2_get_random_recipes = """
SELECT DISTINCT recipe_id, recipe_name
FROM ALL_RECIPES
order by rand()
Limit 4
"""

def get_query_trivia_2(recipe_id1, recipe_id2, recipe_id3 ,recipe_id4, nutrition_id):
	query = re.sub("<RECIPE_ID1>", str(recipe_id1), trivia_2_get_recipe_of_max_nutrition, re.MULTILINE)
	query = re.sub("<RECIPE_ID2>", str(recipe_id2), query, re.MULTILINE)
	query = re.sub("<RECIPE_ID3>", str(recipe_id3), query, re.MULTILINE)
	query = re.sub("<RECIPE_ID4>", str(recipe_id4), query, re.MULTILINE)
	return re.sub("<NUTRITION_ID>", str(nutrition_id), query, re.MULTILINE)

################################
###########  TRIVIA3 ###########
################################


trivia_3_get_random_ingredient = """
SELECT ingredient_id, ingredient_name
FROM INGREDIENTS 
WHERE ingredient_id <> <INGREDIENT_ID>
ORDER BY RAND()
LIMIT 3
"""

trivia3_get_max_ingredient_of_precentage_from_nutrition = """
SELECT i.ingredient_name, i.ingredient_id
FROM INGREDIENTS i
INNER JOIN (
	SELECT r2i.ingredient_id as ingredient_id, count(r2i.recipe_id) as cnt
	FROM 		RECIPE2INGREDIENTS r2i
	INNER JOIN 	INGREDIENT_NUTRITION inn on r2i.ingredient_id = inn.ingredient_id
	INNER JOIN 	NUTRITIONS n on n.nutrition_id = inn.nutrition_id,
				RECOMMEND_BY_AGE_GENDER as rbag
	WHERE
		n.nutrition_id = <NUTRITION_ID>
		AND
		rbag.age = <AGE> AND rbag.is_female = <GENDER>
		AND 
		inn.weight_mg_from_ingredient / rbag.weight_mg >= <RANDOM_PRECENTAGE>
	GROUP BY r2i.ingredient_id, r2i.recipe_id
	HAVING cnt >= <MIN_RECIPES>
	ORDER BY cnt DESC
) INGREDIENTS_COUNT on i.ingredient_id = INGREDIENTS_COUNT.ingredient_id
LIMIT 1
"""

def get_trivia_3(age, gender, nutrition_id, precentage, min_recipes):
	q = trivia3_get_max_ingredient_of_precentage_from_nutrition
	q = re.sub("<NUTRITION_ID>", str(nutrition_id), q, re.MULTILINE)
	q = re.sub("<AGE>", str(age), q, re.MULTILINE)
	q = re.sub("<GENDER>", str(gender), q, re.MULTILINE)
	q = re.sub("<RANDOM_PRECENTAGE>", str(precentage), q, re.MULTILINE)
	q = re.sub("<MIN_RECIPES>", str(min_recipes), q, re.MULTILINE)
	return q

def get_query_trivia_3_random_ingredients(ingredient_id):
	return re.sub("<INGREDIENT_ID>", str(ingredient_id), trivia_3_get_random_ingredient)


###############################################################################################
###############################################################################################
###############################################################################################
###############################################################################################
################################## Old QUERIES ################################################
###############################################################################################
###############################################################################################
###############################################################################################
###############################################################################################


alg_query_old = """AND ar.recipe_id NOT IN (
	SELECT DISTINCT r2i.recipe_id
	FROM
			RECIPE2INGREDIENTS AS r2i,
			INGREDIENTS AS ing
	WHERE
			r2i.ingredient_id = ing.ingredient_id AND
			ing.ingredient_name LIKE \"%<ALG>%\"
	)"""


allergies_query_old = """SELECT DISTINCT ar.recipe_id AS recipe_id, ar.recipe_name AS recipe_name
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

query3_old = """SELECT 	DISTINCT fr.recipe_id
FROM 	RECOMMEND_BY_AGE_GENDER as rbag,
		FOOD_RECIPES as fr,
		ALL_RECIPES as ar
WHERE
		rbag.gender = \"<GENDER>\" AND
		rbag.age = <AGE> AND
		fr.recipe_id = ar.recipe_id AND
		MATCH(fr.course) AGAINST(\"<MEAL_OPTION>\")  """


inner_query_for_query1_2_old = """<AND> ar.recipe_id IN (
SELECT 	DISTINCT rw.recipe_id as recipe_id
FROM 	RECIPE_NUTRITIONS_WEIGHTS as rnw,
		RECIPE_WEIGHTS as rw,
		NUTRITIONS as n
WHERE
		rw.recipe_id = rnw.recipe_id AND
		rnw.nutrition_id = n.nutrition_id AND
		n.nutrition_name = \"<NUT_KEY>\" AND
		rnw.weight / rw.weight <NUT_IF>
)"""

weights_view_old= """CREATE VIEW RECIPE_WEIGHTS AS
SELECT DISTINCT ar.recipe_id as recipe_id, SUM(st.tot_weight) as weight
FROM 	ALL_RECIPES          as ar, 
		INGREDIENTS          as i, 
		RECIPE2INGREDIENTS   as r2i,
		(
			SELECT DISTINCT (r2i.servings * i.serving_weight) as tot_weight, ar.recipe_id as recipe_id
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
	ar.recipe_id"""

weights_view_old2 = """CREATE VIEW RECIPE_WEIGHTS AS
SELECT DISTINCT SUM(r2i.servings * i.serving_weight_grams) as tot_weight, r2i.recipe_id as recipe_id
FROM 		RECIPE2INGREDIENTS r2i
INNER JOIN 	INGREDIENTS i on i.ingredient_id = r2i.ingredient_id
GROUP BY r2i.recipe_id"""

recipe_nutritions_view_old2 = """CREATE VIEW RECIPE_NUTRITIONS_WEIGHTS AS
SELECT DISTINCT r2i.recipe_id as recipe_id, inn.nutrition_id as nutrition_id, SUM(r2i.servings * inn.weight_mg_from_ingredient) as weight
FROM		RECIPE2INGREDIENTS r2i 
INNER JOIN 	INGREDIENT_NUTRITION inn on inn.ingredient_id = r2i.ingredient_id
GROUP BY r2i.recipe_id, inn.nutrition_id"""

recipe_nutritions_view_old = """CREATE VIEW RECIPE_NUTRITIONS_WEIGHTS AS
SELECT DISTINCT ar.recipe_id as recipe_id, inn.nutrition_id as nutrition_id, SUM(r2i.servings * inn.weight_mg) as weight
FROM	ALL_RECIPES as ar,
		RECIPE2INGREDIENTS as r2i,
		INGREDIENT_NUTRITION as inn
WHERE
	ar.recipe_id = r2i.recipe_id AND
	inn.ingredient_id = r2i.ingredient_id
GROUP BY
	ar.recipe_id, inn.nutrition_id"""

daily_meals_view_old = """CREATE VIEW DAILY_MEALS AS
SELECT 	DISTINCT breakfast_r.recipe_id AS breakfast_id, lunch_r.recipe_id AS lunch_id, dinner_r.recipe_id AS dinner_id
FROM	( SELECT DISTINCT recipe_id FROM ALL_RECIPES where MATCH(course) AGAINST("Breakfast and Brunch") as breakfast_r
		( SELECT DISTINCT recipe_id FROM ALL_RECIPES where MATCH(course) AGAINST("Lunch") as lunch_r
		( SELECT DISTINCT recipe_id FROM ALL_RECIPES where MATCH(course) AGAINST("Main Dishes") as dinner_r"""


ineffective_inner_query_for_query3 = """AND ar.recipe_id in  (
	SELECT DISTINCT ar.recipe_id as recipe_id 
	FROM ALL_RECIPES ar inner join RECIPE_NUTRITIONS_WEIGHTS rnw on ar.recipe_id = rnw.recipe_id
		inner join RECOMMEND_BY_AGE_GENDER rbag on rbag.nutrition_id = rnw.nutrition_id,
		NUTRITIONS as n
	WHERE
		n.nutrition_name = <NUT_KEY> AND
		rnw.weight / rbag.weight_mg <NUT_IF>
)"""

inner_query_for_query4_old = """AND dm.breakfast_id, dm.lunch_id, dm.dinner_id IN (
	SELECT DISTINCT dm2.breakfast_id, dm2.lunch_id, dm2.dinner_id
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
)"""


#### I think this should be a view - there are 2 huge views and in mysql you can't index views #### -GUY (this one is faster than query1)
inner_query_for_query1_2_no_if = """<AND> ar.recipe_id IN (
SELECT DISTINCT rw.recipe_id as recipe_id
FROM 		RECIPE_WEIGHTS rw
INNER JOIN	RECIPE_NUTRITIONS_WEIGHTS rnw on rw.recipe_id = rnw.recipe_id
INNER JOIN	NUTRITIONS n on rnw.nutrition_id = n.nutrition_id
WHERE
		n.nutrition_name = \"<NUT_KEY>\" AND
		rnw.weight / rw.weight <NUT_IF>
)"""

inner_query_for_query1_2_old_views = """
<AND> 	(n.nutrition_name <> \"<NUT_KEY>\" OR rnw.weight / rw.weight <NUT_IF>)"""

# food recipes by nutritional values
query1_no_if = """SELECT DISTINCT ar.recipe_name
FROM		ALL_RECIPES ar
INNER JOIN 	FOOD_RECIPES fr on ar.recipe_id = fr.recipe_id
WHERE
	MATCH(fr.course) AGAINST(\"<MEAL_OPTION>\")  """

#### I think this should be a view - there are 2 huge views and in mysql you can't index views #### -GUY
query1_old3 = """SELECT DISTINCT ar.recipe_name
FROM		ALL_RECIPES ar
INNER JOIN	VIEW_RECIPE_NUTRITIONS_WEIGHTS vrnw on ar.recipe_id = vrnw.recipe_id
INNER JOIN	NUTRITIONS n on vrnw.nutrition_id = n.nutrition_id
INNER JOIN 	FOOD_RECIPES fr on ar.recipe_id = fr.recipe_id
WHERE
	MATCH(fr.course) AGAINST(\"<MEAL_OPTION>\")  """

inner_query_for_query3_old_views = """AND fr.recipe_id in  (
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
)"""

def get_query2_old(nutritions_values):
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

			if nut == "calories_kcal":
				if nutritions_values[nut] != "d":

					if first:
						nline = re.sub("<AND>", "", nline, re.MULTILINE)
						first = False
					else:
						nline = re.sub("<AND>", "AND", nline, re.MULTILINE)

					nline = re.sub("vrnw.precentage <NUT_IF>", "rnw.weight <= " + nutritions_values[nut], nline, re.MULTILINE)
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
						return ""
	return q

query3_old = """SELECT DISTINCT fr.recipe_id
FROM 	RECOMMEND_BY_AGE_GENDER as rbag,
		FOOD_RECIPES as fr
WHERE
		rbag.gender = \"<GENDER>\" AND
		rbag.age = <AGE> AND
		MATCH(fr.course) AGAINST(\"<MEAL_OPTION>\") """


inner_query_for_query3_old = """AND fr.recipe_id in  (
	SELECT DISTINCT ar.recipe_id as recipe_id 
	FROM 		ALL_RECIPES ar 
	INNER JOIN 	VIEW_RECIPE_NUTRITIONS_WEIGHTS vrnw on ar.recipe_id = rnw.recipe_id
	INNER JOIN 	RECOMMEND_BY_AGE_GENDER rbag on rbag.nutrition_id = vrnw.nutrition_id
	INNER JOIN NUTRITIONS n
	WHERE
		n.nutrition_name = \"<NUT_KEY>\" AND
		(
			(
				n.max_or_min = \"min\" AND
				vrnw.weight / rbag.weight_mg >= <NUT_VAL>
			)
			OR
			(
				n.max_or_min = \"max\" AND
				vrnw.weight / rbag.weight_mg <= <NUT_VAL>
			)
		)
)"""

# all day recipes by daily values
query4_old = """SELECT DISTINCT *
FROM VIEW_DAILY_MEALS as vdm
<WHERE>"""

### Need to check this only after fixing the DAILY_MEALS ### - GUY
inner_query_for_query4_old = """<AND> vdm.breakfast_id, vdm.lunch_id, vdm.dinner_id IN (
	SELECT DISTINCT vdm2.breakfast_id, vdm2.lunch_id, vdm2.dinner_id
	FROM 		VIEW_DAILY_MEALS vdm2 	
	INNER JOIN	VIEW_RECIPE_NUTRITIONS_WEIGHTS vrnw_b on vrnw_b.recipe_id = vdm2.breakfast_id
	INNER JOIN	VIEW_RECIPE_NUTRITIONS_WEIGHTS vrnw_l on vrnw_l.recipe_id = vdm2.lunch_id
	INNER JOIN	VIEW_RECIPE_NUTRITIONS_WEIGHTS vrnw_d on vrnw_d.recipe_id = vdm2.dinner_id,
	RECOMMEND_BY_AGE_GENDER rbag 
	INNER JOIN NUTRITIONS n on rbag.nutrition_id = n.nutrition_id
	WHERE
		rbag.age = <AGE> AND
		rbag.gender = "<GENDER>" AND
		n.nutrition_name = "<NUT_KEY>" AND
		(
			(
			n.max_or_min = "min" AND
			(vrnw_b.weight + vrnw_l.weight + vrnw_d.weight) / rbag.weight_mg >= <NUT_IF>
			)
			OR
			(
			n.max_or_min = "max" AND
			(vrnw_b.weight + vrnw_l.weight + vrnw_d.weight) / rbag.weight_mg <= <NUT_IF>
			)
		)
)"""

def get_query4_old(nutritions_values, age, gender):
	# If it's FullDay then need to use query #4

	q = query4

	where_to_empty = True
	first = True
	for nut in NUTRITIONS:
		if nut == "alcohol":
			continue

		if nutritions_values[nut] != "" and nutritions_values[nut] != "Don't Care" and nutritions_values[nut] != "d":
			where_to_empty = False
			nline = inner_query_for_query4

			q = re.sub("<WHERE>", "WHERE", q)

			nline = re.sub("<GENDER>", gender, nline, re.MULTILINE)
			nline = re.sub("<AGE>", age, nline, re.MULTILINE)

			if first:
				nline = re.sub("<AND>", "", nline)
				first = False
			else:
				nline = re.sub("<AND>", "AND", nline)

			nline = re.sub("<NUT_KEY>", nut, nline)
			try:
				val = float(nutritions_values[nut]) / float(100)
			except:
				val = nutritions_values[nut]
				print "ERROR: expected int value, but got:", val
				return ""

			nline = re.sub("<NUT_IF>", str(val), nline, re.MULTILINE)

			q += nline

	if where_to_empty:
		q = re.sub("<WHERE>", "", q)

	return q

daily_meals_view_old = """CREATE VIEW VIEW_DAILY_MEALS AS
SELECT DISTINCT breakfast_r.recipe_id AS breakfast_id, lunch_r.recipe_id AS lunch_id, dinner_r.recipe_id AS dinner_id
FROM	( SELECT DISTINCT recipe_id FROM FOOD_RECIPES where MATCH(course) AGAINST("Breakfast and Brunch") as breakfast_r,
		( SELECT DISTINCT recipe_id FROM FOOD_RECIPES where MATCH(course) AGAINST("Lunch") as lunch_r,
		( SELECT DISTINCT recipe_id FROM FOOD_RECIPES where MATCH(course) AGAINST("Main Dishes") as dinner_r
ORDER BY RAND()
limit 30000"""

trivia_3_by_recommended_day_intake = """
SELECT * 
FROM 		RECOMMEND_BY_AGE_GENDER rbag 
INNER JOIN 	NUTRITIONS n on rbag.nutrition_id = rbag.nutrition_id
INNER JOIN 	VIEW_RECIPE_NUTRITIONS_WEIGHTS vrnw on n.nutrition_id = vrnw.nutrition_id
WHERE
rbag.age = <AGE> AND 
rbag.gender = <GENDER> AND 
n.nutrition_name = <NUT_KEY> AND
vrnw.weight / rbag.weight_mg > <RANDOM_NUM>
"""


trivia3_take_two = """
SELECT *
FROM 		RECIPE2INGREDIENTS r2i
INNER JOIN 	INGREDIENT_NUTRITION inn on r2i.ingredient_id = inn.ingredient_id
INNER JOIN 	NUTRITIONS n on n.nutrition_id = inn.nutrition_id
			RECOMMEND_BY_AGE_GENDER as rbag
WHERE
(
	n.nutrition_name = "<NUTRITION_NAME>"
	AND
	(	i.ingrdient_name = "<INGREDIENT_1>" OR 
		i.ingrdient_name = "<INGREDIENT_2>" OR 
		i.ingrdient_name = "<INGREDIENT_3>" OR 
		i.ingrdient_name = "<INGREDIENT_4>" 
	)
	AND
	rbag.age = <AGE> AND rbag.gender = <GENDER>
	AND
	inn.weight_mg_from_ingredient / rbag.weight_mg > <PERCENTAGE>
)
GROUP BY r2i.ingredient_id
HAVING COUNT(r2i.recipe_id) >= ALL (
	SELECT count(r2i2.recipe_id)
	FROM RECIPE2INGREDIENTS r2i2
	INNER JOIN INGREDIENTS i2 on r2i2.ingredient_id = i2.ingredient_id
	WHERE
	(
		i2.ingrdient_name = "<INGREDIENT_1>" OR 
		i2.ingrdient_name = "<INGREDIENT_2>" OR 
		i2.ingrdient_name = "<INGREDIENT_3>" OR 
		i2.ingrdient_name = "<INGREDIENT_4>"
	)
	GROUP BY r2i2.ingredient_id
)
"""

def get_query5_old(allergans, option):
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