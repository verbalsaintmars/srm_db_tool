from srm_db_tool.sqlalchemy.make_conn import MakeConn
from srm_db_tool.backup_tables_mgr.base_dbop import \
    BaseDbOp


class MssqlDbOp(BaseDbOp):
    """
    Manipulate sqlite database file
    """
    def __init__(this, a_param):
        """
        a_path : sqlite db file path
        """
        super(MssqlDbOp, this).__init__()

        this.params = a_param

        this.conn = MakeConn(this.params)

        this.metadata.bind = this.conn.GetEngine()
        this.session = this.conn.GetSession()

        this.CheckAndCreateTable()

    def _convertType(this, a_type):
        """
        Convert from different Database's
            column type to compatible sqlite column type
        """
        return a_type

    def Dispose(this):
        this.conn.Dispose()
