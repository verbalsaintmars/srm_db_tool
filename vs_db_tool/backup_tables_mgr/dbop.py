from ..sqlalchemy.db_support.init_params import Init_Params
from ..sqlalchemy.make_conn import MakeConn
from .fm import DbFileOp

import re

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

    def Backup(this, a_data_obj, a_site="pp"):
        """
        a_data_obj : a list of orm objects
        a_site : pp for primary , ss for secondary

        TODO:
        Update passing in a_data_obj.
        Which means, can't use just simple copy row data
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

                # table = Table(tn, this.metadata)
                table = o.__table__.tometadata(this.metadata)
                table.name = tn

                # for col in o.__table__.c:
                #     table.append_column(col.copy())

                this.Base.metadata.create_all()

            TheTable = type(tn, (this.Base,),
                            {'__table__': table})

            table_obj = TheTable()

            for col in o.__table__.c:
                setattr(table_obj, col.name, getattr(o, col.name))

            session = this.conn.GetSession()
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

        session = this.conn.GetSession()

        return session.query(table).all()

    def Debug(this):
        return this.conn

    def Dispose(this):
        """
        TODO:
            Make use for Context Managers
        """
        this.conn.GetEngine().close()
