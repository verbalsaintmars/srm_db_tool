import argparse
from srm_db_tool.modules.tools.recovery_plan.argparse_parent \
    import version_parser as parent_parser

ap_args = {'prog': 'lsvm',
           'description': 'List SRM Protection Group\'s Protected VMs',
           'epilog': 'Contact VMWare/CPD/SRM team for help.',
           'fromfile_prefix_chars': '@',
           'add_help': True,
           'parents': [parent_parser]}

parser = argparse.ArgumentParser(**ap_args)


"""
Table name arguement
"""
pgname_args = {'type': str,
               'help': "type in recovery plan name to show details "
               "or 'all' to show all the recovery plans"}

parser.add_argument('pg_name', **pgname_args)


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

from srm_db_tool.modules.tools.recovery_plan.ymlparsing\
    import DB_CONN_PP, DB_CONN_SS


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

from srm_db_tool.modules.tools.protection_group.list_vm\
    import ListVm


lsvm = ListVm(the_conn)

vm_result = lsvm.GetProtectedVms(arg_result.pg_name)

if vm_result is not None:
    lsvm.PrintResult(vm_result)
