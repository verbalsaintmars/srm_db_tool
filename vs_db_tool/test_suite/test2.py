from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..orm.srm.general.pd_licenseasset import pd_licenseasset


engine = create_engine(r'mssql+pyodbc://ad:ca$hc0w@10.20.233.103:1433/shc_srm_50x_pp_1')

Session = sessionmaker(bind=engine)

session = Session()


