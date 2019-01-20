#!/usr/bin/env python
import re
from utils import *

################################
############ VIEWS #############
################################

# This view maps the recipes to their weights
weights_view = """CREATE VIEW VIEW_RECIPE_WEIGHTS AS
SELECT DISTINCT ROUND(SUM(r2i.servings * i.serving_weight_grams),2) as weight, r2i.recipe_id as recipe_id
FROM 		INGREDIENTS i
INNER JOIN RECIPE2INGREDIENTS r2i on i.ingredient_id = r2i.ingredient_id
GROUP BY r2i.recipe_id"""

# This view maps the recipes to all of their nutritions weights 
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
FROM		NUTRITIONS n
INNER JOIN 	INGREDIENT_NUTRITION inn on n.nutrition_id = inn.nutrition_id
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

# To filter the specific nutritions
FILTER_BY_NUTRITIONS_for_query1_2 = "MATCH(n.nutrition_name) AGAINST(\"<NUT_KEY>\")"

# If the nutrition name is <NUT_KEY> then the precentage should apply the <NUT_IF>
NUTRITIONS_CHECK_for_query1_2 = """AND	(NOT MATCH(n.nutrition_name) AGAINST(\"<NUT_KEY>\") OR vrnw.precentage <NUT_IF>)"""

# The check of the preperation time (not always checked)
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
FROM 		NUTRITIONS n
INNER JOIN  RECOMMEND_BY_AGE_GENDER rbag on n.nutrition_id = rbag.nutrition_id
INNER JOIN 	VIEW_RECIPE_NUTRITIONS_WEIGHTS vrnw on rbag.nutrition_id = vrnw.nutrition_id
INNER JOIN 	FOOD_RECIPES fr on fr.recipe_id = vrnw.recipe_id
WHERE
rbag.is_female = <GENDER> AND
rbag.age = <AGE> AND
MATCH(fr.course) AGAINST(\"<MEAL_OPTION>\") 
<FILTER_BY_NUTRITIONS>
<NUTRITIONS_CHECK>
GROUP by fr.recipe_id
) RECIPE_COUNTERS on RECIPE_COUNTERS.recipe_id = fr.recipe_id
WHERE RECIPE_COUNTERS.cnt = <NUT_NUM>"""

# To get the specific nutrition
FILTER_BY_NUTRITIONS_for_query3_4 = "MATCH(n.nutrition_name) AGAINST(\"<NUT_KEY>\")"

# To check that if it's the nutrition_name then it should apply the <NUT_VAL>
NUTRITIONS_CHECK_for_query3_4 = """AND	(NOT MATCH(n.nutrition_name) AGAINST(\"<NUT_KEY>\") OR 
		(
			(
				n.is_max = 0 AND
				vrnw.weight / rbag.weight_mg >= <NUT_VAL>
			)
			OR
			(
				n.is_max = 1 AND
				vrnw.weight / rbag.weight_mg <= <NUT_VAL>
			)
		)
	)"""

# A function that receives meal option, age, gender and nutritional values, and returns the query
# for food recipes by daily values.
def get_query3(nutritions_values, meal_option, age, gender):


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

# The query for getting food or cocktail recipes according to unwanted ingredients
allergies_query = """SELECT DISTINCT ar.recipe_id AS recipe_id, ar.recipe_name AS recipe_name
FROM 		ALL_RECIPES AS ar 
INNER JOIN	<FOOD_DRINK>
WHERE
		<FOOD_DRINK_FIELDS>
		<ALG_QUERY_1>
		<ALG_QUERY_2>
		<ALG_QUERY_3>
GROUP BY
		ar.recipe_id"""

alg_query = """<AND> ar.recipe_id NOT IN (
	SELECT DISTINCT r2i.recipe_id
	FROM		INGREDIENTS ing 
	INNER JOIN 	RECIPE2INGREDIENTS r2i on r2i.ingredient_id = ing.ingredient_id
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
		query = re.sub("<FOOD_DRINK>", "COCKTAIL_RECIPES cr on ar.recipe_id = cr.recipe_id", allergies_query, re.MULTILINE)
		first = True
		query = re.sub("<FOOD_DRINK_FIELDS>", "", query, re.MULTILINE)
	else:
		query = re.sub("<FOOD_DRINK>", "FOOD_RECIPES fr on ar.recipe_id = fr.recipe_id", allergies_query, re.MULTILINE)
		my_food_fields = re.sub("<MEAL_OPTION>", option, food_fields, re.MULTILINE)
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

	query = re.sub("<ALG_QUERY_1>", algqueries[0], query, re.MULTILINE)
	query = re.sub("<ALG_QUERY_2>", algqueries[1], query, re.MULTILINE)
	query = re.sub("<ALG_QUERY_3>", algqueries[2], query, re.MULTILINE)

	return query

################################
###########  TRIVIA1 ###########
################################

# Query to get the maximum nutrition inside the specified <RECIPE_ID>
trivia_1_get_max_nutrition = """
SELECT DISTINCT n.nutrition_id, n.nutrition_name
FROM NUTRITIONS n
INNER JOIN
(
	SELECT DISTINCT r2i.recipe_id as recipe_id, inn.nutrition_id as nutrition_id, SUM(r2i.servings * inn.weight_mg_from_ingredient) as weight
	FROM		INGREDIENT_NUTRITION inn 
	INNER JOIN 	RECIPE2INGREDIENTS r2i on inn.ingredient_id = r2i.ingredient_id
	WHERE		r2i.recipe_id = <RECIPE_ID>
	GROUP BY r2i.recipe_id, inn.nutrition_id
) vrnw on n.nutrition_id = vrnw.nutrition_id
INNER JOIN(
			SELECT DISTINCT v.recipe_id, MAX(v.weight) as max_weight
			FROM (SELECT DISTINCT r2i.recipe_id as recipe_id, inn.nutrition_id as nutrition_id, SUM(r2i.servings * inn.weight_mg_from_ingredient) as weight
				FROM		INGREDIENT_NUTRITION inn 
				INNER JOIN 	RECIPE2INGREDIENTS r2i on inn.ingredient_id = r2i.ingredient_id
				WHERE		r2i.recipe_id = <RECIPE_ID>
				GROUP BY r2i.recipe_id, inn.nutrition_id) AS v
			GROUP BY v.recipe_id 
) max_nut_table on vrnw.weight = max_nut_table.max_weight
"""

# Query to get a random recipe
trivia_1_get_random_recipe = """
SELECT DISTINCT recipe_id, recipe_name from ALL_RECIPES order by rand() limit 1
"""

# Query to get 3 random nutritions which are different than <ANS_NUTRITION_ID>
trivia_1_get_random_nutritions = """
SELECT DISTINCT nutrition_id, nutrition_name
FROM NUTRITIONS
WHERE nutrition_id <> <ANS_NUTRITION_ID>
order by rand()
Limit 3
"""

# Gets the trivia1 query - changes the <RECIPE_ID> with the given recipe_id
def get_query_trivia_1(recipe_id):
	return re.sub("<RECIPE_ID>", str(recipe_id), trivia_1_get_max_nutrition, re.MULTILINE)

# Gets the query of 3 random nutritions other than nutiriton_id
def get_query_trivia_1_random_nutritions(nutrition_id):
	return re.sub("<ANS_NUTRITION_ID>", str(nutrition_id), trivia_1_get_random_nutritions, re.MULTILINE)

################################
###########  TRIVIA2 ###########
################################

# For the chosen 4 recipes, and nutrition, gets the recipe which has the max value of this nutrition.
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
	FROM		INGREDIENT_NUTRITION inn 
	INNER JOIN 	RECIPE2INGREDIENTS r2i on inn.ingredient_id = r2i.ingredient_id
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

# Gets a random nutrition
trivia_2_get_random_nutrition = """
SELECT DISTINCT nutrition_id, nutrition_name FROM NUTRITIONS ORDER BY RAND() LIMIT 1
"""

# Gets 4 random recipes
trivia_2_get_random_recipes = """
SELECT DISTINCT recipe_id, recipe_name
FROM ALL_RECIPES
order by rand()
Limit 4
"""

# gets query for trivia2 changes the recipes and the ingredients
def get_query_trivia_2(recipe_id1, recipe_id2, recipe_id3 ,recipe_id4, nutrition_id):
	query = re.sub("<RECIPE_ID1>", str(recipe_id1), trivia_2_get_recipe_of_max_nutrition, re.MULTILINE)
	query = re.sub("<RECIPE_ID2>", str(recipe_id2), query, re.MULTILINE)
	query = re.sub("<RECIPE_ID3>", str(recipe_id3), query, re.MULTILINE)
	query = re.sub("<RECIPE_ID4>", str(recipe_id4), query, re.MULTILINE)
	return re.sub("<NUTRITION_ID>", str(nutrition_id), query, re.MULTILINE)

################################
###########  TRIVIA3 ###########
################################

# Gets 4 random ingredients other than <INGREDIENT_ID>
trivia_3_get_random_ingredient = """
SELECT DISTINCT ingredient_id, ingredient_name
FROM INGREDIENTS 
WHERE ingredient_id <> <INGREDIENT_ID>
ORDER BY RAND()
LIMIT 3
"""

# Gets the ingredient, which has <RANDOM_PRECENTAGE> of <NUTRITION_ID> from the daily intake for <AGE>,<GENDER>,
# and appears in most of the recipes having clue - more than <MIN_RECIPES> recipes
trivia3_get_max_ingredient_of_precentage_from_nutrition = """
SELECT DISTINCT i.ingredient_name, i.ingredient_id
FROM INGREDIENTS i
INNER JOIN (
	SELECT r2i.ingredient_id as ingredient_id, count(r2i.recipe_id) as cnt
	FROM 		NUTRITIONS n
	INNER JOIN 	INGREDIENT_NUTRITION inn on n.nutrition_id = inn.nutrition_id
	INNER JOIN  RECOMMEND_BY_AGE_GENDER rbag on rbag.nutrition_id = n.nutrition_id
	INNER JOIN 	RECIPE2INGREDIENTS r2i on r2i.ingredient_id = inn.ingredient_id
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

# gets query trivia3 by replacing to the right parameters
def get_trivia_3(age, gender, nutrition_id, precentage, min_recipes):
	q = trivia3_get_max_ingredient_of_precentage_from_nutrition
	q = re.sub("<NUTRITION_ID>", str(nutrition_id), q, re.MULTILINE)
	q = re.sub("<AGE>", str(age), q, re.MULTILINE)
	q = re.sub("<GENDER>", str(gender), q, re.MULTILINE)
	q = re.sub("<RANDOM_PRECENTAGE>", str(precentage), q, re.MULTILINE)
	q = re.sub("<MIN_RECIPES>", str(min_recipes), q, re.MULTILINE)
	return q

# gets 3 random ingredients other than ingredient_id
def get_query_trivia_3_random_ingredients(ingredient_id):
	return re.sub("<INGREDIENT_ID>", str(ingredient_id), trivia_3_get_random_ingredient)

