import argparse
from srm_db_tool.modules.tools.protection_group.argparse_parent \
    import version_parser as parent_parser

ap_args = {'prog': 'lspg',
           'description': 'List SRM protection groups',
           'epilog': 'Contact VMWare/CPD/SRM team for help.',
           'fromfile_prefix_chars': '@',
           'add_help': True,
           'parents': [parent_parser]}

parser = argparse.ArgumentParser(**ap_args)


"""
Table name arguement
"""
pgname_args = {'type': str,
               'help': "type in Protection Group name to show details "
               "or 'all' to show all the recovery plans"}

parser.add_argument('pg_name', **pgname_args)


"""
which site to list pg
"""
site_args = {'type': str,
             'nargs': '?',
             'default': 'both',
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

if arg_result.site == "both":
    if not (conn_flag & 1):
        print(pp_msg)
        sys.exit()

    if not (conn_flag & 2):
        print(ss_msg)
        sys.exit()
elif arg_result.site == "pp":
    if not (conn_flag & 1):
        print(pp_msg)
        sys.exit()
elif arg_result.site == "ss":
    if not (conn_flag & 2):
        print(pp_msg)
        sys.exit()

# -----------------------------------------------------------------
from srm_db_tool.modules.tools.protection_group.list_protection_group\
    import ListProtectionGroup


lspg = ListProtectionGroup(pp_conn, ss_conn)

if arg_result.site == 'both':
    if arg_result.pg_name == 'all':
        lspg()
    else:
        lspg(arg_result.pg_name)

if arg_result.site == 'pp':
    if arg_result.pg_name == 'all':
        lspg.site(a_site='pp')
    else:
        lspg.site(arg_result.pg_name, a_site='pp')

if arg_result.site == 'ss':
    if arg_result.pg_name == 'all':
        lspg.site(a_site='ss')
    else:
        lspg.site(arg_result.pg_name, a_site='ss')
