from srm_db_tool.modules.tools.backup_restore_tb.ymlparsing \
    import SQLITE_DB_DIR, DB_CONN_PP, DB_CONN_SS
from srm_db_tool.modules.tools.backup_restore_tb.connection \
    import MakeConns, CheckConns

from srm_db_tool.modules.tools.check_create_table_cache import \
    CheckCreateCacheTable

import unicodedata

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

"""
Force refresh cache
"""
ft_args = {'action': 'store_true',
           'help': "Force recreate cache tables."}

parser.add_argument('--ft', **ft_args)

"""
Force backup into a locked dump.
"""
fb_args = {'action': 'store_true',
           'help': "Force backup into a locked database, might cause crash if"
           "primary key is violated."}

parser.add_argument('--fb', **fb_args)

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
        print(str(r) + " table is/are not in the cache table.")
        sys.exit()


# tableOp object init
from srm_db_tool.backup_tables_mgr.meta_table import \
    meta_table_name, fixby_table_name
from srm_db_tool.backup_tables_mgr.sqlitedbop import SqliteDbOp
from srm_db_tool.backup_tables_mgr.tableop import TableOp
from srm_db_tool.orm.gentable import GenTable

sqlop = None
tableOp = None

if arg_result.file == 'default':
    sqlop = SqliteDbOp(a_path=SQLITE_DB_DIR)
    tableOp = TableOp(sqlop)
else:
    sqlop = SqliteDbOp(arg_result.file, SQLITE_DB_DIR)
    tableOp = TableOp(sqlop)

if tableOp.GetMetaData()['lock']:
    if not arg_result.fb:
        print("database : {} is locked. If insist, use --fb to override.".
              format(arg_result.file))
        sys.exit()


def GetOrmClasses(a_site):
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()

    if a_site == 'pp':
        Base.metadata.bind = pp_conn.GetEngine()
    else:
        Base.metadata.bind = ss_conn.GetEngine()

    metadata = Base.metadata
    metadata.reflect()

    ormClasses =\
        [GenTable(unicodedata.normalize('NFKD', t).
         encode('ascii', 'ignore'),
         a_table=metadata.tables[t]) for t in metadata.tables
         if ms_pat_1.search(t) is None if ms_pat_2.match(t) is None
         if t != meta_table_name if t != fixby_table_name]
    return ormClasses

from srm_db_tool.modules.tools.version_check.version_check import GetSrmVersion
from srm_db_tool.backup_tables_mgr.dumptype import DumpType

pp_version = None
ss_version = None

if conn_flag & 1:
    pp_version = GetSrmVersion(pp_conn, 'pp')[1]  # version of primary site
if conn_flag & 2:
    ss_version = GetSrmVersion(ss_conn, 'ss')[1]  # version of secondary site


def Backup(a_site, a_type):
    session = None
    engine = None

    if a_site == 'pp':
        session = pp_conn.GetSession()
        engine = pp_conn.GetEngine()
    else:
        session = ss_conn.GetSession()
        engine = ss_conn.GetEngine()

    if a_type == 'all':
        for orm_c in GetOrmClasses(a_site):
            qresult = session.query(orm_c).all()
            if qresult is not None:
                tableOp.Backup(
                    qresult,
                    pp_version if a_site == 'pp' else ss_version,
                    "primary" if a_site == 'pp' else "secondary",
                    DumpType.ALL,
                    a_prNum=arg_result.pr,
                    a_kburl=arg_result.kb,
                    a_desc=arg_result.desc,
                    a_force=True)

    else:
        for tn in input_tables:
            table_c = GenTable(tn, engine)
            qresult = session.query(table_c).all()

            if qresult.__len__() == 0:
                if a_site == 'pp':
                    print("Protected Site Table : "
                          + tn + " has no data.")
                else:
                    print("Secondary Site Table : "
                          + tn + " has no data.")
            else:
                tableOp.Backup(
                    qresult,
                    pp_version if a_site == 'pp' else ss_version,
                    "primary" if a_site == 'pp' else "secondary",
                    DumpType.CUSTOMIZED,
                    a_prNum=arg_result.pr,
                    a_kburl=arg_result.kb,
                    a_desc=arg_result.desc,
                    a_force=True)


"""
Check sites
"""
if arg_result.site == 'pp':
    if 'all' in input_tables:
        Backup('pp', 'all')

    else:
        Backup('pp', 'tables')

elif arg_result.site == 'ss':
    if 'all' in input_tables:
        Backup('ss', 'all')

    else:
        Backup('ss', 'tables')
