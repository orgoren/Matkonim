import requests
import csv
import json
import re
from retrival_utils import *
import unicodedata

BASE_URL = 'http://api.yummly.com/v1/api/'
APP_ID_1 = '0ff68785'
APP_KEY_1 = '2294e654308abac7a88c9e2c264c44aa'
CREDENTIALS_STR_1 = '_app_id=' + APP_ID_1 + '&_app_key=' + APP_KEY_1
APP_ID_2 = '69f70b4b'
APP_KEY_2 = '234035babc041c289a8449be47a91dd6'
CREDENTIALS_STR_2 = '_app_id=' + APP_ID_2 + '&_app_key=' + APP_KEY_2
APP_ID_3 = '2ff4f85c'
APP_KEY_3 = 'adba41763421147d3bcae5641c09a723'
CREDENTIALS_STR_3 = '_app_id=' + APP_ID_3 + '&_app_key=' + APP_KEY_3
CATEGORY_LIST_URL = BASE_URL + 'metadata/course?' + CREDENTIALS_STR_1
METADATA_BY_CATEGORY_URL = BASE_URL + 'recipes?' + CREDENTIALS_STR_1 + '&requirePictures&allowedCourse[]=course^course-'
MAX_RESULTS = '&maxResult=200&start='
LOOKUP_BY_ID_URL = BASE_URL + 'recipe/'
RECIPE_METADATA_FILE = 'recipes_metadata.json'
RECIPE_JSON_FILE = 'recipes_details.json'
RECIPE_CSV_FILE = 'recipes.csv'

patt_21 = re.compile('.*-')
patt_22 = re.compile('salt and .*pepper', flags=re.IGNORECASE)
patt_23 = re.compile(' and .*pepper', flags=re.IGNORECASE)
patt_24 = re.compile('.*pepper', flags=re.IGNORECASE)
patt_25 = re.compile('(\d+) -(\d+)|(\d+)- (\d+)', flags=re.IGNORECASE)
patt_26 = re.compile('(\d)-?([A-Za-z])', flags=re.IGNORECASE)
patt_27 = re.compile(' |-')
patt_28 = re.compile('salt|pepper', flags=re.IGNORECASE)
patt_29 = re.compile('&|-and-')
patt_30 = re.compile('[^A-Za-z]+')


def get_recipes_categories():
    categories = requests.get(CATEGORY_LIST_URL).text
    categories = categories.replace('set_metadata(\'course\', ', '')
    categories = categories.replace(');', '')
    categories = json.loads(categories)
    categories_arr = []
    for category_dict in categories:
        if category_dict['name'] != 'Cocktails' and category_dict['name'] != 'Beverages':
            curr_category = category_dict['name']
            categories_arr.append(curr_category)
    return categories_arr


def get_recipes_metadata(categories_arr):
    for category in categories_arr:
        category_outfile = category.replace(' ', '_') + '_tmp.json'
        with open(category_outfile, 'w') as f:
            f.write('[')
            url_category = category.replace(' ', '+')
            for i in range(20):
                category_metadata_dict = requests.get(METADATA_BY_CATEGORY_URL + url_category + MAX_RESULTS + str(i*200)).json()
                category_matches = category_metadata_dict['matches']
                for match in category_matches:
                    match['course'] = category
                json.dump(category_metadata_dict['matches'], f)
                if i != 19:
                    f.write(',')
            f.write(']')
    with open(RECIPE_METADATA_FILE, 'w') as outfile:
        outfile.write('[')
        for cat in categories_arr:
            fname = cat.replace(' ', '_') + '_tmp.json'
            with open(fname) as infile:
                for line in infile:
                    tmp = line[1:-1]
                    outfile.write(tmp)
            if categories_arr.index(cat) != len(categories_arr) - 1:
                outfile.write(',')
        outfile.write(']')
    return


def parse_ingredients(ingredient_lines, ingredient_list):
    result_arr = []
    had_salt_and_pepper = False
    for curr_ingredient in ingredient_list:
        try:
            if bool(re.search(patt_22, curr_ingredient)):
                if not had_salt_and_pepper:
                    curr_ingredient = re.sub(patt_23, '', curr_ingredient)
                    had_salt_and_pepper = True
                else:
                    curr_ingredient = re.sub(patt_24, 'pepper', curr_ingredient)
            quantity = u'None'
            unit = u'servings'
            curr_line = None
            ing_patt_1 = re.compile(re.sub(patt_30, '.+', curr_ingredient), flags=re.IGNORECASE)
            ing_patt_2 = re.compile(curr_ingredient.split()[-1]+'|'+curr_ingredient.split()[0], flags=re.IGNORECASE)
            ing_patt_3 = re.compile(curr_ingredient[:-2], flags=re.IGNORECASE)
            ing_patt_4 = re.compile(curr_ingredient[:-1], flags=re.IGNORECASE)
            for tmp_line in ingredient_lines:
                tmp_line = tmp_line.replace(' g ', ' gram ').replace('0g ', '0 gram ').replace('1g ', '1 gram ').replace('2g ', '2 gram ').replace('3g ', '3 gram ').replace('4g ', '4 gram ').replace('5g ', '5 gram ').replace('6g ', '6 gram ').replace('7g ', '7 gram ').replace('8g ', '8 gram ').replace('9g ', '9 gram ').replace('  ', ' ').strip()
                if bool(re.search(ing_patt_1, tmp_line)):
                    final_curr_line = tmp_line
                    curr_line = re.sub(ing_patt_1, '', tmp_line)
                    break
                elif bool(re.search(ing_patt_2, tmp_line)):
                    final_curr_line = tmp_line
                    curr_line = re.sub(ing_patt_2, '', tmp_line)
                    break
                elif curr_ingredient[-1] == 's':
                    if curr_ingredient[-2] == 'e' and bool(re.search(ing_patt_3, tmp_line)):
                        final_curr_line = tmp_line
                        curr_line = re.sub(ing_patt_3, '', tmp_line)
                        break
                    elif bool(re.search(ing_patt_4, tmp_line)):
                        final_curr_line = tmp_line
                        curr_line = re.sub(ing_patt_4, '', tmp_line)
                        break
            if curr_line is None:
                return []
            for frac in unicode_fractions:
                curr_line = curr_line.replace(frac, unicode_fractions[frac]).strip()
            amount_string = re.sub(patt_25, '\1-\2', curr_line).strip()
            amount_string = re.sub(patt_26, '\1 \2', amount_string)
            for couple in uniform_units_patterns:
                amount_string = re.sub(couple[1], uniform_units[couple[0]], amount_string)
            for tup in possible_units_patterns:
                if bool(re.search(tup[2], amount_string)):
                    tmp_arr = re.split(patt_27, re.search(tup[2], amount_string).group(1))
                    quantity = str(float(Fraction(tmp_arr[0]) + Fraction(tmp_arr[1])))
                    unit = re.search(tup[2], amount_string).group(2)
                    break
                elif bool(re.search(tup[3], amount_string)):
                    quantity = str(float(Fraction(re.search(tup[3], amount_string).group(1))))
                    unit = re.search(tup[3], amount_string).group(2)
                    break
                elif bool(re.search(tup[4], amount_string)):
                    quantity = str(float(re.search(tup[4], amount_string).group(1)))
                    unit = re.search(tup[4], amount_string).group(2)
                    break
                elif bool(re.search(tup[1], amount_string)):
                    quantity = re.search(tup[1], amount_string).group(1)
                    unit = re.search(tup[1], amount_string).group(2)
                    break
            if quantity == u'None' or unit == u'servings':
                quantity, unit = parse_amount(amount_string)
            if bool(re.search(patt_28, curr_ingredient)) and unit == u'servings':
                unit = u'tsp'
            for tup in possible_units_patterns:
                if bool(re.search(tup[5], unit)) or bool(re.search(tup[5], curr_ingredient)):
                    unit = tup[0]
                    break
            # for part in curr_ingredient.split():
            #     if bool(re.search('\\b'+part+'\\b', unit, flags=re.IGNORECASE)):
            #         unit = u'servings'
            # if len(unit) == 1 and unit not in uniform_units:
            #     unit = u'servings'
            unit = unit.replace('  ', ' ').strip()
            # for couple in uniform_units_patterns:
            #     amount_string = re.sub(couple[1], uniform_units[couple[0]], amount_string)
            curr_ingredient = re.sub(patt_29, ' and ', curr_ingredient).replace('  ', ' ').strip()
            if unit not in possible_units:
                unit = u'servings'
            result_arr.extend([curr_ingredient, quantity, unit, final_curr_line])
        except:
            return []
    return result_arr


def get_recipes_json():
    count = 0
    with open(RECIPE_METADATA_FILE, 'r') as metadata_file:
        all_metadata_arr = json.load(metadata_file)
    with open(RECIPE_JSON_FILE, 'w+') as recipe_json_file:
        recipe_json_file.write('[')
        for part_arr in all_metadata_arr:
            for metadata_dict in part_arr:
                count += 1
                recipe_id = metadata_dict['id'].replace(' ', '+').strip()
                if count < 20000:
                    CREDENTIALS_STR = CREDENTIALS_STR_2
                else:
                    CREDENTIALS_STR = CREDENTIALS_STR_3
                try:
                    curr_recipe_details = requests.get(LOOKUP_BY_ID_URL + recipe_id + '?' + CREDENTIALS_STR).json()
                    curr_recipe_details.pop('nutritionEstimates', None)
                    curr_recipe_details.pop('yield', None)
                    curr_recipe_details.pop('prepTime', None)
                    curr_recipe_details.pop('cookTime', None)
                    curr_recipe_details.pop('totalTime', None)
                    curr_recipe_details.pop('attribution', None)
                    curr_recipe_details.pop('attributes', None)
                    curr_recipe_details.pop('cookTimeInSeconds', None)
                    curr_recipe_details.pop('flavors', None)
                    curr_recipe_details.pop('rating', None)
                    curr_recipe_details['course'] = metadata_dict['course']
                    curr_recipe_details['ingredients'] = metadata_dict['ingredients']
                    curr_recipe_details['sourceRecipeUrl'] = curr_recipe_details['source']['sourceRecipeUrl']
                    curr_recipe_details.pop('source', None)
                    if ('images' in curr_recipe_details
                            and curr_recipe_details['images'] is not None and curr_recipe_details['images'] != []):
                        image_arr = curr_recipe_details['images'][0]
                        curr_recipe_details['image'] = u'None'
                        if ('hostedLargeUrl' in image_arr
                                and image_arr['hostedLargeUrl'] is not None and image_arr['hostedLargeUrl'] != ''):
                            image = image_arr['hostedLargeUrl']
                            curr_recipe_details['image'] = image
                        elif ('hostedMediumUrl' in image_arr
                                and image_arr['hostedMediumUrl'] is not None and image_arr['hostedMediumUrl'] != ''):
                            image = image_arr['hostedMediumUrl']
                            curr_recipe_details['image'] = image
                        curr_recipe_details.pop('images', None)
                    json.dump(curr_recipe_details, recipe_json_file)
                    if all_metadata_arr.index(part_arr) != (len(all_metadata_arr) - 1):
                        recipe_json_file.write(',')
                    else:
                        if part_arr.index(metadata_dict) != (len(part_arr) - 1):
                            recipe_json_file.write(',')
                except:
                    continue
        recipe_json_file.write(']')
    return


def create_recipe_csv():
    index = 0
    with open(RECIPE_JSON_FILE, 'r') as recipe_json_file:
        all_recipes = json.load(recipe_json_file)
    with open(RECIPE_CSV_FILE, 'w+') as output:
        writer = csv.writer(output, lineterminator='\n')
        title_row = ['#', 'food_id', 'food_name', 'course', 'prep_time_minutes', 'food_picture',
                     'food_details_url'] + ['ingredient', 'quantity', 'unit', 'full_ingredient_line'] * 20
        writer.writerow(title_row)
        for curr_recipe_dict in all_recipes:
            index += 1
            food_id = re.sub(patt_21, '', curr_recipe_dict['id'])
            recipe_name = curr_recipe_dict['name'].strip()
            prep_time_min = str(curr_recipe_dict['totalTimeInSeconds'] / 60).strip()
            course = curr_recipe_dict['course']
            recipe_url = curr_recipe_dict['sourceRecipeUrl']
            ingredients_list = curr_recipe_dict['ingredients']
            ingredient_lines = curr_recipe_dict['ingredientLines']
            image = curr_recipe_dict['image']
            recipe_row = [str(index), food_id, recipe_name, course, prep_time_min, image, recipe_url]
            ingredients_amounts_arr = parse_ingredients(ingredient_lines, ingredients_list)
            if ingredients_amounts_arr == [] or len(ingredients_amounts_arr) != 4*len(ingredients_list):
                index -= 1
                continue
            recipe_row.extend(ingredients_amounts_arr)
            try:
                recipe_row = [unicodedata.normalize('NFKD', unicode(s)).encode('ascii', 'ignore') for s in recipe_row]
                writer.writerow(recipe_row)
            except Exception as e:
                index -= 1
                continue
    return


def main():
    categories_arr = get_recipes_categories()
    get_recipes_metadata(categories_arr)
    get_recipes_json()
    create_recipe_csv()
    return


if __name__ == "__main__":
    main()