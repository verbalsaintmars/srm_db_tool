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
                   'nargs': '*',
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
which workflow tables to dump.
"""
wf_args = {'type': str,
           'nargs': '?',
           'help': "Talbes of workflow to backup.\n"}

parser.add_argument('-wf', '--wf', **wf_args)


"""
list workflow provided.
"""
list_wf_args = {'action': 'store_true',
                'help': "List workflows supported.\n"}
parser.add_argument('-l', '--listwf', **list_wf_args)


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

parser.add_argument('-ft', '--ft', **ft_args)

"""
Force backup into a locked dump.
"""
fb_args = {'action': 'store_true',
           'help': "Force backup into a locked database, might cause crash if"
           "primary key is violated."}

parser.add_argument('-fb', '--fb', **fb_args)

arg_result = parser.parse_args()
if arg_result.table_name.__len__() == 0 and \
    arg_result.listwf is False and \
    arg_result.ft is False and \
        arg_result.wf is None:
    print("Please use -h for help.")
    import sys
    sys.exit()

"""
Workflow logic
"""
input_tables = None
dtype = None


def CheckCacheTable():
    global input_tables
    if 'all' not in input_tables:
        table_in_cache_set = input_tables & table_cache

        if len(table_in_cache_set) != len(input_tables):
            import sys
            r = input_tables - table_in_cache_set
            print(str(r) + " table is/are not in the cache table.")
            sys.exit()


def ListSupportWorkFlow():
    if arg_result.listwf is not False:
        from srm_db_tool.backup_tables_mgr.tables.workflow import WorkFlow
        wf_obj = WorkFlow()
        wf_list = wf_obj.GetWfList()

        wf_str_tmp = "{:^20} {:^10}"
        import sys
        print(wf_str_tmp.format("Workflow modules", "Description"))
        for wf in wf_list:
            print(wf_str_tmp.format(wf[0], wf[1]))
        sys.exit()

ListSupportWorkFlow()


def GetWfTables():
    global input_tables
    global dtype

    if arg_result.wf is not None:
        from srm_db_tool.backup_tables_mgr.tables.workflow import WorkFlow
        wf_obj = WorkFlow()
        wf_list = wf_obj.GetWfList()
        table_list = None

        for wf in wf_list:
            if arg_result.wf == wf[0]:
                table_list = wf[2]
                dtype = wf[0]

        if table_list is None:
            print("Please specify the proper workflow module."
                  "Use -l to list supported modules.")
            import sys
            sys.exit()

        input_tables = set(table_list)
        CheckCacheTable()

GetWfTables()


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
        import sys
        print(pp_msg)
        sys.exit()

if arg_result.site == 'ss':
    if not (conn_flag & 2):
        import sys
        print(ss_msg)
        sys.exit()

if arg_result.ft:
    table_cache = CheckCreateCacheTable(the_conn, True)

if input_tables is None:
    if arg_result.table_name is None:
        import sys
        print("Please either type in -wf or tables you want to backup from.")
        sys.exit()

    input_tables = set(arg_result.table_name)
    CheckCacheTable()


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

if tableOp.GetMetaData()['Lock state']:
    if not arg_result.fb:
        import sys
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
                dumptype = DumpType.CUSTOMIZED
                if a_type is not None:
                    dumptype.TYPE = a_type

                tableOp.Backup(
                    qresult,
                    pp_version if a_site == 'pp' else ss_version,
                    "primary" if a_site == 'pp' else "secondary",
                    dumptype,
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
        Backup('pp', dtype)

elif arg_result.site == 'ss':
    if 'all' in input_tables:
        Backup('ss', 'all')

    else:
        Backup('ss', dtype)
