from ..sqlalchemy.db_support.init_params import Init_Params
from ..sqlalchemy.make_conn import MakeConn

from ..exception.predefined import GeneralException
from ..exception.predefined import SaException

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
    """
    Each TableOb instance uses single sqlite db file.
    Each TableOb instance has it's own connection to sqlite db file
    Each TableOb instance can restore from different version of table
    """

    def __enter__(this):
        return this

    def __exit__(this, exc_type, exc_value, exc_tb):
        if exc_type is None:
            # print('exited normally\n')
            this.Dispose()
        else:
            # print('raise an exception!', exc_type)
            this.Dispose()
            return False

    def __init__(this, a_dbfile=None, a_default_path=None):
        """
        a_dbfile is the sqlite db file
        """
        this.params = Init_Params()
        this.params.DBTYPE = 'sqlite'

        if a_dbfile is None:
            this.params.PATH =\
                DbFileOp(a_default_path=a_default_path).NextFileName()
        else:
            from os.path import join
            this.params.PATH =\
                join(a_default_path if a_default_path is not None else "",
                     a_dbfile)

        this.conn = MakeConn(this.params)

        this.Base = declarative_base()
        this.Base.metadata.bind = this.conn.GetEngine()
        this.metadata = this.Base.metadata

        # cache
        # table name : table class, table class has version info from it's name
        this.tables = {}

    def _ConvertType(this, a_type):
        """
        Convert from different Database's
            column type to compatible sqlite column type
        """
        # General Types

        # Latin1_General_CI_AS issue
        from sqlalchemy import VARCHAR as General_VARCHAR
        from sqlalchemy import UnicodeText

        # DB Specific types
        # MS SQL
        from sqlalchemy.dialects.mssql import VARCHAR as MSSQL_VARCHAR
        from sqlalchemy.dialects.mssql import NTEXT as MSSQL_NTEXT

        try:
            result = {
                MSSQL_NTEXT: UnicodeText(),
                MSSQL_VARCHAR: General_VARCHAR(255)
            }[type(a_type)]
            return result
        except KeyError:
            # print("hhhh" + str(type(a_type)))
            return a_type

    def _ReflectTable(this, a_table_name):
        """
        Reflect the a_table_name_xxxx (xxxx is version) schema(s)
            base on this instance's engine connetion
        """

        this.metadata.reflect()

        pat = re.compile(a_table_name, re.IGNORECASE)

        return sorted(
            [str(t.name) for t in this.metadata.tables.values()
             if pat.search(t.name) is not None],
            key=str.lower,
            cmp=comp_table_name)

    def Backup(this, a_value_list, a_site="pp"):
        """
        a_value_list : list of orm objects, which have table information
        a_site : pp for primary , ss for secondary, or other value
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
                """
                tablename_{a_site}_xxxx (xxxx is version)
                """
                table_class = this.tables[str(o.__table__.name) + a_site]

            except AttributeError as e:
                print(
                    GeneralException(
                        "I0",
                        "Backup accept only list of ORM objects "
                        "which contains table information",
                        __name__))
                return

            except KeyError:
                """
                tablename has not been cached/used
                """
                # tnl : table name list
                tnl = this._ReflectTable(str(o.__table__.name + "_" + a_site))

                # tn : table name
                tn = None
                version = None

                if tnl.__len__() > 0:
                    """
                    if has tablename in this sqlite db file,
                    generate a new tablename table with version bumped + 1
                    """
                    version = int(pat.search(tnl[-1]).group('version')) + 1
                    tn = str(o.__table__.name + "_" + a_site + "_" +
                             str(version).zfill(4))
                else:
                    """
                    else the version of this tablename in this sqlite db file
                    is 1
                    """
                    version = 1
                    tn = str(o.__table__.name + "_" + a_site + "_" +
                             str(version).zfill(4))

                # table = Table(tn, this.metadata)
                """
                safe the original table name.
                then modify to the version added table name.
                purpose is for copying the metadata
                """
                orig_name = o.__table__.name
                o.__table__.name = tn
                """
                make a new table into this sqlite db file
                """
                table = o.__table__.tometadata(this.metadata)
                """
                save the original table name back.
                """
                o.__table__.name = orig_name
                # table.name = tn

                # convert column type from
                #   different database to sqlite supported type
                for c in table.columns.values():
                    #print("hahahahha: " + c.type)
                    c.type = this._ConvertType(c.type)
                    """
                    if type(c.type) is VARCHAR:
                        c.type = this._ConvertType(
                            VARCHAR)(255)
                    """

                # hack : do not create index, prevent same indexname
                # created against different table_000x
                table.indexes = set()

                # for col in o.__table__.c:
                #     table.append_column(col.copy())
                """
                cache the ORM class object
                """
                this.tables[str(o.__table__.name) + a_site] =\
                    type(tn, (this.Base,), {'__table__': table})

                table_class = this.tables[str(o.__table__.name) + a_site]

                this.metadata.create_all()

            except Exception as e:
                print(
                    GeneralException(
                        "U0", "Shouldn't be here...", __name__))
                return

            # create ORM object against sqlite table
            # table_obj = this.tables[str(o.__table__.name) + a_site]()
            table_obj = table_class()

            for col in o.__table__.c:
                setattr(table_obj, col.name, getattr(o, col.name))

            try:
                """
                backup data into table
                """
                session.add(table_obj)
            except Exception as e:
                print(
                    SaException(
                        "SA",
                        "session.add ORM object failed", __name__, e))
                return
        try:
            session.commit()
        except Exception as e:
            print(SaException("SA", "session.commit failed", __name__, e))
            return

    def ListTables(this):
        """
        List this TableOp instance's sqlite db file's tables
        """
        this.metadata.reflect()
        return this.metadata.tables

    def ListVersion(this, a_datum_obj, a_site='pp'):
        """
        Pass in a ORM object, will list the table version for this
            ORM object's table name
        """
        table_in = a_datum_obj.__table__

        tnl = this._ReflectTable(str(table_in.name + "_" + a_site))

        pat = re.compile(a_site + "_(?P<version>\d{4})")

        versions = []

        for tn in tnl:
            result = pat.search(tn)
            if result:
                versions.append(int(result.group('version')))

        return tuple(versions)

    def Restore(this, a_datum_obj, a_site="pp", a_version=None):
        """
        Passes in an ORM object. Base on the table information
            in the ORM object, return all data/rows of this table.
        If a_version is None, will use the latest version of this table.
        """
        pat = re.compile(a_site + "_(?P<version>\d{4})")

        table_in = a_datum_obj.__table__

        tnl = this._ReflectTable(str(table_in.name + "_" + a_site))

        table_c = None

        if a_version is not None and type(a_version) is int:
            pat = re.compile(
                a_site + "_(?P<version>" + str(a_version).zfill(4) + ")")
            result = [tn for tn in tnl if pat.search(tn) is not None]

            if result.__len__() == 1:
                table = this.metadata.tables[result[0]]

                from srm_db_tool.orm.srm import gentable
                table_c =\
                    gentable.GenTable(str(table.name), this.conn.GetEngine())

            else:
                """
                print(GeneralException(
                    'O0',
                    "No version {} of table : {} found".format(
                        a_version,
                        table_in.name),
                    __name__))
                """
                return None
        else:
            try:
                table_c = this.tables[str(table_in.name) + a_site]
            except KeyError as e:
                if tnl.__len__() > 0:
                    tn = str(table_in.name + "_" + a_site + "_" + str(
                        int(pat.search(tnl[-1]).group('version'))).
                        zfill(4))

                    table = this.metadata.tables[tn]

                    from srm_db_tool.orm.gentable import GenTable
                    table_c =\
                        GenTable(
                            str(table.name),
                            this.conn.GetEngine())

                else:
                    """
                    print(GeneralException(
                        'O0',
                        "Table : {}"
                        " has never been backedup"
                        " in this sqlite db : {}".
                        format(table_in.name, this.params.PATH),
                        __name__))
                    """
                    return None

        session = this.conn.GetSession()

        result = None
        try:
            result = session.query(table_c).all()
        except Exception as e:
            print(
                SaException(
                    "SA",
                    "session.query failed against sqlite", __name__, e))
            return None
        else:
            if result.__len__() == 0:
                return None
            else:
                return result

    def Remove(this, a_datum_obj):
        session = this.conn.GetSession()

        try:
            session.delete(a_datum_obj)
        except Exception as e:
            print(
                SaException(
                    "SA",
                    "session.delete failed against sqlite",
                    __name__,
                    e))

        try:
            session.commit()
        except Exception as e:
            print(
                SaException(
                    "SA",
                    "session.commit failed against sqlite",
                    __name__,
                    e))

    def Debug(this):
        return this.metadata.tables
        # return this.conn

    def Dispose(this):
        """
        TODO:
            Make use for Context Managers
        """
        this.conn.Dispose()
