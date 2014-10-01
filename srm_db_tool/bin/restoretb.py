import argparse
from srm_db_tool.modules.tools.backup_restore_tb.argparse_parent \
    import version_parser as parent_parser

ap_args = {'prog': 'restoretb',
           'description': 'Restore SRM database tables',
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
                   "or 'all' to restore the whole database"}

parser.add_argument('table_name', **table_name_args)


"""
sqlite db file name
"""
dbfilename_args = {'type': str,
                   'nargs': '?',
                   'default': 'default',
                   'help': "sqlite db file name or use the latest generated name."}

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
from srm_db_tool.backup_tables_mgr.fm import DbFileOp
from srm_db_tool.orm.gentable import GenTable

tableOp = None

if result.file == 'default':
    filename = DbFileOp(SQLITE_DB_DIR).LatestFileName(False)
    tableOp = TableOp(a_dbfile=filename, a_default_path=SQLITE_DB_DIR)
    result.file = filename
else:
    tableOp = TableOp(a_dbfile=result.file, a_default_path=SQLITE_DB_DIR)


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


import re
ms_pat_1 = 'spt_'
ms_pat_2 = 'MSreplication_options'
ms_pat_1 = re.compile(ms_pat_1)
ms_pat_2 = re.compile(ms_pat_2)


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


def DeleteAndRestore(a_table_name, a_site, a_force=False):
    engine = pp_conn.GetEngine() if a_site == 'pp' else ss_conn.GetEngine()
    session = pp_conn.GetSession() if a_site == 'pp' else ss_conn.GetSession()
    site_name = "Protected" if a_site == 'pp' else "Recovery"

    table_c = GenTable(a_table_name, engine)

    restore_result = tableOp.Restore(table_c, a_site)

    if restore_result is None:
        print("Recovery db file: "
              + result.file + " has no backup table: "
              + a_table_name + " for " + site_name + " site")
        if a_force is True:
            engine.execute(table_c.__table__.delete())

    elif restore_result.__len__() == 0:
        print("Recovery db file: "
              + result.file + " has no data for " + site_name + " site table: "
              + a_table_name)
        if a_force is True:
            engine.execute(table_c.__table__.delete())

    else:
        engine.execute(table_c.__table__.delete())

    if restore_result is not None:
        for orm_o in restore_result:
            local_orm_o = table_c()
            for c in table_c.__table__.c:
                setattr(local_orm_o, c.name, getattr(orm_o, c.name))
            session.add(local_orm_o)
            session.commit()


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
            DeleteAndRestore(str_tname, 'pp', True)

        l_tables = ReflectDb('ss').tables
        for tname in l_tables:
            if ms_pat_1.search(tname) is not None:
                continue
            if ms_pat_2.match(tname) is not None:
                continue
            str_tname = unicodedata.normalize('NFKD', tname).\
                encode('ascii', 'ignore')
            DeleteAndRestore(str_tname, 'ss', True)

    else:
        DeleteAndRestore(result.table_name, 'pp')
        DeleteAndRestore(result.table_name, 'ss')

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
            DeleteAndRestore(str_tname, 'pp', True)
    else:
        DeleteAndRestore(result.table_name, 'pp')


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
            DeleteAndRestore(str_tname, 'ss', True)
    else:
        DeleteAndRestore(result.table_name, 'ss')
