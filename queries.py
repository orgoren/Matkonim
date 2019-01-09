#!/usr/bin/env python

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
SELECT ar.recipe_name, rnw.nutrition_id
FROM	ALL_RECIPES as ar,
		RECIPE_WEIGHTS as rw,
		FOOD_RECIPES as fr,
		NUTRITIONS as n,
		RECIPE_NUTRITIONS_WEIGHTS as rnw
WHERE
	ar.recipe_id = rw.recipe_id AND
	fr.recipe_id = ar.recipe_id AND
	ar.recipe_id = rnw.recipe_id AND
	n.nutrition_id = rnw.nutrition_id
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
	ar.recipe_id = rnw.recipe_id AND
	<OTHER QUERIES OF THE FORM OF:
		rnw.nutrition_id = {} AND rnw.weight > 0.3 AND
		rnw.nutrition_id = {} AND rnw.weight < 0.05 AND
		rnw.nutrition_id = {} AND rnw.weight = 0
	>
"""

query3 = """
SELECT 	*
FROM 	RECOMMEND_BY_AGE_GENDER as rbag,
		FOOD_RECIPES as fr,
		ALL_RECIPES as ar,
		RECIPE_NUTRITIONS_WEIGHTS as rnw
WHERE
		rbag.gender = {} AND
		rbag.age = {} AND
		fr.recipe_id = ar.recipe_id AND
		ar.recipe_id = rnw.recipe_id AND
		fr.course = {} AND
		(rnw.nutrition_id = {} and ((rnw.bad & rnw.weight <= rbag.weight_mg) or (rnw.good & rnw.weight >= rbag.weight_mg)))
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











