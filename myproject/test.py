import pandas as pd
import numpy as np
import collections
import json

filename = r'C:\Users\Illya.Prokopenko\scrapy_project\myproject\result.csv'

df = pd.read_csv(filename, sep=',', decimal='.', encoding='latin1')
df = df.drop_duplicates()

num_of_product_fr = df.loc[df.region == 'fr_fr'].groupby('region')['region'].count().values[0]
num_of_product_us = df.loc[df.region == 'en_us'].groupby('region')['region'].count().values[0]

# Check currency. Create new column. Yes if currency right, else - no
df['right_currency'] = np.where(((df['region'] == 'fr_fr') & (df['currency'] == 'EUR')) | ((df['region'] == 'en_us') & (df['currency'] == 'USD')), 'yes', 'no')

# Count color percent. First i calculate all colors of all items and then find percent of each other
tmp = df[['name', 'color']]
tmp = tmp.drop_duplicates()
tmp = tmp.dropna()
all_colors = []
for color in tmp['color'].values:
    colors = color.split(', ')
    for c in colors:
        all_colors.append(c)

counter = collections.Counter(all_colors)
n = len(all_colors)
for key in counter.keys():
    counter[key] = counter[key] / n

# Count size percent
tmp = df[['name', 'size']]
tmp = tmp.drop_duplicates()
tmp = tmp.dropna()
tmp = tmp.groupby('size')['size'].count()
size_name = tmp.index
size_val = [val / len(size_name) for val in tmp.values]

tmp = df[['name', 'description']]
tmp = tmp.drop_duplicates()
all_desc = tmp.shape[0]
have_desc = tmp.dropna().shape[0]
desc_percent = have_desc / all_desc

result = {'num_of_product_fr': int(num_of_product_fr),
          'num_of_product_us': int(num_of_product_us),
          'right_currency': dict(zip(df.name.values, df.right_currency.values)),
          'color_percent': counter,
          'size_percent': dict(zip(list(size_name), list(size_val))),
          'have_description_percent': float(desc_percent)
          }

# Write all to result file
with open('test.json', 'w') as fp:
    json.dump(result, fp)
