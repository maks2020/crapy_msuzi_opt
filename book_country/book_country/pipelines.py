# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from constants import PG_DB_NAME, PG_PASSWORD, PG_SERVER_IP, PG_PORT, PG_USER

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    category = Column(String)
    product = relationship('Product', back_populates='category')


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name_product = Column(String)
    code_product = Column(String)
    price = Column(Float)
    manufacturer = Column(String)
    kind = Column(String)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship('Category', back_populates='product')
    image_name = Column(String)
    status = Column(String)


class BookCountryPipeline(object):
    def __init__(self):
        self.eng = self.connect(PG_USER, PG_PASSWORD, PG_DB_NAME)
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
        query_category = (self.session.query(Category)
                          .filter(Category.category == item['category']))
        state_category = self.session.query(query_category.exists()).scalar()
        if state_category is False:
            category = Category(category=item['category'])
        else:
            category = query_category.one()
        query_product = (self.session.query(Product)
                         .filter(Product.name_product == item['name_product']))
        state_product = self.session.query(query_product.exists()).scalar()
        if state_product is False:
            product = Product(name_product=item['name_product'],
                              code_product=item['code_product'],
                              price=item['price'],
                              manufacturer=item['manufacturer'],
                              kind=item['kind'],
                              image_name=item['image_name'],
                              status=item['status'])
            category.product.append(product)
            self.session.add(category)
            self.session.commit()
        elif (item['status'] != query_product.status or
              item['price'] != query_product.price):
            if item['status'] != query_product.status:
                query_product.status = item['status']
            if item['price'] != query_product.price:
                query_product.price = item['price']
            self.session.commit()
        else:
            print('Product %s is exist' % item['name_product'])
        return item

