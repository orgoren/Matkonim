Drop database if exists DbMysql11;
CREATE SCHEMA IF NOT EXISTS DbMysql11;
USE DbMysql11;


CREATE TABLE DbMysql11.ALL_RECIPES(
  recipe_id SMALLINT UNSIGNED NOT NULL,
  recipe_name VARCHAR(55) NULL DEFAULT NULL,  
  picture VARCHAR(255),
  PRIMARY KEY (recipe_id),
  INDEX recipe_id (recipe_id ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;


CREATE TABLE DbMysql11.FOOD_RECIPES(
  food_id SMALLINT UNSIGNED NOT NULL,
  recipe_id SMALLINT UNSIGNED NOT NULL,
  prep_time_in_minutes SMALLINT UNSIGNED NOT NULL,
  food_details VARCHAR(2500) NOT NULL,
  INDEX food_id (food_id ASC),
  FOREIGN KEY (recipe_id)
  REFERENCES DbMysql11.ALL_RECIPES (recipe_id)
  ON UPDATE CASCADE) 
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8mb4;


CREATE TABLE DbMysql11.COCKTAIL_RECIPES (
  cocktail_id SMALLINT UNSIGNED NOT NULL,
  recipe_id SMALLINT UNSIGNED NOT NULL,
  is_alcoholic TINYINT UNSIGNED NOT NULL,
  cocktail_details VARCHAR(2500) NOT NULL,
  INDEX cocktail_id (cocktail_id ASC),
  FOREIGN KEY (recipe_id)
  REFERENCES DbMysql11.ALL_RECIPES (recipe_id)
  ON UPDATE CASCADE)
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8mb4;


CREATE TABLE DbMysql11.INGREDIENTS (
  ingredient_id SMALLINT UNSIGNED NOT NULL,
  ingredient_name VARCHAR(55) NOT NULL,
  serving_weight TINYINT UNSIGNED NOT NULL, -- check with carmel if need to change to SMALLINT (up to 65535)
  serving_quantity TINYINT UNSIGNED NOT NULL, -- check with carmel if need to change to SMALLINT (up to 65535)
  serving_unit TINYINT UNSIGNED NOT NULL,  -- check with carmel if need to change to SMALLINT (up to 65535)
  PRIMARY KEY (ingredient_id),
  INDEX ingredient_id (ingredient_id ASC),
  FULLTEXT INDEX ingredient_name (ingredient_name))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;


CREATE TABLE DbMysql11.RECIPE2INGREDIENTS(
  recipe_id SMALLINT UNSIGNED NOT NULL,
  ingredient_id SMALLINT UNSIGNED NOT NULL,
  amount_in_recipe SMALLINT UNSIGNED NOT NULL,
  quantity SMALLINT UNSIGNED NOT NULL,
  unit VARCHAR(20) NOT NULL,
  full_ingredient_line VARCHAR(90) NOT NULL,
  INDEX recipe_id (recipe_id ASC),
  FOREIGN KEY (recipe_id)
  REFERENCES DbMysql11.ALL_RECIPES(recipe_id)
  ON UPDATE CASCADE,
  INDEX ingredient_id (ingredient_id ASC),
  FOREIGN KEY (ingredient_id)
  REFERENCES DbMysql11.INGREDIENTS(ingredient_id)
  ON UPDATE CASCADE)
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8mb4;


CREATE TABLE DbMysql11.INGREDIENT_NUTIRITION (
   ingredient_name VARCHAR(55) NOT NULL,
	ingredient_id SMALLINT UNSIGNED NOT NULL,
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
   PRIMARY KEY (ingredient_name),
   INDEX (ingredient_id, ingredient_name),
   FOREIGN KEY (ingredient_id)
   REFERENCES DbMysql11.INGREDIENTS(ingredient_id)
   ON UPDATE CASCADE)
ENGINE = InnoDB
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
   REFERENCES DbMysql11.INGREDIENT_NUTIRITION(ingredient_name)
   ON UPDATE CASCADE)
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8mb4;

Insert into DbMysql11.ALL_RECIPES
Values (1, "Test", "Test details");

Insert into DbMysql11.FOOD_RECIPES
Values (11, 1, 2300, "FOOD_TEST");
