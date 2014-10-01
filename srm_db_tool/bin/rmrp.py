import argparse
from srm_db_tool.modules.tools.recovery_plan.argparse_parent \
    import version_parser as parent_parser

ap_args = {'prog': 'rmrp',
           'description': 'Remove SRM recovery plans',
           'epilog': 'Contact shc for any help.',
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
             'default': 'both',
             'choices': ['pp', 'ss'],
             'help': "pp or ss for protected site or recovery site.\n"
             "Default: %(default)s"}

parser.add_argument('-s', '--site', **site_args)


# result = parser.parse_args(["pds_table_name"])
# result = parser.parse_args(['pdr_vminfo', '-f', 'testME.db'])
# result = parser.parse_args(['all', '-f', 'all_pp.db', '-s', 'pp'])
result = parser.parse_args()

from srm_db_tool.modules.tools.recovery_plan.ymlparsing\
    import SQLITE_DB_DIR, DB_CONN_PP, DB_CONN_SS


from srm_db_tool.modules.tools.recovery_plan.connection\
    import MakeConns, CheckConns

pp_conn, ss_conn = MakeConns(DB_CONN_PP, DB_CONN_SS)

if result.site == "both":
    pp_msg = "Choose to remove recovery plan on both site, " +\
             "but no complete Protected Site DB " +\
             "Connection information provided."
    ss_msg = "Choose to remove recovery plan on both site, " +\
             "but no complete Recovery Site DB " +\
             "Connection information provided."
    CheckConns(pp_conn, ss_conn, pp_msg, ss_msg)

# -----------------------------------------------------------------
from srm_db_tool.backup_tables_mgr.dbop import TableOp

tableOp = None

if result.file == 'default':
    tableOp = TableOp(a_default_path=SQLITE_DB_DIR)
else:
    tableOp = TableOp(a_dbfile=result.file, a_default_path=SQLITE_DB_DIR)


# -----------------------------------------------------------------
from srm_db_tool.modules.tools.recovery_plan.remove_recovery_plan\
    import RemoveRecoveryPlan


rmrp = RemoveRecoveryPlan(pp_conn, ss_conn, tableOp)


if result.site == 'both':
    rmrp(result.rp_name, a_site='pp')
    rmrp(result.rp_name, a_site='ss')

if result.site == 'pp':
    rmrp(result.rp_name, a_site='pp')

if result.site == 'ss':
    rmrp(result.rp_name, a_site='ss')
