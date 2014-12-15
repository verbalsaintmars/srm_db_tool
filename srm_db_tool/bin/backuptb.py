import argparse
from srm_db_tool.modules.tools.backup_restore_tb.argparse_parent \
    import version_parser as parent_parser

ap_args = {'prog': 'backuptb',
           'description': 'Backup SRM database tables',
           'epilog': 'Contact shc for any help.',
           'fromfile_prefix_chars': '@',
           'add_help': True,
           'parents': [parent_parser]}

parser = argparse.ArgumentParser(**ap_args)


"""
Table name arguement
"""
table_name_args = {'type': str,
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
             'choices': ['pp', 'ss'],
             'help': "pp or ss for protected site or recovery site.\n"
             "Default: %(default)s"}

parser.add_argument('-s', '--site', **site_args)

# result = parser.parse_args(["pds_table_name"])
# result = parser.parse_args(['pdr_vminfo', '-f', 'testME.db'])
# result = parser.parse_args(['pd_moref', '-f', 'testME2.db'])
result = parser.parse_args()

from srm_db_tool.modules.tools.backup_restore_tb.ymlparsing\
    import SQLITE_DB_DIR, DB_CONN_PP, DB_CONN_SS


from srm_db_tool.modules.tools.backup_restore_tb.connection\
    import MakeConns, CheckConns

pp_conn, ss_conn = MakeConns(DB_CONN_PP, DB_CONN_SS)

if result.site == "both":
    pp_msg = "Choose to back up both site, " +\
             "but no complete Protected Site DB " +\
             "Connection information provided."
    ss_msg = "Choose to back up both site, " +\
             "but no complete Recovery Site DB " +\
             "Connection information provided."
    CheckConns(pp_conn, ss_conn, pp_msg, ss_msg)

"""
import ms_pat_1 and ms_pat_2
"""
from srm_db_tool.modules.tools.backup_restore_tb.regex import *

# tableOp object init
from srm_db_tool.backup_tables_mgr.dbop import TableOp
from srm_db_tool.orm.gentable import GenTable

tableOp = None

if result.file == 'default':
    tableOp = TableOp(a_default_path=SQLITE_DB_DIR)
else:
    tableOp = TableOp(a_dbfile=result.file, a_default_path=SQLITE_DB_DIR)


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
         if ms_pat_1.search(t) is None if ms_pat_2.match(t) is None]
    return ormClasses


"""
Check sites
"""
if result.site == 'both':
    if result.table_name == 'all':
        import unicodedata

        session_pp = pp_conn.GetSession()
        for orm_c in GetOrmClasses('pp'):
            result = session_pp.query(orm_c).all()
            if result is not None:
                tableOp.Backup(result, 'pp')

        session_ss = ss_conn.GetSession()
        for orm_c in GetOrmClasses('ss'):
            result = session_ss.query(orm_c).all()
            if result is not None:
                tableOp.Backup(result, 'ss')
    else:
        table_pp_c = GenTable(result.table_name, pp_conn.GetEngine())
        table_ss_c = GenTable(result.table_name, ss_conn.GetEngine())
        session_pp = pp_conn.GetSession()
        session_ss = ss_conn.GetSession()

        result_pp = session_pp.query(table_pp_c).all()
        result_ss = session_ss.query(table_ss_c).all()

        if result_pp.__len__() == 0:
            print("Protected Site Table : " + result.table_name + " has no data.")
        if result_ss.__len__() == 0:
            print("Recovery Site Table : " + result.table_name + " has no data.")

        tableOp.Backup(result_pp, 'pp')
        tableOp.Backup(result_ss, 'ss')


elif result.site == 'pp':
    if result.table_name == 'all':
        import unicodedata

        session_pp = pp_conn.GetSession()
        for orm_c in GetOrmClasses('pp'):
            result = session_pp.query(orm_c).all()
            if result is not None:
                tableOp.Backup(result, 'pp')

    else:
        table_pp_c = GenTable(result.table_name, pp_conn.GetEngine())
        session_pp = pp_conn.GetSession()

        result_pp = session_pp.query(table_pp_c).all()
        if result_pp.__len__() == 0:
            print("Protected Site Table : " + result.table_name + " has no data.")

        tableOp.Backup(result_pp, 'pp')

elif result.site == 'ss':
    if result.table_name == 'all':
        import unicodedata

        session_ss = ss_conn.GetSession()
        for orm_c in GetOrmClasses('ss'):
            result = session_ss.query(orm_c).all()
            if result is not None:
                tableOp.Backup(result, 'ss')
    else:
        table_ss_c = GenTable(result.table_name, ss_conn.GetEngine())
        session_ss = ss_conn.GetSession()

        result_ss = session_ss.query(table_ss_c).all()
        if result_ss.__len__() == 0:
            print("Recovery Site Table : " + result.table_name + " has no data.")

        tableOp.Backup(result_ss, 'ss')
