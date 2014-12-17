from srm_db_tool.sqlalchemy.db_support.init_params import Init_Params
from srm_db_tool.sqlalchemy.make_conn import MakeConn

from srm_db_tool.modules.tools.version_check.version_check \
    import GetSrmVersion


def main():
    input_params = Init_Params()
    input_params.DBTYPE = 'mssql'
    input_params.DSN = "fun_db"
    input_params.UID = "ad"
    input_params.PWD = "ca$hc0w"

    conn = MakeConn(input_params)

    result = GetSrmVersion(conn)
    print(result[0])
    print(result[1])
