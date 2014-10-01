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
#result = parser.parse_args(['pd_moref', '-f', 'testME2.db'])
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


from srm_db_tool.backup_tables_mgr.dbop import TableOp
from srm_db_tool.orm.gentable import GenTable

tableOp = None

if result.file == 'default':
    tableOp = TableOp(a_default_path=SQLITE_DB_DIR)
else:
    tableOp = TableOp(a_dbfile=result.file, a_default_path=SQLITE_DB_DIR)


import sys
if result.site == "both":
    if pp_conn is None:
        print("Choose to back up both site, "
              "but no complete protected Site DB "
              "Connection information provided.")
        sys.exit()
    if ss_conn is None:
        print("Choose to back up both site, "
              "but no complete recovery Site DB "
              "Connection information provided.")
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
         a_table=metadata.tables[t]) for t in metadata.tables]
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
