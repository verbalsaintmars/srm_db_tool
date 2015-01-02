"""
backuptb table_name {db file name} {pp,ss}
backuptb all {db file name} {pp,ss}
"""
from srm_db_tool.config_mgr.parseyml import ParseYml

ymlParser = ParseYml()

"""
p_result:
    (sqlite_db_dir, (protection site Init_Params, recovery site Init_Params))
"""
p_result = ymlParser.LoadYml()

if p_result is None:
    import sys
    sys.exit()

SQLITE_DB_DIR = p_result[0]

"""
Already a Init_Param object
"""
DB_CONN_PP = None
DB_CONN_SS = None
try:
    DB_CONN_PP = p_result[1][0]
except Exception as e:
    print(e)

try:
    DB_CONN_SS = p_result[1][1]
except Exception as e:
    print(e)
