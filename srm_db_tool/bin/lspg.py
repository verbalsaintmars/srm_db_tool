import argparse
from srm_db_tool.modules.tools.protection_group.argparse_parent \
    import version_parser as parent_parser

ap_args = {'prog': 'lspg',
           'description': 'List SRM protection groups',
           'epilog': 'Contact shc for any help.',
           'fromfile_prefix_chars': '@',
           'add_help': True,
           'parents': [parent_parser]}

parser = argparse.ArgumentParser(**ap_args)


"""
Table name arguement
"""
rpname_args = {'type': str,
               'help': "type in recovery plan name to show details "
               "or 'all' to show all the recovery plans"}

parser.add_argument('pg_name', **rpname_args)


"""
which site to restore tables
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
result = parser.parse_args()

from srm_db_tool.modules.tools.protection_group.ymlparsing\
    import DB_CONN_PP, DB_CONN_SS


from srm_db_tool.modules.tools.protection_group.connection\
    import MakeConns, CheckConns

pp_conn, ss_conn = MakeConns(DB_CONN_PP, DB_CONN_SS)

if result.site == "both":
    pp_msg = "Choose to show protection group info on both site, " +\
             "but no complete Protected Site DB " +\
             "Connection information provided."
    ss_msg = "Choose to show protection group info on both site, " +\
             "but no complete Recovery Site DB " +\
             "Connection information provided."
    CheckConns(pp_conn, ss_conn, pp_msg, ss_msg)

# -----------------------------------------------------------------
from srm_db_tool.modules.tools.protection_group.list_protection_group\
    import ListProtectionGroup


lspg = ListProtectionGroup(pp_conn, ss_conn)

if result.site == 'both':
    if result.pg_name == 'all':
        lspg()
    else:
        lspg(result.pg_name)

if result.site == 'pp':
    if result.pg_name == 'all':
        lspg.site(a_site='pp')
    else:
        lspg.site(result.pg_name, a_site='pp')

if result.site == 'ss':
    if result.pg_name == 'all':
        lspg.site(a_site='ss')
    else:
        lspg.site(result.pg_name, a_site='ss')
