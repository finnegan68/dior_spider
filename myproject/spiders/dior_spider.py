import scrapy
import pandas as pd
import datetime
import json
import os
import logging
from scrapy.utils.log import configure_logging

configure_logging(install_root_handler=False)
logging.basicConfig(
    filename='log.txt',
    format='%(levelname)s: %(message)s',
    level=logging.INFO
)

site = 'https://www.dior.com'
regions = ['fr_fr', 'en_us']
result_file_path = r'C:\Users\Illya.Prokopenko\scrapy_project\myproject\result.csv'


class DiorSpider(scrapy.Spider):
    name = "dior"

    # Start requests to fr and us region
    def start_requests(self):
        for region in regions:
            yield scrapy.Request(url=site + '/' + region, callback=self.parse)

    def parse(self, response):
        urls = response.xpath('//a[re:test(@class, "navigation-item-link")]//@href').extract()
        for p in urls:
            if site not in p:
                yield scrapy.Request(url=site + p, callback=self.parse_categories)

    # Parse all categories
    def parse_categories(self, response):
        urls = response.xpath('//a[re:test(@class, "product-link")]//@href').extract()
        for url in urls:
            yield scrapy.Request(url=site + url, callback=self.parse_product)

    def parse_product(self, response):
        name = response.css('h1').css('span::text').extract_first()
        url = response.url
        region = url.split('/')[3]
        try:
            description = response.xpath('//div[@class="product-tab-html"]').css('div::text').extract()[0]
        except IndexError:
            description = 'no description'

        data = response.xpath('//script/text()').extract()

        '''
        a little bit of hardcode :)
        i got data from <script> tag like a string, that contain info about product
        '''

        data = json.loads(data[4][31:-7])

        # Some products have few variations, and that's why i create lists
        sku_list = []
        price_list = []
        currency_list = []
        size_list = []
        category_list = []
        status_list = []
        scanning_time_list = []

        # We have not info about color of each product unit, we just know that we have this product in some colors
        color_str = ''

        for el in data['CONTENT']['cmsContent']['elements']:
            if el['type'] == 'PRODUCTVARIATIONS':
                for var in el['variations']:
                    sku_list.append(var['sku'])
                    price_list.append(var['price']['value'])
                    currency_list.append(var['price']['currency'])
                    size_list.append(var['title'])
                    category_list.append(var['tracking'][0]['ecommerce']['add']['products']['category'])
                    # Some products have no status
                    try:
                        status_list.append(var['status'])
                    except KeyError:
                        status_list.append('no status')
                    scanning_time_list.append(datetime.datetime.now())
            elif el['type'] == 'PRODUCTDECLINATIONS':
                for product in el['declinations']:
                    color_str = color_str + product['color'] + ', '
                color_str = color_str[:-2]

            n = len(sku_list)

            # Create dataframe and append it to result file
            new_df = pd.DataFrame({
                'url': [url for i in range(0, n)],
                'name': [name for i in range(0, n)],
                'price': price_list,
                'currency': currency_list,
                'category': category_list,
                'SKU': sku_list,
                'status': status_list,
                'scanning_time': scanning_time_list,
                'color': [color_str for i in range(0, n)],
                'size': size_list,
                'region': [region for i in range(0, n)],
                'description': [description for i in range(0, n)]
            })

            if not os.path.isfile(result_file_path):
                new_df.to_csv(result_file_path,
                              header=['url', 'name', 'price', 'currency', 'category', 'SKU', 'status', 'scanning_time',
                                      'color', 'size', 'region', 'description'])
            else:
                new_df.to_csv(result_file_path, mode='a', header=False)
