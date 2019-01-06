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
	recipe_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  	food_id INT UNSIGNED NOT NULL,
  	prep_time_in_minutes SMALLINT UNSIGNED NOT NULL,
  	food_details VARCHAR(2500) NOT NULL,
  	INDEX food_id (food_id ASC),
	FOREIGN KEY (recipe_id)
  	REFERENCES DbMysql11.ALL_RECIPES (recipe_id)
	ON UPDATE CASCADE) 
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8mb4;


CREATE TABLE DbMysql11.COCKTAIL_RECIPES (
	recipe_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  	cocktail_id SMALLINT UNSIGNED NOT NULL,
  	is_alcoholic TINYINT UNSIGNED NOT NULL,
  	cocktail_details VARCHAR(3500) NOT NULL,
  	INDEX cocktail_id (cocktail_id ASC),
	FOREIGN KEY (recipe_id)
  	REFERENCES DbMysql11.ALL_RECIPES (recipe_id))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8mb4;


CREATE TABLE DbMysql11.INGREDIENTS (
  	ingredient_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  	ingredient_name VARCHAR(55) NOT NULL,
  	serving_quantity TINYINT UNSIGNED NOT NULL,
  	serving_unit VARCHAR(15) NOT NULL,
  	serving_weight TINYINT UNSIGNED NOT NULL,
  	PRIMARY KEY (ingredient_id),
  	INDEX ingredient_id (ingredient_id ASC),
  	FULLTEXT INDEX ingredientName (ingredient_name) )
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8mb4;


CREATE TABLE DbMysql11.RECIPE2INGREDIENTS(
  	recipe_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  	ingredient_id SMALLINT UNSIGNED NOT NULL,
	ingredient_name VARCHAR(55) NOT NULL,
  	serving FLOAT(7) UNSIGNED NOT NULL,
  	full_ingredient_line VARCHAR(90) NOT NULL,
  	PRIMARY KEY (recipe_id, ingredient_id),
  	INDEX (recipe_id, ingredient_id),
	FOREIGN KEY (ingredient_id)
  	REFERENCES DbMysql11.INGREDIENTS (ingredient_id)
	ON UPDATE CASCADE,
	FOREIGN KEY (recipe_id)
  	REFERENCES DbMysql11.ALL_RECIPES (recipe_id)
	ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8mb4;


CREATE TABLE DbMysql11.INGREDIENT_NUTRITION (
	ingredient_name VARCHAR(55) NOT NULL,
	ingredient_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
	suger_mg Float(3) DEFAULT 0,
	iron_mg Float(3) DEFAULT 0,
	calcium_mg Float(3) DEFAULT 0,
	sodium_mg Float(3) DEFAULT 0,
	protein_mg Float(3) DEFAULT 0,
	cholesterol_mg Float(3) DEFAULT 0,
	potassium_mg Float(3) DEFAULT 0,
	lactose_mg Float(3) DEFAULT 0,
	vitamin_C_mg Float(3) DEFAULT 0,
	staurated_fat_mg Float(3) DEFAULT 0,
	trans_fat_mg Float(3) DEFAULT 0,
	dietary_fiber_mg Float(3) DEFAULT 0,
	calories_kcal Float(3) DEFAULT 0,
	alcohol_mg Float(3) DEFAULT 0,
	magnesium_mg Float(3) DEFAULT 0,
	zinc_mg Float(3) DEFAULT 0,
   PRIMARY KEY (ingredient_name),
   INDEX (ingredient_id),
	FOREIGN KEY (ingredient_id)
	REFERENCES DbMysql11.INGREDIENTS (ingredient_id)
	ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8mb4;


CREATE TABLE DbMysql11.RECOMMEND_BY_AGE_GENDER(
	age TINYINT NOT NULL,
	gender BIT NOT NULL, -- 1 for Female, 0 for Male
   ingredient_name VARCHAR(55) NOT NULL,
	sugars Float(3) DEFAULT 0,
	iron Float(3) DEFAULT 0,
	calcium Float(3) DEFAULT 0,
	sodium Float(3) DEFAULT 0,
	protein Float(3) DEFAULT 0,
	cholesterol Float(3) DEFAULT 0,
	potassium Float(3) DEFAULT 0,
	lactose Float(3) DEFAULT 0,
	vitaminC Float(3) DEFAULT 0,
	saturated_fat Float(3) DEFAULT 0,
	trans_fat Float(3) DEFAULT 0,
	dietary_fiber Float(3) DEFAULT 0,
	calories Float(3) DEFAULT 0,
	fat Float(3) DEFAULT 0,
	alcoholic Float(3) DEFAULT 0,
   PRIMARY KEY (age, gender),
   INDEX (age, gender),
	FOREIGN KEY (ingredient_name)
  	REFERENCES DbMysql11.INGREDIENT_NUTRITION (ingredient_name)
	ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;
