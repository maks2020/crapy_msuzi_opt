#!/bin/sh
sleep 30
/env_app/bin/python /app/book_country/book_country/spiders/kanc_spider.py
/env_app/bin/python /app/book_country/book_country/report.py
