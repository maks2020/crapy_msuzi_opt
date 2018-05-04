# -*- coding: utf-8 -*-

import os
import re

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

import bs4
from bs4 import BeautifulSoup

import msuzi_opt.msuzi_opt.settings as my_setting
from msuzi_opt.msuzi_opt.items import MsuziOptProductItem, MsuziOptCatalogItem
from constants import IMAGE_PATH


class MsuziOptCrawlSpider(CrawlSpider):
    name = 'msuzi_opt_crawl'
    allowed_domains = ['msuzi-opt.ru']
    start_urls = [
                    'http://www.msuzi-opt.ru/catalog294_1.html',
                    'http://www.msuzi-opt.ru/catalog341_1.html',
                    'http://www.msuzi-opt.ru/catalog348_1.html',
                    'http://www.msuzi-opt.ru/catalog349_1.html',
                    'http://www.msuzi-opt.ru/catalog350_1.html',
                    'http://www.msuzi-opt.ru/catalog351_1.html',
                    'http://www.msuzi-opt.ru/catalog352_1.html',
                    'http://www.msuzi-opt.ru/catalog353_1.html',
                    'http://www.msuzi-opt.ru/catalog347_1.html',
                    'http://www.msuzi-opt.ru/catalog354_1.html'
                  ]

    rules = (
        Rule(LxmlLinkExtractor(restrict_css=('#goods_main h1 > a',)),
             callback='parse_product'),
        Rule(LxmlLinkExtractor(), callback='parse_catalog',),
        Rule(LxmlLinkExtractor(restrict_css=('#main > p:nth-child(2) > a',)),
             follow=True)
    )

    def parse_catalog(self, response):
        item = MsuziOptCatalogItem()
        soup = BeautifulSoup(response.text, 'lxml')
        item['url_catalog'] = response.url
        item['name_catalog'] = '::'.join([a.get_text(strip=True)
                                          for a in soup.select('a.title')])
        yield item

    def parse_product(self, response):
        item = MsuziOptProductItem()
        soup = BeautifulSoup(response.text, 'lxml')
        item['name'] = soup.find('h1').get_text(strip=True)
        item['referer'] = response.request.headers.get('Referer').decode()
        url_images, item['name_images'] = self.handler_photo_url(soup)
        item['props'], item['descr'] = self.handler_product_props(soup)
        for name_image, url_image in zip(item['name_images'], url_images):
            yield scrapy.Request(url_image, callback=self.parse_image,
                                 meta={'name_image': name_image})
        yield item

    @staticmethod
    def handler_photo_url(soup):
        try:
            photo_obj = soup.find(string=re.compile(r'Фото:'))
            hrefs = [a.get('href') for a in photo_obj.next_siblings
                     if isinstance(a, bs4.element.Tag)]
            url_images = [re.search(r",.*(http.*big.*[0-9]+.jpg)", href)
                          .group(1)
                          for href in hrefs]
            name_images = [re.search(r'.*(big.*[0-9]+.jpg).*', url_image)
                           .group(1)
                           for url_image in url_images]
        except AttributeError:
            url_image = soup.select_one('#jqzoom').get('href')
            name_image = url_image.split('/')[-1]
            url_images = [url_image]
            name_images = [name_image]
        return url_images, name_images

    @staticmethod
    def handler_product_props(soup):
        trs_goods_line = soup.select('.goods_line > table > tr')
        if len(trs_goods_line) == 6:
            prop_products_html = trs_goods_line[4].select('.rpad .rpad > tr')
            product_descr = [br.next.strip() for br in
                             trs_goods_line[5].find_all('br') if
                             br.next.strip()]
        elif len(trs_goods_line) == 5:
            prop_products_html = trs_goods_line[3].select('.rpad .rpad > tr')
            product_descr = [br.next.strip() for br in
                             trs_goods_line[4].find_all('br') if
                             br.next.strip()]
        else:
            return None, None
        products_prop_tds = [tr.select('td') for tr in prop_products_html]
        length_prop = len(products_prop_tds)
        product_props = []
        for products_prop_td in products_prop_tds:
            if length_prop > 1:
                product_prop = [td.get_text(strip=True)
                                for td in products_prop_td[1:]]
            if length_prop == 1:
                product_prop = [td.get_text(strip=True)
                                for td in products_prop_td[:-1]]
            product_props.append(product_prop)
        return product_props, product_descr

    @staticmethod
    def parse_image(response):
        os.makedirs(IMAGE_PATH, exist_ok=True)
        image_name = response.meta['name_image']
        image_path = os.path.join(IMAGE_PATH, image_name)
        with open(image_path, 'wb') as image_file:
            image_file.write(response.body)


def run_crawl():
    """Run crawler"""
    crawler_setting = Settings()
    crawler_setting.setmodule(my_setting)
    process = CrawlerProcess(settings=crawler_setting)
    process.crawl(MsuziOptCrawlSpider)
    process.start()


if __name__ == '__main__':
    run_crawl()
