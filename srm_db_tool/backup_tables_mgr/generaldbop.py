from srm_db_tool.backup_tables_mgr.base_dbop import \
    BaseDbOp


class GeneralDbOp(BaseDbOp):
    """
    General DbOp class:
        for read data only.
    """
    def __init__(this, a_conn, a_create_meta_table=False):
        super(GeneralDbOp, this).__init__()

        this.conn = a_conn

        this.metadata.bind = this.conn.GetEngine()
        this.session = this.conn.GetSession()

        this.CheckAndCreateTable(a_create_meta_table)

    def _convertType(this, a_type):
        return a_type

    def Dispose(this):
        this.conn.Dispose()
