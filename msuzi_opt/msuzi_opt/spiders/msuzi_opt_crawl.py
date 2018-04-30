# -*- coding: utf-8 -*-
import scrapy


class MsuziOptCrawlSpider(scrapy.Spider):
    name = 'msuzi_opt_crawl'
    allowed_domains = ['msuzi-opt.ru']
    start_urls = ['http://msuzi-opt.ru/']

    def parse(self, response):
        pass
