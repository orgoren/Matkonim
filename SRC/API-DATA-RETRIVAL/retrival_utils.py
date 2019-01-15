from fractions import Fraction
import re
import unicodedata
import json
import csv

INGREDIENTS_CSV_FILE = 'ingredients.csv'
INGREDIENTS_JSON_FILE = 'ingredients_details.json'
RECIPES_CSV_FILE = 'recipes.csv'
COCKTAILS_CSV_FILE = 'cocktails.csv'
FIXED_RECIPES_CSV_FILE = 'recipes_fixed.csv'
FIXED_COCKTAILS_CSV_FILE = 'cocktails_fixed.csv'


unicode_fractions = {u'\xbd': u' 1/2', u'\xbc': u' 1/4', u'\u2153': u' 1/3', u'\u2154': u' 2/3'}

possible_units = [u'oz', u'floz', u'ml', u'dl', u'cl', u'kg', u'gram', u'lbs', u'l', u'cups', u'cans', u'tsp', u'tbsp',
                  u'pounds', u'bottles', u'cloves', u'jiggers', u'slices', u'pints', u'glasses', u'gal', u'parts',
                  u'handfuls', u'wedges', u'packages', u'boxes', u'dashes', u'chunks', u'pieces', u'drops', u'shots',
                  u'strips', u'leaves', u'springs', u'quarts', u'sticks', u'twists', u'splashes', u'scoops', u'jars',
                  u'measures', u'cubes', u'pinches', u'tubes', u'cobs', u'containers', u'loaves', u'bunches', u'heads',
                  u'roots', u'patties', u'bundles', u'ears', u'bags', u'packs', u'packets', u'sleeves', u'sheets',
                  u'sprigs', u'cartons', u'stalks', u'blocks', u'whole', u'bowls', u'servings']

possible_units_patterns = [(u, re.compile('(\d+).?(\\b'+u+'\\b)', flags=re.IGNORECASE),
                            re.compile('(\d{1,4}[ -]?\d/\d).?(\\b'+u+'\\b)', flags=re.IGNORECASE),
                            re.compile('(\d/\d).?(\\b'+u+'\\b)', flags=re.IGNORECASE),
                            re.compile('(\d{1,4}\.\d{1,4}).?(\\b'+u+'\\b)', flags=re.IGNORECASE),
                            re.compile('\\b'+u+'\\b', flags=re.IGNORECASE)) for u in possible_units]

uniform_units = {u'ounce': u'oz', u'ounces': u'oz', u'kilograms': u'kg', u'kilogram': u'kg', u'gr.': u'gram',
                 u'gr': u'gram', u'g': u'gram', u'grams': u'gram', u'lb': u'lbs', u'pound': u'lbs', u'pounds': u'lbs',
                 u'fl oz': u'floz', u'fl. oz': u'floz', u'fl.oz': u'floz', u'liter': u'l', u'block': u'blocks',
                 u'litre': u'l', u'litres': u'l', u'cup': u'cups', u'can': u'cans', u'tblsp': u'tbsp', u'liters': u'l',
                 u'teaspoon': u'tsp', u'teaspoons': u'tsp', u'tablespoon': u'tbsp', u'tablespoons': u'tbsp',
                 u'dozen': u'dozens', u'glass': u'glasses', u'gallon': u'gal', u'box': u'boxes', u'part': u'parts',
                 u'chunk': u'chunks', u'piece': u'pieces', u'drop': u'drops', u'stick': u'sticks', u'clove': u'cloves',
                 u'tbs': u'tbsp', u'handful': u'handfuls', u'bottle': u'bottles', u'package': u'packages',
                 u'packet': u'packets', u'pack': u'packs', u'jigger': u'jiggers', u'shot': u'shots', u'leaf': u'leaves',
                 u'wedge': u'wedges', u'slice': u'slices', u'dash': u'dashes', u'strip': u'strips', u'quart': u'quarts',
                 u'spring': u'springs', u'pint': u'pints', u'scoop': u'scoops', u'twist': u'twists', u'tube': u'tubes',
                 u'splash': u'splashes', u'measure': u'measures', u'qt': u'quarts', u'cube': u'cubes', u'jar': u'jars',
                 u'head': u'heads', u'pinch': u'pinches', u'bunch': u'bunches', u'container': u'containers',
                 u'loaf': u'loaves', u'pks': u'packs', u'pkg': u'packages', u'pkgs': u'packages', u'bundle': u'bundles',
                 u'root': u'roots', u'ear': u'ears', u'bag': u'bags', u'cob': u'cobs', u'sleeve': u'sleeves',
                 u'sheet': u'sheets', u'tbp': u'tbsp', u'patty': u'patties', u'sprig': u'sprigs', u'carton': u'cartons',
                 u'stalk': u'stalks', u'tbsps': u'tbsp', u'tbps': u'tbsp', u'tbspn': u'tbsp', u'tsbpns': u'tbsp',
                 u'tb': u'tbsp', u'tsps': u'tsp', u'ts': u'tsp', u'bowl': u'bowls', u'serving': u'servings',
                 u'gm': u'gram', u'gms': u'gram'}

uniform_units_patterns = [(u, re.compile('\\b'+u+'\\b', flags=re.IGNORECASE)) for u in uniform_units]

unit_strings = {u'dozens': u'12', u'fourth': u'1/4', u'fifth': u'1/5', u'fifths': u'1/5', u'quarter': u'1/4',
                u'quarters': u'1/4', u'third': u'1/3', u'thirds': u'1/3', u'half': u'1/2', u'halves': u'1/2'}

uniform_alcohol = {'sweet and sour': 'sweet and sour sauce', 'amaretto': 'amaretto liqueur',
                   'grand marnier': 'orange liqueur', 'absolut citron': 'vodka', 'absolut kurant': 'vodka',
                   'smirnoff': 'vodka', 'anis': 'anise', 'bailey': 'baileys', 'bacardi limon': 'bacardi rum',
                   'sambuca': 'anise liqueur', 'black sambuca': 'anise liqueur', 'bitter': 'bitters',
                   'anisette': 'anise liqueur', 'corona': 'beer', 'jagermeister': 'jager', 'whisky': 'whiskey',
                   'goldschlager': 'schnapps'}

conversion_to_grams = {'oz': 28.34, 'lbs': 453.592}

conversion_to_servings = {'couple': 2, 'few': 3, 'some': 4, 'several': 5}

conversion_to_cups = {'jiggers': 0.1875, 'drops': 0.0002, 'l': 4.226, 'ml': 0.004226, 'floz': 0.125, 'tbsp': 0.0625,
                      'cl': 0.04226, 'gal': 16, 'pints': 2, 'quart': 4, 'measure': 0.1, 'tsp': 0.02083, 'dl': 0.4226,
                      'cups': 1}

patt_1 = re.compile('^a ', flags=re.IGNORECASE)
patt_2 = re.compile('\\bt\.?\\b')
patt_3 = re.compile('\\bT\.?\\b')
patt_4 = re.compile('\\bc\.?\\b', flags=re.IGNORECASE)
patt_5 = re.compile(u'to taste')
patt_6 = re.compile('\\b\d+-inch\\b|\\b\d+ inch\\b', flags=re.IGNORECASE)
patt_7 = re.compile('\(.*?\)|\[.*?\]')
patt_8 = re.compile('(\d)+ or (\d)+')
patt_9 = re.compile('(\d)+ or ')
patt_10 = re.compile('(\d)+ to (\d)+')
patt_11 = re.compile('(\d)+ to ')
patt_12 = re.compile('(\d)+ ?- ?(\d)+')
patt_13 = re.compile('(\d)+ ?-')
patt_14 = re.compile('^\d+$', flags=re.IGNORECASE)
patt_15 = re.compile('\d+')
patt_16 = re.compile('long|short|large|big|medium|small|organic|hot|cold|sweet|fresh|black|white|ripe|soft|hard|vegan|thick|thin', flags=re.IGNORECASE)
patt_17 = re.compile('[A-Z]*ed\\b|[A-Z]*ly\\b|[A-Z]*en\\b|[A-Z]*less\\b|[A-Z]*ness\\b', flags=re.IGNORECASE)
patt_18 = re.compile('^-|\\bat\\b|\\bas\\b|\\bor\\b|\\band\\b|\\bwith\\b|\\bin\\b|\\bon\\b|\\bof\\b|\\bfor\\b|\\bsuch\\b|\\bnot\\b|\\band\\b|\\bad\\b|\\babout\\b|\\bto\\b|\\bover\\b', flags=re.IGNORECASE)
patt_19 = re.compile(',.*|[^A-Za-z ]')
patt_20 = re.compile('[^0-9\.]')


def get_all_ing_arr():
    all_ing_arr = []
    with open(INGREDIENTS_JSON_FILE, "r") as ingredients_file:
        ingredient_details = json.load(ingredients_file)
        for arr in ingredient_details:
            if 'foods' not in arr:
                continue
            for ing_dict in arr['foods']:
                all_ing_arr.append(ing_dict)
    all_ing_arr = {v['food_name']: v for v in all_ing_arr}.values()
    return all_ing_arr


def fix_measures(recipe_row, all_ing_arr):
    recipe_ingredients = recipe_row[7::4]
    try:
        for i in range(len(recipe_ingredients)):
            rec_ing = recipe_ingredients[i]
            idx = 7 + i*4
            rec_qty = float(recipe_row[idx + 1])
            rec_unit = recipe_row[idx + 2].strip()
            if rec_unit == 'servings':
                continue
            if rec_unit in conversion_to_servings:
                recipe_row[idx + 1] = str(rec_qty * conversion_to_servings[rec_unit])
                recipe_row[idx + 2] = 'servings'
                continue
            ing_dict = None
            for tmp_dict in all_ing_arr:
                if tmp_dict['food_name'].lower() == rec_ing.lower():
                    ing_dict = tmp_dict
            if ing_dict is None:
                recipe_row[idx + 2] = 'servings'
                continue
            flag = False
            if rec_unit == 'gram':
                recipe_row[idx + 1] = str(rec_qty / ing_dict['serving_weight_grams'])
                recipe_row[idx + 2] = 'servings'
                continue
            elif rec_unit in conversion_to_grams:
                recipe_row[idx + 1] = str(conversion_to_grams[rec_unit] * rec_qty / ing_dict['serving_weight_grams'])
                recipe_row[idx + 2] = 'servings'
                continue
            for alt in ing_dict['alt_measures']:
                meas = alt['measure']
                if meas in uniform_units:
                    meas = uniform_units[meas]
                if rec_unit in meas:
                    recipe_row[idx + 1] = str(rec_qty * alt['serving_weight'] / alt['qty'] / ing_dict['serving_weight_grams'])
                    recipe_row[idx + 2] = 'servings'
                    flag = True
                    break
            if not flag and rec_unit in conversion_to_cups:
                for alt in ing_dict['alt_measures']:
                    meas = alt['measure']
                    if 'cup' in meas:
                        recipe_row[idx + 1] = str(conversion_to_cups[rec_unit] * rec_qty * alt['serving_weight']
                                                  / alt['qty'] / ing_dict['serving_weight_grams'])
                        recipe_row[idx + 2] = 'servings'
                        flag = True
                        break
                    if meas in uniform_units:
                        meas = uniform_units[meas]
                    if meas in conversion_to_cups:
                        recipe_row[idx + 1] = str(conversion_to_cups[rec_unit] * rec_qty * alt['serving_weight'] *
                                                  conversion_to_cups[meas] / alt['qty'] / ing_dict['serving_weight_grams'])
                        recipe_row[idx + 2] = 'servings'
                        flag = True
                        break
            if not flag:
                recipe_row[idx + 2] = 'servings'
        return [elem for elem in recipe_row if elem != 'servings']
    except:
        return None


def load_ingredients():
    ingredients = []
    with open(INGREDIENTS_CSV_FILE, "r") as ingredients_file:
        ingredients_reader = csv.DictReader(ingredients_file)
        for ingredient in ingredients_reader:
            ing = ingredient['ingredient_name'].lower()
            if ing in ingredients:
                print "Already seen this ingredient! " + ing
            else:
                ingredients.append(ing)
    ingredients = list(set(ingredients))
    ingredients.sort(lambda x, y: cmp(len(y), len(x)))
    ingredient_list = []
    for ing in ingredients:
        ing = ing.strip()
        patt_1 = re.compile('(\\b' + ing + 's?\\b)')
        if ing[-1] == 's':
            patt_2 = re.compile('(\\b' + ing[:-1] + '\\b)')
        else:
            patt_2 = None
        ingredient_list.append((ing, patt_1, patt_2))
    return ingredient_list


def does_ingredient_exist(ingredient, ingredients_list, is_food):
    ingredient = ingredient.lower().strip()
    if ingredient == "":
        return False
    if not is_food:
        if ingredient in uniform_alcohol:
            ingredient = uniform_alcohol[ingredient]
    just_ingredients = []
    for i in ingredients_list:
        just_ingredients.append(i[0])
    if ingredient in just_ingredients:
        return ingredient
    elif ingredient + 's' in just_ingredients:
        return ingredient+'s'
    elif ingredient[-1] == 's' and ingredient[:-1] in just_ingredients:
        return ingredient[:-1]
    for i in ingredients_list:
        if bool(re.search(i[1], ingredient)):
            return re.search(i[1], ingredient).group(1)
        elif i[2] is not None:
            if bool(re.search(i[2], ingredient)):
                return re.search(i[2], ingredient).group(1)
    return False


def get_recipes_from_csv(csv_file_path):
    with open(csv_file_path, "r") as recipes_file:
        csv_reader = csv.reader(recipes_file)
        next(csv_reader)    # skip the first line
        for recipe in csv_reader:
            recipe_id = recipe[1]
            recipe_row = [r for r in recipe if r != ""]
            recipes_ingredients = recipe_row[7::4]
            recipe_row = recipe_row[1:]
            yield (recipe_id, recipes_ingredients, recipe_row)


def find_bad_recipes(is_food):
    ingredients_list = load_ingredients()
    all_ing_arr = get_all_ing_arr()
    bad = 0
    good = 0
    if is_food:
        output_file = FIXED_RECIPES_CSV_FILE
        csv_file_path = RECIPES_CSV_FILE
    else:
        output_file = FIXED_COCKTAILS_CSV_FILE
        csv_file_path = COCKTAILS_CSV_FILE
    with open(output_file, 'w') as fixed_output:
        writer = csv.writer(fixed_output, lineterminator='\n')
        if is_food:
            title_row = ['#', 'food_id', 'food_name', 'course', 'prep_time_minutes', 'food_picture',
                         'food_details_url'] + ['ingredient', 'servings', 'full_ingredient_line'] * 20
        else:
            title_row = ['#', 'cocktail_id', 'cocktail_name', 'is_alcoholic', 'serving_glass', 'cocktail_picture',
                         'cocktail_details'] + ['ingredient', 'servings', 'full_ingredient_line'] * 15
        writer.writerow(title_row)
        for recipe_id, recipes_ingredients, recipe_row in get_recipes_from_csv(csv_file_path):
            recipe_id = recipe_id.split('-')[-1]
            if not recipe_id.isdigit():
                bad += 1
                continue
            else:
                recipe_row[0] = recipe_id
            bad_ing = set()
            for i in range(len(recipes_ingredients)):
                res = does_ingredient_exist(recipes_ingredients[i], ingredients_list, is_food)
                if not res:
                    bad_ing.add(recipes_ingredients[i])
                else:
                    recipe_row[6 + i*4] = res
            if len(bad_ing) > 0:
                print "Bad " + str(recipe_id) + " - " + str(bad_ing)
                bad += 1
            else:
                good +=1
                recipe_row = [str(good)] + recipe_row
                recipe_row = fix_measures(recipe_row, all_ing_arr)
                if recipe_row is not None:
                    writer.writerow(recipe_row)
                else:
                    bad += 1
                    good -= 1
        print "Bad: " + str(bad) + " Good: " + str(good)


def is_fraction(string):
    string = string.split('/')
    return len(string) == 2 and all(i.isdigit() for i in string)


def parse_amount(amount_string):
    quantity = u'1'
    unit = u'servings'
    if amount_string is None or amount_string == '' or amount_string == ' ' or amount_string == '\n':
        return quantity, unit
    amount_string = re.sub(patt_1, '', amount_string)
    amount_string = re.sub(patt_2, 'tsp', amount_string)
    amount_string = re.sub(patt_3, 'tbsp', amount_string)
    amount_string = re.sub(patt_4, 'cups', amount_string)
    amount_string = re.sub(patt_5, u'1 tsp', amount_string)
    amount_string = unicodedata.normalize('NFKD', unicode(amount_string.strip())).encode('ascii', 'ignore')
    amount_string = re.sub(patt_6, '', amount_string)
    amount_arr = re.sub(patt_7, '', amount_string).split()
    if len(amount_arr) == 0:
        quantity = u'1'
        unit = u'servings'
        return quantity, unit
    if len(amount_arr) == 1:
        unit = u'servings'
    if is_fraction(amount_arr[0]):
        quantity = str(float(Fraction(amount_arr[0])))
    elif bool(re.match(patt_8, amount_arr[0])):
        quantity = re.sub(patt_9, '', amount_arr[0]).strip()
    elif bool(re.match(patt_10, amount_arr[0])):
        quantity = re.sub(patt_11, '', amount_arr[0]).strip()
    elif bool(re.match(patt_12, amount_arr[0])):
        quantity = re.sub(patt_13, '', amount_arr[0]).strip()
    else:
        quantity = amount_arr[0]
    if len(amount_arr) > 1:
        if amount_arr[1] in unit_strings and re.search(patt_14, amount_arr[0]):
            amount_arr[0] = str(float(Fraction(amount_arr[0]) * Fraction(unit_strings[amount_arr[1]])))
            quantity = amount_arr[0]
            del amount_arr[1]
        if amount_arr[0].isdigit() and is_fraction(amount_arr[1]):
            quantity = str(float(Fraction(amount_arr[0]) + Fraction(amount_arr[1])))
            if len(amount_arr) > 2:
                unit = ' '.join(amount_arr[2:])
            else:
                unit = u'servings'
        else:
            unit = ' '.join(amount_arr[1:])
    unit = unit.strip()
    if not bool(re.search(patt_15, quantity)):
        quantity = u'1'
        unit = u'servings'
    unit = re.sub(patt_16, '', unit)
    unit = re.sub(patt_17, '', unit)
    if bool(re.search(patt_18, unit)):
        unit = u'servings'
    unit = re.sub(patt_19, '', unit).replace('  ', ' ').strip().lower()
    quantity = re.sub(patt_20, '', quantity).replace('  ', ' ').strip().lower()
    if quantity == '':
        quantity = u'1'
    if unit == '':
        unit = u'servings'
    return quantity, unit


if __name__ == "__main__":
    find_bad_recipes(True)
    find_bad_recipes(False)

