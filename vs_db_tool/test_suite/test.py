from ..sqlalchemy.db_support.mssql import MsSql
from ..sqlalchemy.db_support.create_session import Session
from ..sqlalchemy.db_support.init_params import Init_Params
from ..orm.srm.general.pd_licenseasset import pd_licenseasset

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///:memory:', echo=True)


srm_db_conn_pp = MsSql()

params_pp = Init_Params()
params_pp.DB = "shc_srm_50x_pp_1"
params_pp.HOST = "10.20.233.103"
params_pp.UID = "ad"
params_pp.PWD = "ca$hc0w"

srm_engine_pp = srm_db_conn_pp(params_pp)


create_session = Session(srm_engine_pp)
session = create_session()

print(session.query(pd_licenseasset).first())
