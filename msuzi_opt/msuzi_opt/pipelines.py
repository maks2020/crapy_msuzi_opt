# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy import (create_engine, Column, String, Text, Integer, Float,
                        ForeignKey)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from constants import (PG_SERVER_IP, PG_PORT, PG_DB_NAME_MSUZI, PG_PASSWORD,
                       PG_USER)
import msuzi_opt.msuzi_opt as msuzi_opt

Base = declarative_base()


class Catalog(Base):
    __tablename__ = 'catalog'
    id = Column(Integer, primary_key=True)
    url_catalog = Column(String)
    name_catalog = Column(String)
    product = relationship('Product', back_populates='catalog')


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    catalog_id = Column(Integer, ForeignKey('catalog.id'))
    catalog = relationship('Catalog', back_populates='product')
    image = relationship('Image', back_populates='product')
    size_price = relationship('SizePrice', back_populates='product')


class SizePrice(Base):
    __tablename__ = 'size_price'
    id = Column(Integer, primary_key=True)
    size = Column(Text)
    price = Column(Float)
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship('Product', back_populates='size_price')


class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship('Product', back_populates='image')


class MsuziOptPipeline(object):
    def __init__(self):
        self.eng = self.connect(PG_USER, PG_PASSWORD, PG_DB_NAME_MSUZI)
        session = sessionmaker()
        self.session = session(bind=self.eng)
        Base.metadata.create_all(self.eng)

    @staticmethod
    def connect(user, password, db,
                host=PG_SERVER_IP,
                port=PG_PORT):
        url = 'postgresql+psycopg2://%s:%s@%s:%s/%s' % (
            user,
            password,
            host,
            port,
            db
        )
        eng = create_engine(url, client_encoding='utf8')
        return eng

    def process_item(self, item, spider):
        if isinstance(item, msuzi_opt.items.MsuziOptCatalogItem):
            url_catalog = item['url_catalog'].split('_')[0]
            query_catalog = (self.session.query(Catalog)
                             .filter(Catalog.url_catalog == url_catalog))
            state_catalog = self.session.query(
                query_catalog.exists()).scalar()
            if state_catalog is False:
                catalog = Catalog(name_catalog=item['name_catalog'],
                                  url_catalog=url_catalog)
                self.session.add(catalog)
                self.session.commit()
            else:
                print(22222222, query_catalog.one().name_catalog)
                if (state_catalog is True and
                      (query_catalog.one().name_catalog is None or
                       query_catalog.one().name_catalog == '')):
                    query_catalog.one().name_catalog = item['name_catalog']
                    self.session.commit()
                    print(111111111, query_catalog.one().name_catalog)
        if isinstance(item, msuzi_opt.items.MsuziOptProductItem):
            name = item['name']
            code_product = item['descr'][0].split()[1]
            try:
                description = item['descr'][1]
            except IndexError as err:
                print('Error: %s' % err)
                description = None
            name_images = item['name_images']
            props = item['props']
            referer = item['referer']
            url_catalog = referer.split('_')[0]
            name_full = '%s %s' % (code_product, name)
            query_product = (self.session.query(Product)
                             .filter(Product.name == name_full))
            status_product = self.session.query(query_product.exists()).scalar()
            if status_product is False:
                query_catalog = (self.session.query(Catalog)
                                 .filter(Catalog.url_catalog == url_catalog))
                state_catalog = self.session.query(
                    query_catalog.exists()).scalar()
                if state_catalog is False:
                    catalog = Catalog(url_catalog=url_catalog,
                                      name_catalog=None)
                else:
                    catalog = query_catalog.one()
                product = Product(name=name_full, description=description)
                for name_image in name_images:
                    image = Image(name=name_image)
                    product.image.append(image)
                for size, price in props:
                    price = float(price.split()[0])
                    size_price = SizePrice(size=size, price=price)
                    product.size_price.append(size_price)
                catalog.product.append(product)
                self.session.add(catalog)
                self.session.commit()
            else:
                product = query_product.one()
                # size_all_db = set(self.session.query(SizePrice.size)
                #                   .join(Product)
                #                   .filter(Product.name == name_full).all())
                # print(size_all_db)
                # size_all_getting = set([(size,) for size, _ in props])
                # product_report = (self.session.query(Product.name,
                #                                      Product.description,
                #                                      Catalog.name_catalog,
                #                                      SizePrice,
                #                                      Image).join(Catalog).join(Image).join(SizePrice)
                #                   .filter(Product.name == name_full).all())
                for size, price in props:
                    query_size = (self.session.query(SizePrice).join(Product)
                                  .filter(Product.name == name_full, SizePrice.size == size))
                    state_size = (self.session.query(query_size.exists())
                                  .scalar())
                    if state_size is False:
                        size_price = SizePrice(size=size, price=price)
                        product.size_price.append(size_price)
                        self.session.add(product)
                        self.session.commit()
                    else:
                        size_price = query_size.one()
                        price = float(price.split()[0])
                        if price != size_price.price:
                            size_price.price = price
                            self.session.commit()
        return item

    def status_catalog_db(self, url_catalog):
        url_without_page = url_catalog.split('_')[0]
        query_catalog = (self.session.query(Catalog)
                         .filter(Catalog.url_catalog == url_without_page))
        return self.session.query(query_catalog.exists()).scalar()


