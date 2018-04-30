# -*- coding: utf-8 -*-

from openpyxl import Workbook

from book_country.pipelines import Category, Product, BookCountryPipeline


class Report(BookCountryPipeline):
    def __init__(self, name_file):
        super().__init__()
        self.name_file = name_file

    def create_report(self):
        wb = Workbook(write_only=True)
        sh = wb.create_sheet(title='report')
        datas = self.session.query(Product).join(Category).order_by(Product.id)
        for item in datas:
            data = [item.id, item.name_product, item.code_product,
                    item.price, item.manufacturer, item.kind,
                    item.category.category, item.status,
                    'http://194.67.206.56:8090/images_kanc/%s'
                    % item.image_name]
            print(data)
            sh.append(data)
        wb.save(self.name_file)


if __name__ == '__main__':
    report = Report('report.xlsx')
    report.create_report()