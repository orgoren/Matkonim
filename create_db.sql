Drop database if exists DbMysql11;
CREATE SCHEMA IF NOT EXISTS DbMysql11;
USE DbMysql11;


CREATE TABLE DbMysql11.ALL_RECIPES(
	recipe_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  	recipe_name VARCHAR(255) NULL DEFAULT NULL,  
  	picture VARCHAR(255),
  	PRIMARY KEY (recipe_id),
  	INDEX recipe_index (recipe_id ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8mb4;


CREATE TABLE DbMysql11.FOOD_RECIPES(
	recipe_id SMALLINT UNSIGNED NOT NULL,
	food_id INT UNSIGNED NOT NULL,
  	course VARCHAR(20) NOT NULL,
  	prep_time_in_minutes SMALLINT UNSIGNED NOT NULL,
  	food_details VARCHAR(2500) NOT NULL,
  	INDEX food_id (food_id ASC),
	FOREIGN KEY (recipe_id)
  	REFERENCES DbMysql11.ALL_RECIPES (recipe_id)
	ON UPDATE CASCADE) 
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;


CREATE TABLE DbMysql11.COCKTAIL_RECIPES (
	recipe_id SMALLINT UNSIGNED NOT NULL,
  	cocktail_id SMALLINT UNSIGNED NOT NULL,
  	is_alcoholic TINYINT UNSIGNED NOT NULL,
  	cocktail_details VARCHAR(3500) NOT NULL,
	serving_glasss VARCHAR(100) NOT NULL,
  	INDEX cocktail_id (cocktail_id ASC),
	FOREIGN KEY (recipe_id)
  	REFERENCES DbMysql11.ALL_RECIPES (recipe_id))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;


CREATE TABLE DbMysql11.INGREDIENTS (
  	ingredient_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  	ingredient_name VARCHAR(55) NOT NULL,
  	serving_quantity SMALLINT UNSIGNED NOT NULL,
  	serving_unit VARCHAR(55) NOT NULL,
  	serving_weight_grams SMALLINT UNSIGNED NOT NULL,
  	PRIMARY KEY (ingredient_id),
  	INDEX ingredient_id (ingredient_id ASC),
  	FULLTEXT INDEX ingredientName (ingredient_name) )
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8mb4;


CREATE TABLE DbMysql11.RECIPE2INGREDIENTS(
  	recipe_id SMALLINT UNSIGNED NOT NULL,
  	ingredient_id INT UNSIGNED NOT NULL,
  	servings FLOAT(7) UNSIGNED NOT NULL,
  	full_ingredient_line VARCHAR(90) NOT NULL,
  	INDEX (recipe_id),
	FOREIGN KEY (ingredient_id)
  	REFERENCES DbMysql11.INGREDIENTS (ingredient_id)
	ON UPDATE CASCADE,
	FOREIGN KEY (recipe_id)
  	REFERENCES DbMysql11.ALL_RECIPES (recipe_id)
	ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;


CREATE TABLE DbMysql11.INGREDIENT_NUTRITION(
	ingredient_id INT UNSIGNED NOT NULL,
	nutrition_id SMALLINT UNSIGNED NOT NULL,
	weight_mg_from_ingredient Float(3) DEFAULT 0,
   INDEX (ingredient_id),
	FOREIGN KEY (ingredient_id)
	REFERENCES DbMysql11.INGREDIENTS (ingredient_id)
	ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;

CREATE TABLE DbMysql11.NUTRITIONS (
	nutrition_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
	nutrition_name VARCHAR(30) NOT NULL,
	max_or_min VARCHAR(7) NOT NULL,
	PRIMARY KEY (nutrition_id),
	INDEX(nutrition_id))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8mb4;

CREATE TABLE DbMysql11.RECOMMEND_BY_AGE_GENDER(
	gender VARCHAR(7) NOT NULL,
	age TINYINT NOT NULL, -- 0: 14-18, 1:19-30, 2: 31-40, 3: 41-50, 4:51-60, 5:61-70, 6: 71+
	nutrition_id SMALLINT UNSIGNED NOT NULL,
	weight_mg Float(3) DEFAULT 0,
   PRIMARY KEY (gender, age, nutrition_id),
   INDEX (gender, age, nutrition_id),
	FOREIGN KEY (nutrition_id)
  	REFERENCES DbMysql11.NUTRITIONS (nutrition_id)
	ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;


CREATE VIEW RECIPE_WEIGHTS AS
SELECT ar.recipe_id as recipe_id, SUM(st.tot_weight) as weight
FROM 	ALL_RECIPES          as ar, 
		INGREDIENTS          as i, 
		RECIPE2INGREDIENTS   as r2i,
		(
			SELECT (r2i.servings * i.serving_weight_grams) as tot_weight, ar.recipe_id as recipe_id
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
	ar.recipe_id;
	

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
