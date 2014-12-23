"""
lstp
Display dumped database's table info and metadata info
"""
from srm_db_tool.modules.tools.backup_restore_tb.ymlparsing \
    import SQLITE_DB_DIR, DB_CONN_PP, DB_CONN_SS
from srm_db_tool.modules.tools.backup_restore_tb.connection \
    import MakeConns, CheckConns

import argparse
from srm_db_tool.modules.tools.backup_restore_tb.argparse_parent \
    import version_parser as parent_parser

ap_args = {'prog': 'lstb',
           'description': 'List database table info',
           'epilog': 'Contact VMWare/CPD/SRM team for help.',
           'fromfile_prefix_chars': '@',
           'add_help': True,
           'parents': [parent_parser]}

parser = argparse.ArgumentParser(**ap_args)


"""
Table name arguement
"""
table_name_args = {'type': str,
                   'nargs': '*',
                   'help': "type in table name to list info"}

parser.add_argument('table_name', **table_name_args)

"""
sqlite db file name
"""
dbfilename_args = {'type': str,
                   'nargs': '?',
                   'help': "sqlite db file for inspecting."}

parser.add_argument('-f', '--file', **dbfilename_args)


"""
which site to dump tables
"""
site_args = {'type': str,
             'nargs': '?',
             'default': 'pp',
             'choices': ['pp', 'ss'],
             'help': "pp or ss for protected site or recovery site.\n"
             "Default: %(default)s"}

parser.add_argument('-s', '--site', **site_args)

"""
Show metadata table information
"""
meta_args = {'action': 'store_true',
             'help': "show only the metadata info of the database"}

parser.add_argument('-m', '--meta', **meta_args)


"""
Show fixby table information
"""
fixby_args = {'action': 'store_true',
              'help': "list fixby metadata info"}

parser.add_argument('-x', '--fixby', **fixby_args)

arg_result = parser.parse_args()

"""
Extract table name into set
"""
input_tables = \
    set(arg_result.table_name) if arg_result.table_name is not None else None

"""
Check inspecting local sqlite db or remote connection from dbprobe.xml
"""
from srm_db_tool.backup_tables_mgr.tableop import TableOp
import sys

conn_flag = 0
pp_conn = None
ss_conn = None
tableOp = None


def ChkConn():
    global conn_flag
    if CheckConns(pp_conn):
        conn_flag |= 1

    if CheckConns(ss_conn):
        conn_flag |= 2


metastr_template = "{:15} {}"
fixby_template = "{:9} {:>10}"
table_template = "{:9}"


def ChkMetaFlag(a_tableOp):
    if arg_result.meta:
        meta_result = a_tableOp.GetMetaData()

        print(metastr_template.format("Key", "Value"))
        print("-" * 25)
        for key, val in meta_result.iteritems():
            print(metastr_template.format(key, val))

        print("\n")

    if arg_result.fixby:
        fixby_result = a_tableOp.GetFixByModule()

        print(fixby_template.format("Module", "Description"))
        print("-" * 25)

        if fixby_result is not None:
            for mo_val in fixby_result:
                print(fixby_template.format(mo_val.NAME, mo_val.DESC))

        print("\n")

    if input_tables:
        if 'all' in input_tables:
            print(table_template.format("Table name"))
            print("-" * 25)

            for tn in sorted(a_tableOp.ListTables()):
                print(table_template.format(tn))
        else:
            list_table_set = set(a_tableOp.ListTables())
            r_set = input_tables - list_table_set
            if r_set.__len__() != 0:
                print(str(r_set) + " table(s) is/are not in the database.")
            else:
                print(str(input_tables) + " table(s) is/are in the database.")


if arg_result.file is None:
    from srm_db_tool.backup_tables_mgr.generaldbop import GeneralDbOp
    """
    Inspect remote db
    """
    pp_conn, ss_conn = MakeConns(DB_CONN_PP, DB_CONN_SS)

    ChkConn()

    the_conn = None

    pp_msg = "No complete Protected Site DB " +\
             "Connection information provided."
    ss_msg = "No complete Secondary Site DB " +\
             "Connection information provided."

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

    sqlop = GeneralDbOp(a_conn=the_conn, a_create_meta_table=False)
    tableOp = TableOp(sqlop)
else:
    from srm_db_tool.backup_tables_mgr.sqlitedbop import SqliteDbOp
    sqlop = SqliteDbOp(arg_result.file, SQLITE_DB_DIR, False)
    tableOp = TableOp(sqlop)

ChkMetaFlag(tableOp)
