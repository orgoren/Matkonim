#!/usr/bin/env python
import re
from utils import *
#FOOD_NUTRITIONS = [	"sugar",   "iron",     "calcium", "sodium", "protein", "cholesterol", "potassium",
#					"lactose", "vitaminC", "satfat",  "fiber", "calories"]

#VALUES = {"None" : "None", "1" : "None", "d": "dont care", "2" : "less than 5%", "3" : "over 30%"}

weights_view= """
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

recipe_nutritions_view = """
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


daily_meals_view = """
CREATE VIEW DAILY_MEALS AS
SELECT 	breakfast_r.recipe_id AS breakfast_id, lunch_r.recipe_id AS lunch_id, dinner_r.recipe_id AS dinner_id
FROM	( SELECT recipe_id FROM ALL_RECIPES where course="Breakfast and Brunch") as breakfast_r
		( SELECT recipe_id FROM ALL_RECIPES where course="Lunch") as lunch_r
		( SELECT recipe_id FROM ALL_RECIPES where course="Main Dishes") as dinner_r
"""


#	<OTHER QUERIES OF THE FORM OF:
#		n.nutrition_name = {} and rnw.nutrition_id = {} and rnw.weight > 0.3 AND
#		rnw.nutrition_id = {} & rnw.weight < 0.05 AND
#		rnw.nutrition_id = {} & rnw.weight = 0
#	>

# cocktails recipes by nutritional values
query2 = """
SELECT ar.recipe_name
FROM	ALL_RECIPES as ar,
		RECIPE_WEIGHTS as rw,
		COCKTAIL_RECIPES as cr,
		RECIPE_NUTRITIONS_WEIGHTS as rnw
WHERE
	ar.recipe_id = rw.recipe_id AND
	ar.recipe_id = cr.recipe_id AND
	ar.recipe_id = rnw.recipe_id
"""

# one recipe by daily values
query3 = """
SELECT 	*
FROM 	RECOMMEND_BY_AGE_GENDER as rbag,
		FOOD_RECIPES as fr,
		ALL_RECIPES as ar,
		--RECIPE_NUTRITIONS_WEIGHTS as rnw
WHERE
		rbag.gender = <GENDER> AND
		rbag.age = <AGE> AND
		fr.recipe_id = ar.recipe_id AND
		--ar.recipe_id = rnw.recipe_id AND
		fr.course = <MEAL_OPTION>
"""

# all day recipes by daily values
query4 = """
SELECT	*
FROM 	RECOMMEND_BY_AGE_GENDER as rbag,
		DAILY_MEALS as dm,
WHERE	
		rbag.gender = <GENDER> AND
		rbag.age = <AGE>
"""


ineffective_inner_query_for_query3 = """
AND ar.recipe_id in  (
	SELECT ar.recipe_id as recipe_id 
	FROM 	ALL_RECIPES as ar,
			RECOMMEND_BY_AGE_GENDER as rbag,
			RECIPE_NUTRITIONS_WEIGHT as rnw,
			NUTRITIONS as n
	WHERE
		ar.recipe_id = rnw.recipe_id AND
		rbag.nutrition_id = rnw.nutrition_id AND
		n.nutrition_name = <NUT_KEY> AND
		rnw.weight / rbag.weight <NUT_IF>

)
"""

inner_query_for_query3 = """
AND ar.recipe_id in  (
	SELECT DISTINCT ar.recipe_id as recipe_id 
	FROM 		ALL_RECIPES ar 
	INNER JOIN 	RECIPE_NUTRITIONS_WEIGHTS rnw 
				on ar.recipe_id = rnw.recipe_id
	INNER JOIN 	RECOMMEND_BY_AGE_GENDER rbag 
				on rbag.nutrition_id = rnw.nutrition_id
	JOIN NUTRITIONS n
	WHERE
		n.nutrition_name = \"<NUT_KEY>\" AND
		rnw.weight / rbag.weight <NUT_IF>
)
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
		(rnw_b.weight + rnw_l.weight + rnw_d.weight / rbag.weight_mg) <= <NUT_VAL>
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

inner_query_for_query1 = """
AND ar.recipe_id IN (
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

def get_query1(nutritions_values, meal_option, is_food=True):
	q = re.sub("<MEAL_OPTION>", meal_option, query1, re.MULTILINE)

	for nut in NUTRITIONS:
		if is_food and nut == "alcohol":
			continue

		if nutritions_values[nut] != "":
			nline = inner_query_for_query1
			nline = re.sub("<NUT_KEY>", nut, nline)

			if nut == "calories":
				if nutritions_values[nut] != "d":
					nline = re.sub("<NUT_IF>", "rnw.weight <= " + nutritions_values[nut], nline, re.MULTILINE)
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
########### QUERY 5 ############
################################

allergies_query = """

SELECT DISTINCT ar.recipe_id AS recipe_id, ar.recipe_name AS recipe_name
FROM 
		ALL_RECIPES AS ar,
		RECIPE2INGREDIENTS AS r2i,
WHERE
		ar.recipe_id = r2i.recipe_id
		<ALG_QUERY_1>
		<ALG_QUERY_2>
		<ALG_QUERY_3>
GROUP BY
		recipe_id
"""

alg_query = """
AND recipe_id NOT IN (
	SELECT r2i.recipe_id
	FROM
			RECIPE2INGREDIENTS AS r2i,
			INGREDIENTS AS ing
	WHERE
			r2i.ingredient_id = ing.ingredient_id AND
			ing.ingredient_name LIKE "%<ALG>%"
)
"""


def get_query5(alg1, alg2, alg3):
	if alg1 != "":
		alg_query1 = re.sub("<ALG>", alg1, alg_query, re.MULTILINE)
	else:
		alg_query1 = ""

	if alg2 != "":
		alg_query2 = re.sub("<ALG>", alg2, alg_query, re.MULTILINE)
	else:
		alg_query2 = ""

	if alg3 != "":
		alg_query3 = re.sub("<ALG>", alg3, alg_query, re.MULTILINE)
	else:
		alg_query3 = ""

	query = re.sub("<ALG_QUERY_1>", alg_query1, allergies_query, re.MULTILINE)
	query = re.sub("<ALG_QUERY_2>", alg_query2, query, re.MULTILINE)
	query = re.sub("<ALG_QUERY_3>", alg_query3, query, re.MULTILINE)

	return query