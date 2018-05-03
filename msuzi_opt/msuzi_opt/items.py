# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MsuziOptProductItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    props = scrapy.Field()
    descr = scrapy.Field()
    referer = scrapy.Field()
    name_images = scrapy.Field()


class MsuziOptCatalogItem(scrapy.Item):
    name_catalog = scrapy.Field()
    url_catalog = scrapy.Field()

