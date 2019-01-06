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

query1 = """
SELECT ar.recipe_name, rnw.nutrition_id
FROM	ALL_RECIPES as ar,
		RECIPE_WEIGHTS as rw,
		RECIPE_NUTRITIONS_WEIGHTS as rnw
WHERE
	ar.recipe_id = rw.recipe_id AND
	ar.recipe_id = rnw.recipe_id AND
	rnw.nutrition_id = {} AND
	rnw.weight / rw.weight <= 0.05 AND
	rnw.nutrition_id = {} AND
	rnw.weight / rw.weight >- 0.3 AND
		rnw.nutrition_id = {} AND
	rnw.weight = 0


"""