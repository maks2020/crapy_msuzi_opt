# -*- coding: utf-8 -*-

import os

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from bs4 import BeautifulSoup

import book_country.settings as my_setting
from book_country.items import BookCountryItem
from constants import IMAGE_PATH


class KancSpiderSpider(CrawlSpider):
    name = 'kanc_spider'
    allowed_domains = ['bookcountry-shop.ru']
    start_urls = [
        'http://bookcountry-shop.ru/kategorii/raznoe.html',
        'http://bookcountry-shop.ru/kategorii/bumagnaya-produkciya.html',
        'http://bookcountry-shop.ru/kategorii/tovary-dlya-ofisa.html',
        'http://bookcountry-shop.ru/kategorii/tvorchestvo.html',
        'http://bookcountry-shop.ru/kategorii/pismennye-prinadlegnosti.html',
        'http://bookcountry-shop.ru/kategorii/shkolnye-prinadlegnosti.html'
    ]

    rules = (
        Rule(LxmlLinkExtractor(restrict_css=('tr td.info div.name a', )),
             callback='parse_product'),
        Rule(LxmlLinkExtractor(restrict_css=(
            'ul.pagination > li > a',)), follow=True)
    )

    def parse_product(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        if ('<div class="not_available" id="not_available">Нет в наличии</div>'
                not in soup):
            item = BookCountryItem()
            item['name_product'] = soup.select_one('h1').get_text(strip=True)

            item['code_product'] = (soup.select_one('span.jshop_code_prod >'
                                                    ' span#product_code')
                                    .get_text(strip=True))
            item['price'] = float(soup.select_one('span#block_price')
                                  .get_text(strip=True).split()[0])
            extra_fields = soup.select('div.extra_fields span'
                                       '.extra_fields_value')
            item['manufacturer'] = extra_fields[0].get_text(strip=True)
            item['kind'] = extra_fields[1].get_text(strip=True)
            item['category'] = (soup.select('ul.breadcrumb li')[-2]
                                .get_text(strip=True))
            if 'noimage.gif' not in response.text:
                href = soup.select_one('a.zoom').get('href')
                image_name = href.split('/')[-1]
                item['image_name'] = image_name
            else:
                item['image_name'] = None
            yield item
            if item['image_name'] is not None:
                yield scrapy.Request(href, callback=self.parse_image,
                                     meta={'image_name': item['image_name']})

    @staticmethod
    def parse_image(response):
        os.makedirs(IMAGE_PATH, exist_ok=True)
        image_name = response.meta['image_name']
        image_path = os.path.join(IMAGE_PATH, image_name)
        with open(image_path, 'wb') as image_file:
            image_file.write(response.body)


def run_crawl():
    """Run crawler"""
    crawler_setting = Settings()
    crawler_setting.setmodule(my_setting)
    process = CrawlerProcess(settings=crawler_setting)
    process.crawl(KancSpiderSpider)
    process.start()


if __name__ == '__main__':
    run_crawl()