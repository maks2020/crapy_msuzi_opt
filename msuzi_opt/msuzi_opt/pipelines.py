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
import msuzi_opt

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
    price = Column(Float)
    sizes = Column(Text)
    catalog_id = Column(Integer, ForeignKey('catalog.id'))
    catalog = relationship('Catalog', back_populates='product')
    image = relationship('Image', back_populates='product')


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
            state_catalog = self.session.query(query_catalog.exists()).scalar()
            print(state_catalog)
            if state_catalog is False:
                catalog = Catalog(name_catalog=item['name_catalog'],
                                  url_catalog=url_catalog)
                self.session.add(catalog)
                self.session.commit()
            elif state_catalog is True and query_catalog.name_catalog is None:
                query_catalog.name_catalog = item['name_catalog']
                query_catalog.save()
                self.session.commit()
        return item
