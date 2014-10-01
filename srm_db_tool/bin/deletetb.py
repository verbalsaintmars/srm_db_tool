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

from srm_db_tool.modules.tools.backup_restore_tb.ymlparsing\
    import DB_CONN_PP, DB_CONN_SS


from srm_db_tool.modules.tools.backup_restore_tb.connection\
    import MakeConns, CheckConns

pp_conn, ss_conn = MakeConns(DB_CONN_PP, DB_CONN_SS)

if result.site == "both":
    pp_msg = "Choose to delete both site, " +\
             "but no complete Protected Site DB " +\
             "Connection information provided."
    ss_msg = "Choose to delete both site, " +\
             "but no complete Recovery Site DB " +\
             "Connection information provided."
    CheckConns(pp_conn, ss_conn, pp_msg, ss_msg)

from srm_db_tool.modules.tools.backup_restore_tb.regex import *

from srm_db_tool.orm.gentable import GenTable


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
            if ms_pat_1.search(tname) is not None:
                continue
            if ms_pat_2.match(tname) is not None:
                continue
            str_tname = unicodedata.normalize('NFKD', tname).\
                encode('ascii', 'ignore')
            Delete(str_tname, 'pp', True)

        l_tables = ReflectDb('ss').tables
        for tname in l_tables:
            if ms_pat_1.search(tname) is not None:
                continue
            if ms_pat_2.match(tname) is not None:
                continue
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
            if ms_pat_1.search(tname) is not None:
                continue
            if ms_pat_2.match(tname) is not None:
                continue
            str_tname = unicodedata.normalize('NFKD', tname).\
                encode('ascii', 'ignore')
            Delete(str_tname, 'pp', True)
    else:
        Delete(result.table_name, 'pp')


elif result.site == 'ss':
    if result.table_name == 'all':
        l_tables = ReflectDb('ss').tables
        for tname in l_tables:
            if ms_pat_1.search(tname) is not None:
                continue
            if ms_pat_2.match(tname) is not None:
                continue
            str_tname = unicodedata.normalize('NFKD', tname).\
                encode('ascii', 'ignore')
            Delete(str_tname, 'ss', True)
    else:
        Delete(result.table_name, 'ss')
