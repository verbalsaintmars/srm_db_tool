from srm_db_tool.orm.srm import pdr_planproperties
from srm_db_tool.orm.srm import pdr_plancontents
from srm_db_tool.orm.srm import pdr_protectiongroupmap
from srm_db_tool.orm.srm import g_do_array

from srm_db_tool.formatter.layout import PrintResult

from srm_db_tool.backup_tables_mgr.dbop import TableOp
from srm_db_tool.backup_tables_mgr.fm import DbFileOp
from srm_db_tool.exception.predefined import MODULE_EXCEPT_FORMAT

from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound

#tableop = dbop.TableOp()
#tableop.Backup([pp_result], a_site="pp")
#tableop.Backup([ss_result], a_site="ss")


class RemoveRecoveryPlan(object):

    def __init__(this, a_pp_conn, a_ss_conn, a_formatter=PrintResult()):
        this.pp_conn = a_pp_conn
        this.ss_conn = a_ss_conn
        this.formatter = a_formatter
        this.tableop = TableOp()
        this.pdr_planproperties_c = None
        this.pdr_plancontents_c = None
        this.pdr_protectiongroupmap_c = None

    def GetPP_Conn(this):
        return this.pp_conn

    def GetSS_Conn(this):
        return this.ss_conn

    def GetTableOp(this):
        return this.tableop

    def GetPP(this):
        return this.pdr_planproperties_c

    def GetPC(this):
        return this.pdr_plancontents_c

    def GetPG(this):
        return this.pdr_protectiongroupmap_c

    def Backup(this, a_result_list, a_site="pp"):
        this.tableop.Backup(a_result_list, a_site)

    def Remove(this, a_datum, a_site):
        session = None
        if a_site == 'pp':
            session = this.pp_conn.GetSession()
        if a_site == 'ss':
            session = this.ss_conn.GetSession()
        session.delete(a_datum)
        session.commit()


    def CreateTableSessionPair(this, a_table, a_site='pp'):
        session = None
        table_c = None

        if a_site == 'pp':
            session = this.pp_conn.GetSession() #GetSession cache's , thus no bad use
            table_c = a_table.GetTable(this.pp_conn.GetEngine())

        if a_site == 'ss':
            session = this.ss_conn.GetSession()
            table_c = a_table.GetTable(this.ss_conn.GetEngine())

        return (table_c, session)

    def List_pdr_planproperties(this, a_name, a_site):
        pair = this.CreateTableSessionPair(
            pdr_planproperties, a_site)

        this.pdr_planproperties_c = pair[0]

        try:
            result = pair[1].query(pair[0]).filter(
                pair[0].name.like(a_name)).one()

            return result

        except (MultipleResultsFound, NoResultFound) as e:
            print(MODULE_EXCEPT_FORMAT.format(__name__, e))
            return None


    def List_pdr_plancontents(this, a_db_id, a_site):
        pair = this.CreateTableSessionPair(
            pdr_plancontents, a_site)

        this.pdr_plancontents_c = pair[0]

        try:
            result = pair[1].query(pair[0]).filter(
                pair[0].db_id==a_db_id).one()

            return result

        except (MultipleResultsFound, NoResultFound) as e:
            print(MODULE_EXCEPT_FORMAT.format(__name__, e))
            return None

    def Map_g_do_array(this, a_protectiongroups, a_site):
        pair = this.CreateTableSessionPair(
            g_do_array, a_site)

        try:
            result = pair[1].query(pair[0]).filter(
                pair[0].seq_id==a_protectiongroups).one()

            return result

        except (MultipleResultsFound, NoResultFound) as e:
            print(MODULE_EXCEPT_FORMAT.format(__name__, e))
            return None

    def List_pdr_protectiongroupmap(this, a_db_id, a_site):
        pair = this.CreateTableSessionPair(
            pdr_protectiongroupmap, a_site)

        this.pdr_protectiongroupmap_c = pair[0]

        try:
            result = pair[1].query(pair[0]).filter(
                pair[0].db_id==a_db_id).one()

            return result

        except (MultipleResultsFound, NoResultFound) as e:
            print(MODULE_EXCEPT_FORMAT.format(__name__, e))
            return None

    def __call__(this, a_name=None, a_site="pp"):
        if a_name is None:
            print("Please enter the Recover Plan we want to remove...")
            return

        pdr_pp = this.List_pdr_planproperties(a_name, a_site)
        if pdr_pp is None:
            print("Recovery Plan : {} does not exist inside the database".\
                  format(a_name))
            return
        # print(pdr_pp.contents)
        pdr_pc = this.List_pdr_plancontents(pdr_pp.contents, a_site)
        if pdr_pc is None:
            print("Recovery Plan : {} does not exist inside the database".\
                  format(a_name))
            return
        # print(pdr_pc.protectiongroups)
        pdr_go_do_array = this.Map_g_do_array(pdr_pc.protectiongroups, a_site)
        # print(pdr_go_do_array.db_id)
        pdr_pg = this.List_pdr_protectiongroupmap(pdr_go_do_array.db_id, a_site)
        # print(pdr_pg.localgroupmoid)

        # backup
        try:
            this.Backup([pdr_pp], a_site)
            this.Backup([pdr_pc], a_site)
            this.Backup([pdr_pg], a_site)
            this.Backup([pdr_go_do_array], a_site)
        except Exception as e:
            print(MODULE_EXCEPT_FORMAT.format(__name__, e))
        else:
            this.Remove(pdr_pp, a_site)
            this.Remove(pdr_pc, a_site)
            this.Remove(pdr_pg, a_site)

    TABLEOP = property(GetTableOp)
    PP = property(GetPP)
    PC = property(GetPC)
    PG = property(GetPG)
    PP_CONN = property(GetPP_Conn)
    SS_CONN = property(GetSS_Conn)
