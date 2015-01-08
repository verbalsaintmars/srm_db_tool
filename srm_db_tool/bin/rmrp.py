import argparse
from srm_db_tool.modules.tools.recovery_plan.argparse_parent \
    import version_parser as parent_parser

from srm_db_tool.modules.tools.recovery_plan.verify \
    import GetVerify

ap_args = {'prog': 'rmrp',
           'description': 'Remove SRM recovery plans',
           'epilog': 'Contact VMWare/CPD/SRM team for help.',
           'fromfile_prefix_chars': '@',
           'add_help': True,
           'parents': [parent_parser]}

parser = argparse.ArgumentParser(**ap_args)


"""
Table name arguement
"""
rpname_args = {'type': str,
               'help': "type in the recovery plan name to be removed."}

parser.add_argument('rp_name', **rpname_args)


"""
sqlite db file name
"""
dbfilename_args = {'type': str,
                   'nargs': '?',
                   'default': 'default',
                   'help': "sqlite db file name or use default generated name"}

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


"""
Description of the database dump
"""
desc_args = {'type': str,
             'nargs': '?',
             'help': "Description of this database dump."}

parser.add_argument('-d', '--desc', **desc_args)


"""
PR Number
"""
pr_args = {'type': int,
           'nargs': '?',
           'help': "PR Number."}

parser.add_argument('-p', '--pr', **pr_args)


"""
KB URL
"""
kb_args = {'type': str,
           'nargs': '?',
           'help': "KB URL"}

parser.add_argument('-k', '--kb', **kb_args)

# result = parser.parse_args(["pds_table_name"])
# result = parser.parse_args(['pdr_vminfo', '-f', 'testME.db'])
# result = parser.parse_args(['all', '-f', 'all_pp.db', '-s', 'pp'])
arg_result = parser.parse_args()

from srm_db_tool.modules.tools.recovery_plan.ymlparsing\
    import SQLITE_DB_DIR, DB_CONN_PP, DB_CONN_SS


from srm_db_tool.modules.tools.recovery_plan.connection\
    import MakeConns, CheckConns

pp_conn, ss_conn = MakeConns(DB_CONN_PP, DB_CONN_SS)

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

import sys

the_conn = None

if arg_result.site == "pp":
    if not (conn_flag & 1):
        print(pp_msg)
        sys.exit()
    the_conn = pp_conn

elif arg_result.site == "ss":
    if not (conn_flag & 2):
        print(pp_msg)
        sys.exit()
    the_conn = ss_conn

# -----------------------------------------------------------------
from srm_db_tool.backup_tables_mgr.sqlitedbop import SqliteDbOp
from srm_db_tool.backup_tables_mgr.tableop import TableOp


sqlop = None
tableOp = None

if arg_result.file == 'default':
    sqlop = SqliteDbOp(a_path=SQLITE_DB_DIR)
    tableOp = TableOp(sqlop)
else:
    sqlop = SqliteDbOp(arg_result.file, SQLITE_DB_DIR)
    tableOp = TableOp(sqlop)


"""
Allow user to confirm the delete
"""
GetVerify()

# -----------------------------------------------------------------
from srm_db_tool.modules.tools.recovery_plan.remove_recovery_plan\
    import RemoveRecoveryPlan


rmrp = RemoveRecoveryPlan(
    the_conn,
    tableOp,
    arg_result.pr,
    arg_result.kb,
    arg_result.desc)


rmrp(arg_result.rp_name, a_site=arg_result.site)
