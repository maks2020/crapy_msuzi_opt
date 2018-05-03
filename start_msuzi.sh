#!/bin/sh
sleep 30
/env_app/bin/python /app/msuzi_opt/msuzi_opt/spiders/msuzi_opt_crawl.py
/env_app/bin/python /app/msuzi_opt/msuzi_opt/report.py
