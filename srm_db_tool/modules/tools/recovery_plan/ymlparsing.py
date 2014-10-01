"""
backuptb table_name {db file name} {pp,ss}
backuptb all {db file name} {pp,ss}
"""
from srm_db_tool.config_mgr.parseyml import ParseYml

ymlParser = ParseYml()
p_result = ymlParser.LoadYml()

SQLITE_DB_DIR = p_result[0]

"""
Already a Init_Param object
"""
DB_CONN_PP = p_result[1][0]
DB_CONN_SS = p_result[1][1]
