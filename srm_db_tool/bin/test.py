from srm_db_tool.modules.tools.backup_restore_tb.ymlparsing \
    import SQLITE_DB_DIR, DB_CONN_PP, DB_CONN_SS
from srm_db_tool.modules.tools.backup_restore_tb.connection \
    import MakeConns, CheckConns

from srm_db_tool.modules.tools.check_create_table_cache import \
    CheckCreateCacheTable

"""
import ms_pat_1 and ms_pat_2
"""
from srm_db_tool.modules.tools.backup_restore_tb.regex import \
    ms_pat_1, ms_pat_2


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

ap_args = {'prog': 'backuptb',
           'description': 'Backup SRM database tables',
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
                   'help': "type in table name to backup "
                   "or 'all' to back the whole database"}

parser.add_argument('table_name', **table_name_args)

"""
sqlite db file name
"""
dbfilename_args = {'type': str,
                   'nargs': '?',
                   'default': 'default',
                   'help': "sqlite db file name or use default generated name"}

parser.add_argument('-f', '--file', **dbfilename_args)


"""
which site to dump tables
"""
site_args = {'type': str,
             'nargs': '?',
             'default': 'both',
             'choices': ['both', 'pp', 'ss'],
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

"""
Force refresh cache
"""
ft_args = {'action': 'store_true',
           'help': "Force recreate cache tables."}

parser.add_argument('--ft', **ft_args)

result = parser.parse_args()

print(result.pr)
print(result.kb)
