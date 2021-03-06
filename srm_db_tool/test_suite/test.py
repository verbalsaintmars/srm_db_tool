from ..sqlalchemy.db_support.mssql import MsSql
from ..sqlalchemy.db_support.sqlite import Sqlite
from ..sqlalchemy.db_support.create_session import Session
from ..sqlalchemy.db_support.init_params import Init_Params
from ..sqlalchemy.make_conn import MakeConn

"""
# Create a parameters
params_pp = Init_Params()
params_pp.DBTYPE = 'sqlite'
params_pp.PATH = "/tmp/test.db"

# Use MakeConn to create engine as well as Session object
conn = MakeConn(params_pp)

# create fake table
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import Column, Integer, String
from sqlalchemy.types import Text


class TestTable(Base):
    __tablename__ = "test_table"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(Text(convert_unicode=True))

    def __repr__(self):
        return "<User(name='%s', fullname='%s', password='%s')>" % (
            self.name, self.fullname, self.password)


TestTable.metadata.create_all(conn.GetEngine())  # create schema into /tmp/test.db

# After create table test_table, we'll see that how convenient
# sqlalchemy could reflect the table schema and for us ready to use

# with our design, we could get the table by module name and that's it!
from ..orm.srm import test_table as the_test_table

Test_table_class = the_test_table.GetTable(conn.GetEngine())

data_1 = Test_table_class(name="verbalsaint", fullname='i am verbalsaint', password='hahah')

data_2 = Test_table_class(name="verbalsaint2", fullname='i am verbalsaint2',
                          password='hahah2')

data_3 = Test_table_class(name="verbalsaint3", fullname='i am verbalsaint3',
                          password='hahah3')

session = conn.GetSession()

session.add_all([data_1, data_2, data_3])

result1 = session.query(Test_table_class).all()

ttable = result1[0].__table__
"""

"""
reulst2 = session.query(Test_table_class).order_by(Test_table_class.id).all()

from sqlalchemy.orm import aliased
test_table_alias = aliased(Test_table_class, name='testtable_alias')
reulst3 = session.query(test_table_alias,
        test_table_alias.id).order_by(test_table_alias.id).all()


reulst4 = session.query(Test_table_class).filter().first()

from ..backup_tables_mgr import dbop
from ..backup_tables_mgr import fm

tableop = dbop.TableOp()
tableop.Backup(result1)
tableop.Dispose()

dbfileop = fm.DbFileOp()
filenm = dbfileop.LatestFileName()

tableop2 = dbop.TableOp(filenm)
result2 = tableop2.Restore(Test_table_class)
tableop2.Dispose()

dbfileop.RemoveFiles(filenm)
"""


######################################
params_hq = Init_Params()
params_hq.DBTYPE = 'mssql'
params_hq.HOST = '10.20.233.103'
params_hq.UID = 'ad'
params_hq.PWD = 'ca$hc0w'
params_hq.DB = '01_HQ'

HQconn = MakeConn(params_hq)
from ..orm.srm import pdr_planproperties
from ..orm.srm import pdr_plancontents
from ..orm.srm import g_do_array
from ..orm.srm import g_string_array

#pdr_planproperties_c = pdr_planproperties.GetTable(HQconn.GetEngine())
g_do_array_c = g_do_array.GetTable(HQconn.GetEngine())
g_string_array_c = g_string_array.GetTable(HQconn.GetEngine())
#g_do_array.GetTable(HQconn.GetEngine())

HQsession = HQconn.GetSession()

#HQResult = HQsession.query(pdr_planproperties_c).all()
HQResult = HQsession.query(g_do_array_c).all()
HQResult2 = HQsession.query(g_string_array_c).all()
ttable2 = HQResult[0].__table__

from ..backup_tables_mgr import dbop
from ..backup_tables_mgr import fm

tableop = dbop.TableOp()
tableop.Backup(HQResult)
re = tableop.Restore(g_do_array_c)

tableop.Backup(HQResult2)
re2 = tableop.Restore(g_string_array_c)


params_rh = Init_Params()
params_rh.DBTYPE = 'mssql'
params_rh.HOST = '10.20.233.103'
params_rh.UID = 'ad'
params_rh.PWD = 'ca$hc0w'
params_rh.DB = 'RH_902'

"""
User.metadata.create_all(conn.GetEngine())  # create schema into /tmp/test.db

data_1 = User(id=42, name='universe', fullname='verbalsaint', password='1234')

session = conn.GetSession()

session.add(data_1)
"""

"""
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

Base = declarative_base()

class ppd_licenseasset(Base):
   __table__ = Table('pd_licenseasset', metadata, autoload=True)

   def __str__(this):
      data = {col.name : getattr(this, col.name) for col in this.__table__.c}
      str_data = ""
      for col in this.__table__.c:
         str_data += "{" + col.name + "} : " + str(data[col.name]) + ", "
      return str_data


result = session.query(ppd_licenseasset).first()


tt = Table('pd_licenseasset', metadata, autoload=True)

#pd = Table('pd_licenseasset', metadata, autoload=True)

#for t in metadata.sorted_tables:
#    print(t.name)
"""
