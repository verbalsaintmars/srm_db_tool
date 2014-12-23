from srm_db_tool.sqlalchemy.make_conn import MakeConn
from srm_db_tool.backup_tables_mgr.base_dbop import \
    BaseDbOp

# General Types
# Latin1_General_CI_AS issue
from sqlalchemy import VARCHAR as General_VARCHAR
# DB Specific types
# MS SQL
from sqlalchemy.dialects.mssql import VARCHAR as MSSQL_VARCHAR
from sqlalchemy.dialects.mssql import NTEXT as MSSQL_NTEXT


class MssqlDbOp(BaseDbOp):
    """
    Manipulate sqlite database file
    """
    def __init__(this, a_param=None, a_conn=None, a_create_meta_table=True):
        super(MssqlDbOp, this).__init__()

        if a_conn is not None:
            this.conn = a_conn
        else:
            this.params = a_param

            this.conn = MakeConn(this.params)

        this.metadata.bind = this.conn.GetEngine()
        this.session = this.conn.GetSession()

        this.CheckAndCreateTable(a_create_meta_table)

    def _convertType(this, a_type):
        """
        Even in mssql , column type should be altered~
        """
        try:
            result = {
                MSSQL_NTEXT: General_VARCHAR(255),
                MSSQL_VARCHAR: General_VARCHAR(255)
            }[type(a_type)]
            return result
        except KeyError:
            return a_type

    def Dispose(this):
        this.conn.Dispose()
