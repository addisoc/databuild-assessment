import urllib
import zipfile

import requests
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
raw_folder = config['data.location']['raw']
ingredients_list: str = config['data.name']['raw.ingredients.url']
recipes_zip: str = config['data.name']['raw.recipes.url']
ingredients_name = config['data.name']['raw.ingredients.list']

r = requests.get(ingredients_list, stream=True)

with open(f"{raw_folder}/{ingredients_name}", 'wb') as f:
    f.write(r.content)

zip_path, _ = urllib.request.urlretrieve(recipes_zip)
with zipfile.ZipFile(zip_path, "r") as f:
    f.extractall(raw_folder)
