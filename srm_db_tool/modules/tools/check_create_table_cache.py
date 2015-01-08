from os import path

table_cache_file_name = 'table_cache'


def CheckCreateCacheTable(a_conn, a_force=False):
    if a_force:
        from srm_db_tool.modules.tools.build_cache_table import BuildCache
        return BuildCache(a_conn, table_cache_file_name)

    if path.isfile(table_cache_file_name+".py"):
        return __import__(table_cache_file_name).tables

    else:
        from srm_db_tool.modules.tools.build_cache_table import BuildCache
        return BuildCache(a_conn, table_cache_file_name)
