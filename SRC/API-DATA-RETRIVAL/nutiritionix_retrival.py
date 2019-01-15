import requests
import csv
import json
import re
from retrival_utils import *
import unicodedata

BASE_URL = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
APP_ID = '643065ce'
APP_KEY = 'f79b0dd7ecd2029bde113d49bc5452e1'
APP_ID_TO_KEYS = {
    # '1ba9db25': 'e61863f0d69ba9d403ce34182058ad45', '03663f91': '3ad41d3cb51829571007890efafb0c1a',
    #               '35d23f2c': 'a1d152de0fb81cb94e513ee93f949416', '620bbd50': '1a4450b5446940202ecd0ec4947b2fe0',
    #               '04aff676': '3939b97c6425784b59480add034df2b5', '947f44c5': 'b9941884c5c16312c2b8950c1e0395c7',
    '83b5eaed': '5c9425cfe4530e972b5be24ad4746781',
    '1f92cec4': '25c7d866648b8cce61e7059205624dda', '59859745': '05be34f0b3d0c5c1030ca3f207e829de',
    'bdb22102': 'b76e129b2b4fadf33007175b57b4dae6', 'a0f9e465': 'f848b98d23930738930b8c0bfcfe9953',
    '0d662fca': '1068bb1882589e60a3a73ed837a5e386', '1b3e0608': 'bc184a1a3166ffe52ff32e83c6e7920c',
    '6ecb3e3a': 'b10fce47424bacd6399b718a64d00392', '59e9a3da': 'a45eb9e75a97cae7d0c8321930916236', APP_ID: APP_KEY,
    'ada22eaf': 'f5c46c5dfd99e16af49bb2c76eaadd90'}

HTTP_HEADERS = {'x-app-id': APP_ID, 'x-app-key': APP_KEY, 'x-remote-user-id': '1',
                'Accept': 'application/json', 'Content-Type': 'application/json'}
HTTP_DATA = {'num_servings': 1, 'line_delimited': True, 'use_raw_foods': True, 'include_subrecipe': False,
             'lat': 0, 'lng': 0, 'meal_type': 0, 'use_branded_foods': False, 'locale': 'en_US'}
INGREDIENTS_FILE = 'ingredients.txt'
INGREDIENTS_CSV_FILE = 'ingredients.csv'
INGREDIENTS_JSON_FILE = 'ingredients_details.json'
RECIPE_JSON_FILE = 'recipes_details.json'
COCKTAIL_CSV_FILE = 'cocktails.csv'


nutri_ordered = ['sugar', 'iron', 'calcium', 'sodium', 'protein', 'cholesterol', 'potassium', 'lactose', 'vitamin_C',
                 'saturated_fat', 'trans_fat', 'dietary_fiber', 'calories', 'alcohol', 'magnesium', 'zinc']

nutri_id_to_name = {269: 'sugar', 303: 'iron', 301: 'calcium', 307: 'sodium', 203: 'protein', 601: 'cholesterol',
                    306: 'potassium', 213: 'lactose', 401: 'vitamin_C', 606: 'saturated_fat', 605: 'trans_fat',
                    291: 'dietary_fiber', 208: 'calories', 221: 'alcohol', 304: 'magnesium', 309: 'zinc'}

nutri_name_to_unit = {'sugar': 'g', 'iron': 'mg', 'calcium': 'mg', 'sodium': 'mg', 'protein': 'g', 'cholesterol': 'mg',
                      'potassium': 'mg', 'lactose': 'g', 'vitamin_C': 'mg', 'saturated_fat': 'g', 'trans_fat': 'g',
                      'dietary_fiber': 'g', 'calories': 'kcal', 'alcohol': 'g', 'magnesium': 'mg', 'zinc': 'mg'}


def get_cocktail_ingredient_list():
    cocktail_ingredient_list = []
    res = []
    ingredients_list = load_ingredients()
    with open(COCKTAIL_CSV_FILE, 'r') as f:
        csv_reader = csv.reader(f)
        next(csv_reader)  # skip the first line
        for cocktail_row in csv_reader:
            cocktail_ingredients = cocktail_row[7::4]
            cocktail_ingredient_list.extend(cocktail_ingredients)
    cocktail_ingredient_list = list(set(cocktail_ingredient_list))
    for i in range(len(cocktail_ingredient_list)):
        cocktail_ingredient_list[i] = cocktail_ingredient_list[i].lower()
    for cocktail_ing in cocktail_ingredient_list:
        cocktail_ing = cocktail_ing.replace('-', ' ').replace('  ', ' ').strip()
        if cocktail_ing != '' and not does_ingredient_exist(cocktail_ing, ingredients_list):
            res.append(cocktail_ing)
    return res


def get_ingredient_list():
    ingredient_list = []
    cocktail_ingredients = get_cocktail_ingredient_list()
    with open(RECIPE_JSON_FILE, 'r') as f:
        recipe_json_arr = json.load(f)
        for recipe_dict in recipe_json_arr:
            ingredient_list.extend(recipe_dict['ingredients'])
    ingredient_list = list(set(ingredient_list + cocktail_ingredients))
    curr_ingredient_string = ""
    ingredient_strings_arr = []
    counter = 0
    for ing in ingredient_list:
        if counter != 10:
            curr_ingredient_string = curr_ingredient_string + ing + '\n'
            counter += 1
        else:
            counter = 0
            ingredient_strings_arr.append(curr_ingredient_string[:-1])
            curr_ingredient_string = ""
    return ingredient_strings_arr


def create_ingredient_json(ingredient_strings_arr):
    api_counter = 90
    api_ids_to_use = APP_ID_TO_KEYS.keys()
    with open(INGREDIENTS_JSON_FILE, 'w') as f:
        f.write('[')
        for ing_str in ingredient_strings_arr:
            if api_counter == 90:
                api_counter = 0
                HTTP_HEADERS['x-app-id'] = api_ids_to_use.pop()
                HTTP_HEADERS['x-app-key'] = APP_ID_TO_KEYS[HTTP_HEADERS['x-app-id']]
            else:
                api_counter += 1
            HTTP_DATA['query'] = ing_str
            try:
                response = requests.post(BASE_URL, headers=HTTP_HEADERS, data=json.dumps(HTTP_DATA)).text
                response = unicodedata.normalize('NFKD', unicode(response)).encode('ascii', 'ignore')
            except:
                print ing_str
                return
            if ingredient_strings_arr.index(ing_str) != 0:
                f.write(',')
            f.write(response)
        f.write(']')
    return


def create_ingredient_csv():
    index = 0
    all_ing_arr = get_all_ing_arr()
    with open(INGREDIENTS_CSV_FILE, 'w+') as output:
        writer = csv.writer(output, lineterminator='\n')
        title_row = ['#', 'ingredient_name', 'serving_quantity', 'serving_unit', 'serving_weight_grams']
        for n in nutri_ordered:
            if n != 'calories':
                title_row.extend([n + '_mg'])
            else:
                title_row.extend([n + '_kcal'])
        writer.writerow(title_row)
        for ing_dict in all_ing_arr:
            index += 1
            ingredient_name = ing_dict['food_name']
            curr_nutri_vals_dict = {n: '0' for n in nutri_ordered}
            for nutri_val in ing_dict['full_nutrients']:
                nutri_val_id = nutri_val['attr_id']
                if nutri_val_id in nutri_id_to_name:
                    nutri_val_name = nutri_id_to_name[nutri_val_id]
                    nutri_val_amount = nutri_val['value']
                    if nutri_name_to_unit[nutri_val_name] == 'g':
                        nutri_val_amount *= 1000
                    curr_nutri_vals_dict[nutri_val_name] = str(nutri_val_amount)
            serving_qty = ing_dict['serving_qty']
            serving_unit = ing_dict['serving_unit']
            for unit in uniform_units:
                if re.search('\\b'+unit+'\\b', serving_unit, flags=re.IGNORECASE):
                    serving_unit = uniform_units[unit]
                    break
            serving_weight_grams = ing_dict['serving_weight_grams']
            ingredient_row = [str(index), ingredient_name, serving_qty, serving_unit, serving_weight_grams]
            ingredient_row += [curr_nutri_vals_dict[k] for k in nutri_ordered]
            try:
                ingredient_row = [unicodedata.normalize('NFKD', unicode(s)).encode('ascii', 'ignore') for s in ingredient_row]
                writer.writerow(ingredient_row)
            except Exception as e:
                index -= 1
                continue
    return


def main():
    ingredient_string_arr = get_ingredient_list()
    create_ingredient_json(ingredient_string_arr)
    create_ingredient_csv()
    return


if __name__ == "__main__":
    main()
