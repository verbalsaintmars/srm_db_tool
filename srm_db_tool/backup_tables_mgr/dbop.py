from ..sqlalchemy.db_support.init_params import Init_Params
from ..sqlalchemy.make_conn import MakeConn

from ..exception.predefined import GeneralException
from ..exception.predefined import SaException

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
    """
    Each TableOb uses single sqlite db.
    Each TableOb uses backup intp single table version and will remember that version
    Each TableOb uses can restore from different version of table
    """

    def __init__(this, a_dbfile=None):
        this.params = Init_Params()
        this.params.DBTYPE = 'sqlite'

        if a_dbfile is None:
            this.params.PATH = DbFileOp().NextFileName()
        else:
            this.params.PATH = a_dbfile

        this.conn = MakeConn(this.params)

        this.Base = declarative_base()
        this.Base.metadata.bind = this.conn.GetEngine()
        this.metadata = this.Base.metadata

        # cache
        # table name : table class, table class has version info from it's name
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
        a_data_obj : a list of orm objects, which should have table information
        a_site : pp for primary , ss for secondary
        """
        try:
            if type(a_value_list) is not list:
                raise GeneralException(
                    "I0", "Backup accept only list of ORM objects", __name__)
        except GeneralException as e:
            print(e)
            return

        pat = re.compile(a_site + "_(?P<version>\d{4})")

        session = this.conn.GetSession()

        for o in a_value_list:
            table_class = None

            try:
                table_class = this.tables[str(o.__table__.name) + a_site]

            except AttributeError as e:
                print(
                    GeneralException(
                        "I0", "Backup accept only list of ORM objects", __name__))
                return

            except KeyError:
                # tnl : table name list
                tnl = this.ReflectTable(str(o.__table__.name + "_" + a_site))

                # tn : table name
                tn = None
                version = None

                if tnl.__len__() > 0:
                    version = int(pat.search(tnl[-1]).group('version')) + 1
                    tn = str(o.__table__.name + "_" + a_site + "_" +\
                        str(version).zfill(4))
                else:
                    version = 1
                    tn = str(o.__table__.name + "_" + a_site + "_" +\
                        str(version).zfill(4))


                # table = Table(tn, this.metadata)
                orig_name = o.__table__.name
                o.__table__.name = tn
                table = o.__table__.tometadata(this.metadata)
                o.__table__.name = orig_name
                table.name = tn

                # convert type from different database to sqlite supported type
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

            except Exception as e:
                print(
                    GeneralException(
                        "U0", "Shouldn't be here...", __name__))
                return

            # create ORM object against sqlite table
            table_obj = this.tables[str(o.__table__.name) + a_site]()
            for col in o.__table__.c:
                setattr(table_obj, col.name, getattr(o, col.name))
            try:
                session.add(table_obj)
            except Exception as e:
                print(SaException("SA", "session.add ORM object failed", __name__, e))
                return
        try:
            session.commit()
        except Exception as e:
            print(SaException("SA", "session.commit failed", __name__, e))
            return

    def ListTables(this):
        this.metadata.reflect()
        return this.metadata.tables

    def ListVersion(this, a_datum_obj, a_site='pp'):
        table_in = a_datum_obj.__table__

        tnl = this.ReflectTable(str(table_in.name + "_" + a_site))

        pat = re.compile(a_site + "_(?P<version>\d{4})")

        versions = []

        for tn in tnl:
            result = pat.search(tn)
            if result:
                versions.append(int(result.group('version')))

        return tuple(versions)

    def Restore(this, a_datum_obj, a_site="pp", a_version=None):
        """
        1. inspect the single obj's table
        2. load latest table
        3. select all and return the result
        """
        pat = re.compile(a_site + "_(?P<version>\d{4})")

        table_in = a_datum_obj.__table__

        tnl = this.ReflectTable(str(table_in.name + "_" + a_site))

        table_c = None

        if a_version is not None and type(a_version) is int:
            pat = re.compile(
                a_site + "_(?P<version>" + str(a_version).zfill(4) + ")")
            result = [tn for tn in tnl if pat.search(tn) is not None]

            if result.__len__() == 1:
                table = this.metadata.tables[result[0]]

                from srm_db_tool.orm.srm import base
                table_c = base.GenTable(str(table.name), this.conn.GetEngine())

            else:
                print(GeneralException(
                    'O0',
                    "No version {} of table : {} found".format(
                        a_version,
                        table_in.name),
                    __name__))
                return
        else:
            try:
                table_c = this.tables[str(table_in.name) + a_site]
            except KeyError as e:
                if tnl.__len__() > 0:
                    tn = str(table_in.name + "_" + a_site + "_" + str(
                        int(pat.search(tnl[-1]).group('version'))).\
                            zfill(4))

                    table = this.metadata.tables[tn]

                    from srm_db_tool.orm.srm import base
                    table_c = base.GenTable(str(table.name), this.conn.GetEngine())

                else:
                    print(GeneralException(
                        'O0',
                        "Table : {}"
                        " has never been backedup"
                        " in this sqlite db : {}".\
                         format(table_in.name, this.params.PATH),
                        __name__))
                    return None

        session = this.conn.GetSession()

        result = None
        try:
            result = session.query(table_c).all()
        except Exception as e:
            print(SaException("SA", "session.query failed against sqlite", __name__, e))
            return
        else:
            return result

    def Remove(this, a_datum_obj):
        session = this.conn.GetSession()

        try:
            session.delete(a_datum_obj)
        except Exception as e:
            print(SaException("SA", "session.delete failed against sqlite", __name__, e))

        try:
            session.commit()
        except Exception as e:
            print(SaException("SA", "session.commit failed against sqlite", __name__, e))

    def Debug(this):
        return this.metadata.tables
        # return this.conn

    def Dispose(this):
        """
        TODO:
            Make use for Context Managers
        """
        this.conn.GetEngine().dispose()
