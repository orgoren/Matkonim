import requests
import csv
from retrival_utils import *


BASE_URL = 'https://www.thecocktaildb.com/api/json/v1/1/'
CATEGORY_LIST_URL = BASE_URL + 'list.php?c=list'
METADATA_BY_CATEGORY_URL = BASE_URL + 'filter.php?c='
LOOKUP_BY_ID_URL = BASE_URL + 'lookup.php?i='
OUTPUT_FILE = 'cocktails.csv'


def get_categories_arr():
    categories_dict = requests.get(CATEGORY_LIST_URL).json()
    categories_arr = []
    for cat_dict in categories_dict['drinks']:
        curr_category = cat_dict['strCategory']
        if curr_category is not None:
            categories_arr.append(curr_category)
    return categories_arr


def get_metadata_arr(categories_arr):
    category_metadata_arr = []
    for category in categories_arr:
        url_category = category.replace(' ', '+')
        category_metadata_dict = requests.get(METADATA_BY_CATEGORY_URL + url_category).json()
        category_metadata_arr.extend(category_metadata_dict['drinks'])
    return category_metadata_arr


def parse_ingredients(cocktail):
    result_arr = []
    for i in range(1, 16):
        curr_ingredient = cocktail['strIngredient' + str(i)]
        amount_string = cocktail['strMeasure' + str(i)]
        full_ingredient_str = 'None'
        if curr_ingredient is not None and curr_ingredient != '' and curr_ingredient != ' ':
            if amount_string is not None:
                curr_ingredient = curr_ingredient.lower().replace('-', ' ').replace('  ', ' ').strip()
                amount_string = amount_string.lower().replace('-', ' ').replace('  ', ' ').strip()
                full_ingredient_str = (amount_string + ' ' + curr_ingredient).replace('  ', ' ').strip()
                attr_pattern = re.compile(
                    '(\\blong\\b|\\bshort\\b|\\blarge\\b|\\bbig\\b|\\bmedium\\b|\\bsmall\\b|\\bdiced\\b|\\bsliced\\b' +
                    '|\\bfresh\\b|\\bcracked\\b|\\bblack\\b|\\bfrozen\\b|\\bripe\\b|\\bbeaten\\b|\\bcrushed\\b)',
                    flags=re.IGNORECASE)
                if bool(re.search(attr_pattern, amount_string)):
                    attr_found = re.search(attr_pattern, amount_string).group(1)
                    if not bool(re.search(attr_found, curr_ingredient, flags=re.IGNORECASE)):
                        curr_ingredient = attr_found + ' ' + curr_ingredient
                        amount_string = re.sub(attr_found, '', amount_string, flags=re.IGNORECASE).strip()
                amount_string = re.sub('^[a-zA-Z ]+', '', amount_string)
                for u in uniform_units:
                    amount_string = re.sub('\\b'+u+'\\b', uniform_units[u], amount_string, flags=re.IGNORECASE)
                for u in possible_units:
                    amount_string = re.sub('\\b'+u+'\\b.*', u, amount_string, flags=re.IGNORECASE)
            quantity, unit = parse_amount(amount_string)
            for u in possible_units:
                if bool(re.search('\\b'+u+'\\b', unit, flags=re.IGNORECASE)):
                    unit = u
            result_arr.extend([curr_ingredient, quantity, unit, full_ingredient_str])
    return result_arr


def create_cocktail_csv(metadata_arr):
    index = 0
    with open(OUTPUT_FILE, 'w+') as output:
        writer = csv.writer(output, lineterminator='\n')
        title_row = ['#', 'cocktail_id', 'cocktail_name', 'is_alcoholic', 'serving_glass', 'cocktail_picture',
                     'cocktail_details'] + ['ingredient', 'quantity', 'unit', 'full_ingredient_line'] * 10
        writer.writerow(title_row)
        for metadata_dict in metadata_arr:
            curr_cocktail_id = metadata_dict['idDrink']
            cocktail = requests.get(LOOKUP_BY_ID_URL + curr_cocktail_id).json()['drinks'][0]
            index += 1
            cocktail_id = cocktail['idDrink']
            cocktail_name = cocktail['strDrink']
            alcoholic = cocktail['strAlcoholic']
            if alcoholic is None:
                alcoholic = u'Alcoholic'
            glass = cocktail['strGlass']
            picture = cocktail['strDrinkThumb']
            recipe = cocktail['strInstructions']
            ingredients_amounts_arr = parse_ingredients(cocktail)
            cocktail_row = [str(index), cocktail_id, cocktail_name, alcoholic, glass, picture, recipe]
            cocktail_row.extend(ingredients_amounts_arr)
            try:
                cocktail_row = [unicodedata.normalize('NFKD', unicode(s)).encode('ascii', 'ignore') for s in cocktail_row]
                writer.writerow(cocktail_row)
            except Exception as e:
                index -= 1
                continue


def main():
    categories_arr = get_categories_arr()
    metadata_arr = get_metadata_arr(categories_arr)
    create_cocktail_csv(metadata_arr)
    return


if __name__ == "__main__":
    main()
