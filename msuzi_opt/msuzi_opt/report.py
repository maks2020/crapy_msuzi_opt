# -*- coding: utf-8 -*-

from collections import defaultdict

from openpyxl import Workbook

from pipelines import Image, Product, Catalog, SizePrice, MsuziOptPipeline


class Report(MsuziOptPipeline):
    def __init__(self):
        super().__init__()
        self.name_file = 'report.xlsx'

    def get_data(self):
        products = self.session.query(Product.name, SizePrice.size,
                                            SizePrice.price).join(
            SizePrice).all()
        d_1 = defaultdict(list)
        for code_name, size_color, price in products:
            d_1[code_name].append((size_color, price))
        results = []
        wb = Workbook(write_only=True)
        sh = wb.create_sheet(title='report')
        for code_name, item in d_1.items():
            product_images = (self.session.query(Image.name, )
                              .join(Product).filter(Product.name == code_name)
                              .all())
            product_images = ['http://194.67.206.56:8090/images_msuzi/%s' % image
                              for image, in product_images]
            catalog, = (self.session.query(Catalog.name_catalog).join(Product)
                        .filter(Product.name == code_name).one())
            description, = (self.session.query(Product.description)
                            .filter(Product.name == code_name).one())
            d_2 = defaultdict(list)
            for size_color, price in item:
                d_2[price].append(size_color)
            price, sizes = list(d_2.items())[0]
            results.append((code_name, ';'.join(sizes), price,
                            ' && '.join(product_images)))
            data = (code_name, description, ';'.join(sizes), price, catalog,
                    ' && '.join(product_images))
            print(data)
            sh.append(data)
        wb.save(self.name_file)


if __name__ == '__main__':
    report = Report()
    report.get_data()