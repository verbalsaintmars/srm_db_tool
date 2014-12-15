from srm_db_tool.backup_tables_mgr.tableop import TableOp
from srm_db_tool.backup_tables_mgr.sqlitedbop import SqliteDbOp
from srm_db_tool.backup_tables_mgr.dumptype import DumpType
from srm_db_tool.sqlalchemy.db_support.init_params import Init_Params
from srm_db_tool.sqlalchemy.make_conn import MakeConn
from sqlalchemy.ext.declarative import declarative_base
from srm_db_tool.orm.gentable import GenTable


def main():
    sqlop = SqliteDbOp(r"/tmp/backup_fun.db")
    tbop = TableOp(sqlop)

    params = Init_Params()
    params.DBTYPE = 'sqlite'
    params.PATH = r"/tmp/sqlite_db.db"

    base = declarative_base()

    conn = MakeConn(params)

    base.metadata.bind = conn.GetEngine()
    session = conn.GetSession()

    table_1_c = GenTable("table_1", a_engine=conn.GetEngine())

    fetched_data = session.query(table_1_c).all()

    tbop.Backup(
        fetched_data,
        "5.8.0.1-ep1",
        "primary",
        DumpType.RecoveryPlan,
        a_desc="Hahaha")

    # ---------------
    # demo restore and insert into another backup db
    print("1")
    sqlop2 = SqliteDbOp(r"/tmp/backup_another_fun.db")
    print("1.2")
    tbop2 = TableOp(sqlop2)
    print("2")

    restored_data = tbop.Restore("table_1")
    print("3")

    if restored_data:
        tbop2.Backup(
            restored_data,
            "backup_verstion",
            "primary",
            DumpType.ProtectionGrp,
            a_desc="restored data")

    tbop.Dispose()
    tbop2.Dispose()
