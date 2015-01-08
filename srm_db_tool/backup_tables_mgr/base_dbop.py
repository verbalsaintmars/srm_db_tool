from srm_db_tool.backup_tables_mgr.meta_table import \
    meta_table_name, fixby_table_name, GenMetaTableParam

from srm_db_tool.backup_tables_mgr.module import Module

from srm_db_tool.sqlalchemy.db_support.init_params import Init_Params
from srm_db_tool.orm.gentable import GenTable
from srm_db_tool.exception.predefined import FixbyModuleException
from srm_db_tool.exception.predefined import SaException

from abc import ABCMeta, abstractmethod

from sqlalchemy import Table  # MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound


class BaseDbOp(object):
    __metaclass__ = ABCMeta

    def __init__(this):
        this.params = Init_Params()
        this.base = declarative_base()
        this.metadata = this.base.metadata

        this.meta_table_c = None
        this.fixby_table_c = None
        this.db_metadata = None

        this.table_cache = {}

    @abstractmethod
    def _convertType(this, a_type):
        """
        Different Database vendor has different types.
        You could provide type conversion in thie mem_fn
        """
        pass

    def _reflectTable(this, a_table_name):
        """
        Reflect the a_table_name schema(s)
            base on this instance's engine connetion
        """

        this.metadata.reflect()
        return this.metadata.tables[a_table_name]

    def _fetch_metadata(this):
        """
        Fetch meta_data from this database through meta_data table
        """
        if this.db_metadata is None:
            try:
                this.db_metadata = this.session.query(this.meta_table_c).one()
            except (MultipleResultsFound, NoResultFound, Exception) as exp:
                if exp.__class__ == MultipleResultsFound:
                    print(SaException(
                        'SA',
                        'More than 1 row found in srm_sqlite_meta_table',
                        'sqlitedbop.py',
                        exp))
                if exp.__class__ == NoResultFound:
                    this.db_metadata = this.meta_table_c()

    def _gen_meta_table_c(this, a_table_name, a_table=None):
        """
        Construct meta_table ORM type
        """

        table_param = None
        table_obj = None
        table_param = None

        table_name = \
            {"meta": meta_table_name, "fixby": fixby_table_name}[a_table_name]

        if a_table is not None:
            table_obj = a_table
        else:
            if a_table_name == "meta":
                table_param = GenMetaTableParam("meta")
            if a_table_name == "fixby":
                table_param = GenMetaTableParam("fixby")
            table_obj = Table(
                table_name,
                # MetaData(),
                this.metadata,
                *table_param.COLS)

        return GenTable(
            table_name,
            a_table=table_obj,
            a_base=this.base)

    def ListTables(this):

        """
        List db tables
        """
        this.metadata.reflect()
        return this.metadata.tables

    def Backup(this, a_value_list):
        """
        a_value_list : a list type of ORM objects
        """
        for o in a_value_list:
            table_class = None

            try:
                """
                Check is thie ORM object's type is cached before
                """
                table_class = this.table_cache[str(o.__table__.name)]

            except KeyError:
                """
                tablename has not been cached/used
                """

                """
                Create the ORM type schema into backuped Database
                """
                table = o.__table__.tometadata(this.metadata)

                # hack : do not create index, prevent same indexname
                # created against different table_000x
                table.indexes = set()
                """
                for i in table.indexes:
                    i.drop()
                """

                """
                Run _convertType: different Database has different type
                    conversion
                """
                for c in table.columns.values():
                    c.index = False
                    c.type = this._convertType(c.type)

                # for col in o.__table__.c:
                #     table.append_column(col.copy())
                """
                cache the ORM type object
                """
                this.table_cache[str(o.__table__.name)] =\
                    GenTable(
                        str(o.__table__.name),
                        a_table=table,
                        a_base=this.base)

                table_class = this.table_cache[str(o.__table__.name)]

                """
                Create the schema into the database
                """
                try:
                    this.metadata.create_all()
                except Exception as e:
                    print(
                        SaException(
                            "SA",
                            "metadata.create_all() failed", __name__, e))
                    return

            # create ORM object from ORM type
            table_obj = table_class()

            for col in o.__table__.c:
                """
                Copy data
                """
                setattr(table_obj, col.name, getattr(o, col.name))

            try:
                """
                backup data into table through ORM object
                """
                this.session.add(table_obj)
            except Exception as e:
                print(
                    SaException(
                        "SA",
                        "session.add ORM object failed", __name__, e))
                return
        try:
            """
            Commit data
            """
            this.session.commit()
        except Exception as e:
            print(SaException("SA", "session.commit failed", __name__, e))
            return

    def Restore(this, a_table_name):
        """
        a_table_name :
            which table needs to be restore from.
        """
        table_c = None

        try:
            """
            Check if this table's ORM type has been cached.
            """
            table_c = this.table_cache[a_table_name]
        except KeyError:
            try:
                table = this._reflectTable(a_table_name)
            except:
                return None
            table_c = GenTable(a_table_name, a_table=table, a_base=this.base)
            this.table_cache[a_table_name] = table_c

        result = None

        try:
            result = this.session.query(table_c).all()
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

    def Remove(this, a_table_name):
        """
        Remove data inside the table.
        Return number of rows being deleted.
        """
        if this.LOCK != 0:
            return

        table_c = None

        try:
            table_c = this.table_cache[a_table_name]
        except KeyError:
            """
            Get table object from this backuped database
            """
            table = this._reflectTable(a_table_name)
            """
            This table's ORM type
            """
            table_c = GenTable(a_table_name, a_table=table, a_base=this.base)
            """
            Cache it!
            """
            this.table_cache[a_table_name] = table_c

        return this.session.query(table_c).delete()

    def CheckAndCreateTable(this, a_create_meta_table=True):
        """
        Check if this sqlite db contains meta data tables.
        i.e meta table and fixby table
        The design of meta data table contains only 1 single entry.
        History of module manipulation is in Fixby table.

        If table does not exist in the current sqlite db file,
        will create the table(s) schema.
        """
        this.metadata.reflect()

        meta_table_result = filter(
            lambda t: str(t.name) == meta_table_name,
            this.metadata.tables.values())

        fixby_table_result = filter(
            lambda t: str(t.name) == fixby_table_name,
            this.metadata.tables.values())

        create_table_flag = 0

        if meta_table_result.__len__() == 0 and a_create_meta_table is True:
            """
            this sqlite db file does not contain meta table
            """
            this.meta_table_c = this._gen_meta_table_c("meta")
            this.meta_table_c.__table__.indexes = set()
            create_table_flag |= 1

        elif meta_table_result.__len__() != 0:
            this.meta_table_c = this._gen_meta_table_c(
                "meta",
                meta_table_result[0])

        if fixby_table_result.__len__() == 0 and a_create_meta_table is True:
            this.fixby_table_c = this._gen_meta_table_c("fixby")
            this.fixby_table_c.__table__.indexes = set()
            create_table_flag |= 2
        elif fixby_table_result.__len__() != 0:
            this.fixby_table_c = this._gen_meta_table_c(
                "fixby",
                fixby_table_result[0])

        if create_table_flag:
            this.base.metadata.create_all()

    def SetSrmVersion(this, a_version, a_force=False):
        if not a_version:
            return

        this._fetch_metadata()
        if this.db_metadata:
            if this.db_metadata.version is None:
                this.db_metadata.version = a_version
                this.db_metadata.lock = 0  # initial lock to false
                this.session.add(this.db_metadata)
                this.session.commit()

            if a_force is True:
                this.db_metadata.version = a_version
                this.session.commit()

    def GetSrmVersion(this):
        this._fetch_metadata()
        return this.db_metadata.version if this.db_metadata else None

    def SetDumpType(this, a_dump_type, a_force=False):
        if not a_dump_type:
            return

        this._fetch_metadata()
        if this.db_metadata:
            if this.db_metadata.dumpType is None:
                this.db_metadata.dumpType = str(a_dump_type)
                this.session.commit()

            if a_force is True:
                this.db_metadata.dumpType = str(a_dump_type)
                this.session.commit()

    def GetDumpType(this):
        this._fetch_metadata()
        dt_str = this.db_metadata.dumpType if this.db_metadata else None

        if dt_str is None:
            return None
        else:
            from srm_db_tool.backup_tables_mgr.dumptype import DumpType
            if dt_str == 'all':
                return DumpType.ALL
            else:
                DumpType.CUSTOMIZED.TYPE = dt_str
                return DumpType.CUSTOMIZED

    def SetSite(this, a_site, a_force=False):
        if not a_site:
            return

        this._fetch_metadata()
        if this.db_metadata:
            if this.db_metadata.site is None:
                this.db_metadata.site = a_site
                this.session.commit()

            if a_force is True:
                this.db_metadata.site = a_site
                this.session.commit()

    def GetSite(this):
        this._fetch_metadata()
        return this.db_metadata.site if this.db_metadata else None

    def SetPairDBFile(this, a_dbfile, a_force=False):
        if not a_dbfile:
            return

        this._fetch_metadata()
        if this.db_metadata:
            if this.db_metadata.pairDbFile is None:
                this.db_metadata.pairDbFile = a_dbfile
                this.session.commit()

            if a_force is True:
                this.db_metadata.pairDbFile = a_dbfile
                this.session.commit()

    def GetPairDBFile(this):
        this._fetch_metadata()
        return this.db_metadata.pairDbFile if this.db_metadata else None

    def SetLock(this, a_lock=1):
        if a_lock is None:
            return

        this._fetch_metadata()
        if this.db_metadata:
            this.db_metadata.lock = a_lock
            this.session.commit()

    def GetLock(this):
        this._fetch_metadata()
        return this.db_metadata.lock if this.db_metadata else None

    def SetPRNum(this, a_pr, a_force=False):
        if not a_pr:
            return

        this._fetch_metadata()
        if this.db_metadata:
            if this.db_metadata.prNumber is None:
                this.db_metadata.prNumber = a_pr
                this.session.commit()

            if a_force is True:
                this.db_metadata.prNumber = a_pr
                this.session.commit()

    def GetPRNum(this):
        this._fetch_metadata()
        return this.db_metadata.prNumber if this.db_metadata else None

    def SetKbUrl(this, a_kb, a_force=False):
        if not a_kb:
            return

        this._fetch_metadata()
        if this.db_metadata:
            if this.db_metadata.kbUrl is None:
                this.db_metadata.kbUrl = a_kb
                this.session.commit()

            if a_force is True:
                this.db_metadata.kbUrl = a_kb
                this.session.commit()

    def GetKbUrl(this):
        this._fetch_metadata()
        return this.db_metadata.kbUrl if this.db_metadata else None

    def SetDescript(this, a_desc, a_force=False):
        if not a_desc:
            return

        this._fetch_metadata()
        if this.db_metadata:
            if this.db_metadata.desc is None:
                this.db_metadata.desc = a_desc
                this.session.commit()

            if a_force is True:
                this.db_metadata.desc = a_desc
                this.session.commit()

    def GetDescript(this):
        this._fetch_metadata()
        return this.db_metadata.desc if this.db_metadata else None

    def SetFixByModule(this, a_module):
        """
        If db is in lock mode, this setting will throw exception:
        FixbyModuleException
        """
        if not a_module:
            return

        if this.db_metadata.lock != 0:
            raise FixbyModuleException(
                "DB",
                "this database is in lock mode",
                "base_dbop.py")

        if this.fixby_table_c is not None:
            fixbyObj = this.fixby_table_c()
            fixbyObj.module = a_module.NAME
            fixbyObj.desc = a_module.DESC
            this.session.add(fixbyObj)
            this.session.commit()

    def GetFixByModule(this):
        if this.fixby_table_c is None:
            return None

        result = this.session.query(this.fixby_table_c).\
            order_by(this.fixby_table_c.id)

        module_result = []

        for r in result:
            mo = Module()
            mo.NAME = r.module
            mo.DESC = r.desc
            module_result.append(mo)

        return module_result

    @abstractmethod
    def Dispose(this):
        pass

    VERSION = property(GetSrmVersion, SetSrmVersion)
    SITE = property(GetSite, SetSite)
    PAIRDB = property(GetPairDBFile, SetPairDBFile)
    LOCK = property(GetLock, SetLock)
    PRNUM = property(GetPRNum, SetPRNum)
    DUMPTYPE = property(GetDumpType, SetDumpType)
    KBURL = property(GetKbUrl, SetKbUrl)
    DESC = property(GetDescript, SetDescript)
    MODULE = property(GetFixByModule, SetFixByModule)
