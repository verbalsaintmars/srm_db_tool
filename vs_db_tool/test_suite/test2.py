from sqlalchemy import *
from sqlalchemy.orm import create_session
from sqlalchemy.ext.declarative import declarative_base

import logging

logging.basicConfig(filename=r'/tmp/db.log')
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)



engine = \
create_engine(r'mssql+pyodbc://ad:ca$hc0w@10.20.233.103:1433/play_db?LANGUAGE=us_english',
        echo=False, convert_unicode=True)

metadata = MetaData(bind=engine, schema='ad', quote_schema=True)

dr_product_info = Table('dr_product_info', metadata, Column('name', String(255),
    primary_key=True), Column('value', String(255)), autoload=True)



