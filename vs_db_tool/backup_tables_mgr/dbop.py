from ..sqlalchemy.db_support.init_params import Init_Params
from ..sqlalchemy.make_conn import MakeConn
from ..exception.predefined import MODULE_EXCEPT_FORMAT
from .fm import DbFileOp

import re

from sqlalchemy.ext.declarative import declarative_base

# General Types
from sqlalchemy import VARCHAR # Latin1_General_CI_AS
from sqlalchemy import UnicodeText

# DB Specific types
# MS SQL
from sqlalchemy.dialects.mssql import NTEXT



# tableName_pp_0001
# tableName_ss_0001
def comp_table_name(lhs, rhs):
    pat = re.compile("_(?P<version>\d{4})")
    lhs_m = pat.search(lhs)
    rhs_m = pat.search(rhs)

    if int(lhs_m.group('version')) < int(rhs_m.group('version')):
        return -1
    else:
        return 1


class TableOp(object):
    def __init__(this, a_dbfile=None):
        params = Init_Params()
        params.DBTYPE = 'sqlite'

        if a_dbfile is None:
            params.PATH = DbFileOp().NextFileName()
        else:
            params.PATH = a_dbfile

        this.conn = MakeConn(params)

        this.Base = declarative_base()

        this.Base.metadata.bind = this.conn.GetEngine()
        this.metadata = this.Base.metadata

        # cache
        this.tables = {}

    def ConvertType(this, a_type):
        return {
                NTEXT: UnicodeText,
                VARCHAR: VARCHAR
               }[a_type]


    def ReflectTable(this, a_table_name):

        this.metadata.reflect()

        pat = re.compile(a_table_name, re.IGNORECASE)

        return sorted(
            [str(t.name) for t in this.metadata.tables.values()
             if pat.search(t.name) is not None],
            key=str.lower,
            cmp=comp_table_name)

    def Backup(this, a_value_list, a_site="pp"):
        """
        a_data_obj : a list of orm objects
        a_site : pp for primary , ss for secondary
        """
        if type(a_value_list) is not list:
            print("a_value_list must be a list of table class objects")
            return None

        pat = re.compile(a_site + "_(?P<version>\d{4})")

        session = this.conn.GetSession()

        for o in a_value_list:
            table_class = None

            try:
                table_class = this.tables[str(o.__table__.name) + a_site]

            except AttributeError as e:
                print(MODULE_EXCEPT_FORMAT.format(__name__, e))
                print("a_value_list must be a list of table class objects")

            except KeyError:
                tnl = this.ReflectTable(str(o.__table__.name + "_" + a_site))
                if tnl.__len__() > 0:
                    tn = str(o.__table__.name + "_" + a_site + "_" + str(
                        int(pat.search(tnl[-1]).group('version')) + 1).
                        zfill(4))
                else:
                    tn = str(o.__table__.name + "_" + a_site + "_" + "0001")


                # table = Table(tn, this.metadata)
                table = o.__table__.tometadata(this.metadata)
                table.name = tn

                for c in table.columns.values():
                    if type(c.type) is NTEXT:
                        c.type = this.ConvertType(NTEXT)()
                    if type(c.type) is VARCHAR:
                        c.type = this.ConvertType(
                            VARCHAR)(255)

                # for col in o.__table__.c:
                #     table.append_column(col.copy())

                this.tables[str(o.__table__.name) + a_site] =\
                    type(tn, (this.Base,), {'__table__': table})

                # hack : do not create index, prevent same indexname
                # created against different table_000x
                table.indexes = set()

                this.Base.metadata.create_all()

            except e:
                print(MODULE_EXCEPT_FORMAT.format(__name__, e))


            table_obj = this.tables[str(o.__table__.name) + a_site]()

            for col in o.__table__.c:
                setattr(table_obj, col.name, getattr(o, col.name))

            session.add(table_obj)

        session.commit()

    def ListTables(this):
        this.metadata.reflect()
        return this.metadata.tables

    def Restore(this, a_datum_obj, a_site="pp"):
        """
        1. inspect the single obj's table
        2. load latest table
        3. select all and return the result
        """
        pat = re.compile(a_site + "_(?P<version>\d{4})")

        table_in = a_datum_obj.__table__

        tnl = this.ReflectTable(str(table_in.name + "_" + a_site))
        tn = None

        if tnl.__len__() > 0:
            tn = str(table_in.name + "_" + a_site + "_" + str(
                int(pat.search(tnl[-1]).group('version'))).
                zfill(4))
        else:
            return None

        table = this.metadata.tables[tn]

        from vs_db_tool.orm.srm import base
        table_c = base.GenTable(str(table.name), this.conn.GetEngine())

        session = this.conn.GetSession()

        return session.query(table_c).all()

    def Remove(this, a_datum_obj):
        session = this.conn.GetSession()
        session.delete(a_datum_obj)
        session.commit()

    def Debug(this):
        return this.conn

    def Dispose(this):
        """
        TODO:
            Make use for Context Managers
        """
        this.conn.GetEngine().dispose()
