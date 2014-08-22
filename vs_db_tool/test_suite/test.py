from ..sqlalchemy.db_support.mssql import MsSql
from ..sqlalchemy.db_support.create_session import Session
from ..sqlalchemy.db_support.init_params import Init_Params
from ..orm.srm.general.pd_licenseasset import pd_licenseasset
from ..orm.srm.general.pd_licensereservation import pd_licensereservation

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *

engine = create_engine('sqlite:///:memory:', echo=True)


srm_db_conn_pp = MsSql()

params_pp = Init_Params()
params_pp.DB = "play_db"
params_pp.HOST = "10.20.233.103"
params_pp.UID = "ad"
params_pp.PWD = "ca$hc0w"

srm_engine_pp = srm_db_conn_pp(params_pp)


create_session = Session(srm_engine_pp)
session = create_session()

print(session.query(pd_licenseasset).first())
print(session.query(pd_licensereservation).first())

#value = session.query(pd_licensereservation).first()

#session.delete(value)

metadata = MetaData(bind=srm_engine_pp)

#pd = Table('pd_licenseasset', metadata, autoload=True)

#for t in metadata.sorted_tables:
#    print(t.name)
