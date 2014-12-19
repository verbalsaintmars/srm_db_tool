from srm_db_tool.sqlalchemy.make_conn import MakeConn
from srm_db_tool.backup_tables_mgr.fm import DbFileOp

from srm_db_tool.backup_tables_mgr.base_dbop import \
    BaseDbOp

# General Types
# Latin1_General_CI_AS issue
from sqlalchemy import VARCHAR as General_VARCHAR
from sqlalchemy import UnicodeText
# DB Specific types
# MS SQL
from sqlalchemy.dialects.mssql import VARCHAR as MSSQL_VARCHAR
from sqlalchemy.dialects.mssql import NTEXT as MSSQL_NTEXT


class SqliteDbOp(BaseDbOp):
    """
    Manipulate sqlite database file
    """
    def __init__(this, a_dbfile=None, a_path=None):
        """
        a_path : sqlite db file path
        """
        super(SqliteDbOp, this).__init__()

        sqlite_db_path = None

        if a_dbfile is None:
            sqlite_db_path =\
                DbFileOp(a_default_path=a_path).NextFileName()
        else:
            from os.path import join
            sqlite_db_path = \
                join(a_path if a_path is not None else "",
                     a_dbfile)

        this.params.DBTYPE = 'sqlite'
        this.params.PATH = sqlite_db_path

        this.conn = MakeConn(this.params)

        this.metadata.bind = this.conn.GetEngine()
        this.session = this.conn.GetSession()

        this.CheckAndCreateTable()

    def _convertType(this, a_type):
        """
        Convert from different Database's
            column type to compatible sqlite column type
        """
        try:
            result = {
                MSSQL_NTEXT: UnicodeText(),
                MSSQL_VARCHAR: General_VARCHAR(255)
            }[type(a_type)]
            return result
        except KeyError:
            return a_type

    def GetDBFilePath(this):
        return this.params.PATH

    def Dispose(this):
        this.conn.Dispose()

    DBFILEPATH = property(GetDBFilePath)
