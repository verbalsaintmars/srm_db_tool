from ..sqlalchemy.db_support.init_params import Init_Params
from ..sqlalchemy.make_conn import MakeConn
from .fm import DbFileOp

import re
from sqlalchemy import Table, MetaData
from sqlalchemy.ext.declarative import declarative_base


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
        """
        this.table_obj = a_table_obj
        this.dbfile = a_dbfile
        this.table = a_table_obj.__table__ if a_table_obj is not None else \
            a_table
        """
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

        this.tables = {}

    def ReflectTable(this, a_table_name):

        this.metadata.reflect()

        pat = re.compile(a_table_name, re.IGNORECASE)

        return sorted(
            [str(t.name) for t in this.metadata.tables.values()
             if pat.search(t.name) is not None],
            key=str.lower,
            cmp=comp_table_name)
        """
        print("sshhh")
        print(metadata.tables)
        print(type(metadata.tables))
        print(dir(metadata.tables))
        print(metadata.tables.values())
        """

    def Backup(this, a_data_obj, a_site="pp"):
        """
        a_data_obj : a list of orm objects
        a_site : pp for primary , ss for secondary

        1. group data_obj by tables

        """

        pat = re.compile(a_site + "_(?P<version>\d{4})")

        for o in a_data_obj:
            tn = None

            try:
                tn = this.tables[str(o.__table__.name)]
            except:
                tnl = this.ReflectTable(str(o.__table__.name + "_" + a_site))
                if tnl.__len__() > 0:
                    tn = str(o.__table__.name + "_" + a_site + "_" + str(
                        int(pat.search(tnl[-1]).group('version')) + 1).
                        zfill(4))
                else:
                    tn = str(o.__table__.name + "_" + a_site + "_" + "0001")

                this.tables[str(o.__table__.name)] = tn

            table = Table(tn, this.metadata)

            for col in o.__table__.c:
                table.append_column(col.copy())

            this.Base.metadata.create_all()

            TheTable = type(tn, (this.Base,),
                            {'__table__': table})

            table_obj = TheTable()

            for col in o.__table__.c:
                setattr(table_obj, col.name, getattr(o, col.name))

            session = this.conn.GetSession()
            session.add(table_obj)
            session.commit()

        # apply schema naming rule
        # 1. reflect table inside db file
        # 2. table name format:
        # tableName_pp_0001
        # tableName_ss_0001

    def ListTables(this):
        this.metadata.reflect()
        return this.metadata.tables

    def SelectAll(this, a_table_class, a_site="pp"):
        sorted(
            [t for t in this.metadata.tables.values()],
            key=str.lower,
            cmp=comp_table_name)

        tnl = this.ReflectTable(
            str(a_table_class.__table__.name + "_" + a_site))

        tn = None

        if tnl.__len__() > 0:
            tn = tnl[-1]
            table = Table(tn, this.metadata)

        else:
            return None
            
        

    def Debug(this):
        return this.conn
