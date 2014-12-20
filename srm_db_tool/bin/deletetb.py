from srm_db_tool.modules.tools.backup_restore_tb.ymlparsing \
    import DB_CONN_PP, DB_CONN_SS
from srm_db_tool.modules.tools.backup_restore_tb.connection \
    import MakeConns, CheckConns

from srm_db_tool.modules.tools.check_create_table_cache import \
    CheckCreateCacheTable

import unicodedata


pp_conn, ss_conn = MakeConns(DB_CONN_PP, DB_CONN_SS)
the_conn = None

if CheckConns(pp_conn):
    the_conn = pp_conn
elif CheckConns(ss_conn):
    the_conn = ss_conn
else:
    print("No connection to database established."
          " Please check dbprobe.xml settings.")
    import sys
    sys.exit()

table_cache = CheckCreateCacheTable(the_conn)

import argparse
from srm_db_tool.modules.tools.backup_restore_tb.argparse_parent \
    import version_parser as parent_parser

ap_args = {'prog': 'deletetb',
           'description': 'delete SRM database tables',
           'epilog': 'Contact VMWare/CPD/SRM team for help.',
           'fromfile_prefix_chars': '@',
           'add_help': True,
           'parents': [parent_parser]}

parser = argparse.ArgumentParser(**ap_args)


"""
Table name arguement
"""
table_name_args = {'type': str,
                   'nargs': '+',
                   'help': "type in table name to delete "
                   "or 'all' to delete the whole database"}

parser.add_argument('table_name', **table_name_args)


"""
which site to restore tables
"""
site_args = {'type': str,
             'nargs': '?',
             'default': 'pp',
             'choices': ['pp', 'ss'],
             'help': "pp or ss for protected site or recovery site.\n"
             "Default: %(default)s"}

parser.add_argument('-s', '--site', **site_args)


"""
Force refresh cache
"""
ft_args = {'action': 'store_true',
           'help': "Force recreate cache tables."}

parser.add_argument('--ft', **ft_args)


# result = parser.parse_args(["pds_table_name"])
# result = parser.parse_args(['pdr_vminfo', '-f', 'testME.db'])
# result = parser.parse_args(['all', '-f', 'all_pp.db', '-s', 'pp'])
arg_result = parser.parse_args()


import sys
conn_flag = 0


def ChkConn():
    global conn_flag
    if CheckConns(pp_conn):
        conn_flag |= 1

    if CheckConns(ss_conn):
        conn_flag |= 2

ChkConn()

pp_msg = "No complete Protected Site DB " +\
         "Connection information provided."
ss_msg = "No complete Secondary Site DB " +\
         "Connection information provided."

if arg_result.site == 'pp':
    if not (conn_flag & 1):
        print(pp_msg)
        sys.exit()

if arg_result.site == 'ss':
    if not (conn_flag & 2):
        print(ss_msg)
        sys.exit()

if arg_result.ft:
    table_cache = CheckCreateCacheTable(the_conn, True)

input_tables = set(arg_result.table_name)

if 'all' not in input_tables:
    table_in_cache_set = input_tables & table_cache

    if len(table_in_cache_set) != len(input_tables):
        r = input_tables - table_in_cache_set
        print(str(r) + " table is/are not in the cache table."
              " Use --ft to force refresh cache table.")
        sys.exit()


from srm_db_tool.orm.gentable import GenTable


def ReflectDb(a_site):
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()

    if a_site == 'pp':
        Base.metadata.bind = pp_conn.GetEngine()
    else:
        Base.metadata.bind = ss_conn.GetEngine()

    metadata = Base.metadata
    metadata.reflect()
    return metadata

# debug = ReflectDb('pp')


def Delete(a_table_name, a_site):
    engine = pp_conn.GetEngine() if a_site == 'pp' else ss_conn.GetEngine()

    table_c = GenTable(a_table_name, engine)

    return engine.execute(table_c.__table__.delete()).rowcount


"""
import ms_pat_1, ms_pat_2, meta table names
"""
from srm_db_tool.modules.tools.backup_restore_tb.regex import \
    ms_pat_1, ms_pat_2
from srm_db_tool.backup_tables_mgr.meta_table import \
    meta_table_name, fixby_table_name

"""
Check sites
"""
if 'all' in input_tables:
    l_tables = ReflectDb(arg_result.site).tables

    for tname in l_tables:
        if ms_pat_1.search(tname) is not None:
            continue
        if ms_pat_2.match(tname) is not None:
            continue

        str_tname = unicodedata.normalize('NFKD', tname).\
            encode('ascii', 'ignore')

        if str_tname == meta_table_name or str_tname == fixby_table_name:
            continue

        affected_rows = Delete(
            str_tname,
            arg_result.site)

        print("Total affected rows for table {:>35}: {:<25}".
              format(str_tname, affected_rows))
else:
    for tn in input_tables:
        affected_rows = Delete(tn, arg_result.site)

        print("Total affected rows for table {:>35}: {:<25}"
              .format(tn, affected_rows))
