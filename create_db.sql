Drop database if exists DbMysql11;
CREATE SCHEMA IF NOT EXISTS DbMysql11;
USE DbMysql11;

-- DROP TABLE ALL_RECIPES
CREATE TABLE DbMysql11.ALL_RECIPES(
  recipe_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  recipe_name VARCHAR(255) NULL DEFAULT NULL,  
  picture VARCHAR(255),
  PRIMARY KEY (recipe_id),
  INDEX recipe_index_ar (recipe_id ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8mb4;

-- DROP TABLE FOOD_RECIPES
CREATE TABLE DbMysql11.FOOD_RECIPES(
  recipe_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  food_id INT UNSIGNED NOT NULL,
  course VARCHAR(27) NOT NULL,
  prep_time_in_minutes SMALLINT UNSIGNED NOT NULL,
  food_details VARCHAR(2500) NOT NULL,
  PRIMARY KEY (recipe_id, food_id),
  INDEX food_id (food_id ASC),
  INDEX recipe_id_index_food_rec (recipe_id ASC),
  INDEX course (course)) 
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8mb4;

-- DROP TABLE COCKTAIL_RECIPES
CREATE TABLE DbMysql11.COCKTAIL_RECIPES (
  recipe_id SMALLINT UNSIGNED NOT NULL,
    cocktail_id SMALLINT UNSIGNED NOT NULL,
    is_alcoholic TINYINT UNSIGNED NOT NULL,
    cocktail_details VARCHAR(3500) NOT NULL,
  serving_glass VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (cocktail_id),
    INDEX cocktail_id (cocktail_id ASC),
  INDEX recipe_id_index_cocktail (recipe_id ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;

-- DROP TABLE DbMysql11.INGREDIENTS
CREATE TABLE DbMysql11.INGREDIENTS (
    ingredient_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    ingredient_name VARCHAR(55) NOT NULL,
    serving_quantity SMALLINT UNSIGNED NOT NULL,
    serving_unit VARCHAR(55) NOT NULL,
    serving_weight_grams SMALLINT UNSIGNED NOT NULL,
    PRIMARY KEY (ingredient_id),
    INDEX ingredient_id (ingredient_id ASC),
    FULLTEXT INDEX ingredient_name_index (ingredient_name) )
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8mb4;

-- DROP TABLE RECIPE2INGREDIENTS
CREATE TABLE DbMysql11.RECIPE2INGREDIENTS(
    recipe_id SMALLINT UNSIGNED NOT NULL,
    ingredient_id INT UNSIGNED NOT NULL,
    servings FLOAT(7) UNSIGNED NOT NULL,
    full_ingredient_line VARCHAR(2500) NOT NULL,
    INDEX recipe_id (recipe_id ASC),
   INDEX ingredient_id_rec2ing (ingredient_id ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;


-- DROP TABLE DbMysql11.INGREDIENT_NUTRITION
CREATE TABLE DbMysql11.INGREDIENT_NUTRITION(
  ingredient_id INT UNSIGNED NOT NULL,
  nutrition_id SMALLINT UNSIGNED NOT NULL,
  weight_mg_from_ingredient Float(3) DEFAULT 0,
  PRIMARY KEY (ingredient_id, nutrition_id),
  INDEX ingredient_id_ingred_nutr (ingredient_id ASC),
  FOREIGN KEY (ingredient_id)
  REFERENCES DbMysql11.INGREDIENTS (ingredient_id)
  ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;

-- DROP TABLE NUTRITIONS
CREATE TABLE DbMysql11.NUTRITIONS (
  nutrition_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  nutrition_name VARCHAR(30) NOT NULL,
  max_or_min VARCHAR(7) NOT NULL,
  PRIMARY KEY (nutrition_id),
  INDEX nut_id_index (nutrition_id ASC),
  INDEX nut_name_index (nutrition_name))
ENGINE = InnoDB
AUTO_INCREMENT = 1
DEFAULT CHARACTER SET = utf8mb4;


-- DROP TABLE RECOMMEND_BY_AGE_GENDER
CREATE TABLE DbMysql11.RECOMMEND_BY_AGE_GENDER(
  gender VARCHAR(7) NOT NULL,
  age TINYINT NOT NULL, -- 0: 14-18, 1:19-30, 2: 31-40, 3: 41-50, 4:51-60, 5:61-70, 6: 71+
  nutrition_id SMALLINT UNSIGNED NOT NULL,
  weight_mg Float(3) DEFAULT 0,
  PRIMARY KEY (gender, age, nutrition_id),
  INDEX nut_id_index_recom_gender_age (nutrition_id),
  INDEX (gender, age),
  INDEX weight_mg_index_recom_gender_age (weight_mg ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;