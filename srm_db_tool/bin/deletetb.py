import argparse
from srm_db_tool.modules.tools.backup_restore_tb.argparse_parent \
    import version_parser as parent_parser

ap_args = {'prog': 'deletetb',
           'description': 'delete SRM database tables',
           'epilog': 'Contact shc for any help.',
           'fromfile_prefix_chars': '@',
           'add_help': True,
           'parents': [parent_parser]}

parser = argparse.ArgumentParser(**ap_args)


"""
Table name arguement
"""
table_name_args = {'type': str,
                   'help': "type in table name to delete "
                   "or 'all' to delete the whole database"}

parser.add_argument('table_name', **table_name_args)



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


# ----------------------------------------------------------
"""
backuptb table_name {db file name} {pp,ss}
backuptb all {db file name} {pp,ss}
"""
from srm_db_tool.config_mgr.parseyml import ParseYml

ymlParser = ParseYml()
p_result = ymlParser.LoadYml()

SQLITE_DB_DIR = p_result[0]

"""
Already a Init_Param object
"""
DB_CONN_PP = p_result[1][0]
DB_CONN_SS = p_result[1][1]


# ----------------------------------------------------------
from srm_db_tool.sqlalchemy.make_conn import MakeConn

pp_conn = None
ss_conn = None

if DB_CONN_PP is not None:
    pp_conn = MakeConn(DB_CONN_PP)

if DB_CONN_SS is not None:
    ss_conn = MakeConn(DB_CONN_SS)


from srm_db_tool.orm.gentable import GenTable
import sys

if result.site == "both":
    if pp_conn is None:
        print("Choose to restore up both site, "
              "but no complete protected Site DB "
              "Connection information provided.")
        sys.exit()
    if ss_conn is None:
        print("Choose to restore up both site, "
              "but no complete recovery Site DB "
              "Connection information provided.")
        sys.exit()


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

# debug = ReflectDb('pp')


def Delete(a_table_name, a_site, a_force=False):
    engine = pp_conn.GetEngine() if a_site == 'pp' else ss_conn.GetEngine()

    table_c = GenTable(a_table_name, engine)

    engine.execute(table_c.__table__.delete())


"""
Check sites
"""
import unicodedata

if result.site == 'both':
    if result.table_name == 'all':

        session_pp = pp_conn.GetSession()

        l_tables = ReflectDb('pp').tables
        for tname in l_tables:
            str_tname = unicodedata.normalize('NFKD', tname).\
                encode('ascii', 'ignore')
            Delete(str_tname, 'pp', True)

        l_tables = ReflectDb('ss').tables
        for tname in l_tables:
            str_tname = unicodedata.normalize('NFKD', tname).\
                encode('ascii', 'ignore')
            Delete(str_tname, 'ss', True)

    else:
        Delete(result.table_name, 'pp')
        Delete(result.table_name, 'ss')

elif result.site == 'pp':
    if result.table_name == 'all':
        l_tables = ReflectDb('pp').tables
        for tname in l_tables:
            str_tname = unicodedata.normalize('NFKD', tname).\
                encode('ascii', 'ignore')
            Delete(str_tname, 'pp', True)
    else:
        Delete(result.table_name, 'pp')


elif result.site == 'ss':
    if result.table_name == 'all':
        l_tables = ReflectDb('ss').tables
        for tname in l_tables:
            str_tname = unicodedata.normalize('NFKD', tname).\
                encode('ascii', 'ignore')
            Delete(str_tname, 'ss', True)
    else:
        Delete(result.table_name, 'ss')
