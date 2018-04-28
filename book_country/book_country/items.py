# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BookCountryItem(scrapy.Item):
    name_product = scrapy.Field()
    code_product = scrapy.Field()
    price = scrapy.Field()
    manufacturer = scrapy.Field()
    kind = scrapy.Field()
    category = scrapy.Field()
    image_name = scrapy.Field()
