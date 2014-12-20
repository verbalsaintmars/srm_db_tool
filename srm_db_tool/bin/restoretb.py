from srm_db_tool.modules.tools.backup_restore_tb.ymlparsing \
    import SQLITE_DB_DIR, DB_CONN_PP, DB_CONN_SS
from srm_db_tool.modules.tools.backup_restore_tb.connection \
    import MakeConns, CheckConns

import unicodedata

"""
import ms_pat_1 and ms_pat_2
"""
from srm_db_tool.modules.tools.backup_restore_tb.regex import \
    ms_pat_1, ms_pat_2
from srm_db_tool.backup_tables_mgr.meta_table import \
    meta_table_name, fixby_table_name


pp_conn, ss_conn = MakeConns(DB_CONN_PP, DB_CONN_SS)


import argparse
from srm_db_tool.modules.tools.backup_restore_tb.argparse_parent \
    import version_parser as parent_parser

ap_args = {'prog': 'restoretb',
           'description': 'Restore SRM database tables',
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
                   'help': "type in table name to restore"
                   "or 'all' to back the whole database"}

parser.add_argument('table_name', **table_name_args)


"""
sqlite db file name
"""
dbfilename_args = {'type': str,
                   'nargs': '?',
                   'default': 'default',
                   'help': "sqlite db file or use the latest generated file"
                   "to restore from."}

parser.add_argument('-f', '--file', **dbfilename_args)


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

the_conn = None

if arg_result.site == 'pp':
    if not (conn_flag & 1):
        print(pp_msg)
        sys.exit()
    the_conn = pp_conn

if arg_result.site == 'ss':
    if not (conn_flag & 2):
        print(ss_msg)
        sys.exit()
    the_conn = ss_conn


from srm_db_tool.backup_tables_mgr.tableop import TableOp
from srm_db_tool.backup_tables_mgr.sqlitedbop import SqliteDbOp
from srm_db_tool.backup_tables_mgr.fm import DbFileOp
from srm_db_tool.orm.gentable import GenTable

tableOp = None
sqlOp = None

if arg_result.file == 'default':
    filename = DbFileOp(SQLITE_DB_DIR).LatestFileName(False)
    sqlOp = SqliteDbOp(filename, SQLITE_DB_DIR)
    tableOp = TableOp(sqlOp)
    arg_result.file = filename
else:
    sqlOp = SqliteDbOp(arg_result.file, SQLITE_DB_DIR)
    tableOp = TableOp(sqlOp)

input_tables = set(arg_result.table_name)


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

### TODO delete all data inside that table then restore!!!
def Restore(a_table_name):
    restore_result = tableOp.Restore(a_table_name)

    if restore_result is None:
        print("Recovery db file: "
              + arg_result.file + " has no backup table: "
              + a_table_name)

    elif restore_result.__len__() == 0:
        print("Recovery db file: "
              + arg_result.file + " has no data in table: "
              + a_table_name)

    session = the_conn.GetSession()

    if restore_result is not None:
        for orm_o in restore_result:
            local_orm_o = table_c()
            for c in table_c.__table__.c:
                setattr(local_orm_o, c.name, getattr(orm_o, c.name))
            session.add(local_orm_o)
            session.commit()


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

        Restore(str_tname)
else:
    DeleteAndRestore(result.table_name, 'pp')
