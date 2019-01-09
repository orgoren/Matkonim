#!/usr/bin/env python
import re

FOOD_NUTRITIONS = [	"sugar",   "iron",     "calcium", "sodium", "protein", "cholesterol", "potassium",
					"lactose", "vitaminC", "satfat",  "fiber", "calories"]

VALUES = {"None" : "None", "1" : "None", "d": "dont care", "2" : "less than 5%", "3" : "over 30%"}

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


# food recipes by nutritional values
query1 = """
SELECT ar.recipe_name
FROM	ALL_RECIPES as ar,
		RECIPE_WEIGHTS as rw,
		FOOD_RECIPES as fr,
		RECIPE_NUTRITIONS_WEIGHTS as rnw
WHERE
	ar.recipe_id = rw.recipe_id AND
	fr.recipe_id = ar.recipe_id AND
	ar.recipe_id = rnw.recipe_id AND
	fr.course = \"<MEAL_OPTION>\"
"""

#	<OTHER QUERIES OF THE FORM OF:
#		n.nutrition_name = {} and rnw.nutrition_id = {} and rnw.weight > 0.3 AND
#		rnw.nutrition_id = {} & rnw.weight < 0.05 AND
#		rnw.nutrition_id = {} & rnw.weight = 0
#	>

# cocktails recipes by nutritional values
query2 = """
SELECT ar.recipe_name, rnw.nutrition_id
FROM	ALL_RECIPES as ar,
		RECIPE_WEIGHTS as rw,
		COCKTAIL_RECIPES as cr,
		RECIPE_NUTRITIONS_WEIGHTS as rnw
WHERE
	ar.recipe_id = rw.recipe_id AND
	ar.recipe_id = cr.recipe_id AND
	ar.recipe_id = rnw.recipe_id
"""


query3 = """
SELECT 	*
FROM 	RECOMMEND_BY_AGE_GENDER as rbag,
		FOOD_RECIPES as fr,
		ALL_RECIPES as ar,
		RECIPE_NUTRITIONS_WEIGHTS as rnw
WHERE
		rbag.gender = <GENDER> AND
		rbag.age = <AGE> AND
		fr.recipe_id = ar.recipe_id AND
		ar.recipe_id = rnw.recipe_id AND
		fr.course = <MEAL_OPTION>
"""

query4 = """
SELECT	*
FROM 	RECOMMEND_BY_AGE_GENDER as rbag,
		FOOD_RECIPES as fr,
		ALL_RECIPES as ar,
		RECIPE_NUTRITIONS_WEIGHTS as rnw	 
WHERE	

"""

query5 = """
SELECT 	*
FROM 	ALL_RECIPES as ar,
		FOOD_RECIPES as fr,
		COCKTAIL_RECIPES as cr,
		RECIPE2INGREDIENTS as r2i
WHERE
		ar.recipe_id = r2i.recipe_id
HAVING () 
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

inner_query_for_query3 = """
AND ar.recipe_id in  (
	SELECT ar.recipe_id as recipe_id 
	FROM 	ALL_RECIPES as ar,
			RECOMMEND_BY_AGE_GENDER as rbag,
			RECIPE_NUTRITIONS_WEIGHT as rnw,
			NUTRITIONS as n
	WHERE
		ar.recipe_id = rbag.recipe_id AND
		ar.recipe_id = rnw.recipe_id AND
		rbag.nutrition_id = rnw.nutrition_id AND
		n.nutrition_name = <NUT_KEY> AND
		rnw.weight / rbag.weight <NUT_IF>

)
"""


def get_query1(nutritions_values, meal_option):
	q = re.sub("<MEAL_OPTION>", meal_option, query1, re.MULTILINE)

	for nut in FOOD_NUTRITIONS:
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








