from srm_db_tool.orm.gentable import GenTable
from srm_db_tool.formatter.layout import PrintResult
from srm_db_tool.exception.predefined import MODULE_EXCEPT_FORMAT

from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound


class RemoveRecoveryPlan(object):

    def __init__(
        this,
        a_pp_conn,
        a_ss_conn,
        a_tableop,
            a_formatter=PrintResult()):

        this.pp_conn = a_pp_conn
        this.ss_conn = a_ss_conn
        this.formatter = a_formatter
        # this.tableop = TableOp()
        this.tableop = a_tableop
        this.pdr_planproperties_c = None
        this.pdr_plancontents_c = None
        this.pdr_protectiongroupmap_c = None

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

    def CreateTableSessionPair(this, a_table_name, a_site='pp'):
        session = None
        table_c = None

        if a_site == 'pp':
            # GetSession cache's , thus no bad use
            session = this.pp_conn.GetSession()
            table_c = GenTable(a_table_name, this.pp_conn.GetEngine())

        if a_site == 'ss':
            session = this.ss_conn.GetSession()
            table_c = GenTable(a_table_name, this.ss_conn.GetEngine())

        return (table_c, session)

    def List_pdr_planproperties(this, a_name, a_site):
        pair = this.CreateTableSessionPair(
            "pdr_planproperties", a_site)

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
            "pdr_plancontents", a_site)

        this.pdr_plancontents_c = pair[0]

        try:
            result = pair[1].query(pair[0]).filter(
                pair[0].db_id == a_db_id).one()

            return result

        except (MultipleResultsFound, NoResultFound) as e:
            print(MODULE_EXCEPT_FORMAT.format(__name__, e))
            return None

    def Map_g_do_array(this, a_protectiongroups, a_site):
        pair = this.CreateTableSessionPair(
            "g_do_array", a_site)

        try:
            result = pair[1].query(pair[0]).filter(
                pair[0].seq_id == a_protectiongroups).all()

            return result

        except (MultipleResultsFound, NoResultFound) as e:
            print(MODULE_EXCEPT_FORMAT.format(__name__, e))
            return None

    def List_pdr_protectiongroupmap(this, a_list, a_site):
        pair = this.CreateTableSessionPair(
            "pdr_protectiongroupmap", a_site)

        this.pdr_protectiongroupmap_c = pair[0]

        result = []

        try:
            for do_array in a_list:
                result.append(
                    pair[1].query(pair[0]).filter(
                        pair[0].db_id == do_array.db_id).one())

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
            print("Recovery Plan : {} does not exist inside the database".
                  format(a_name))
            return
        # print(pdr_pp.contents)
        pdr_pc = this.List_pdr_plancontents(pdr_pp.contents, a_site)
        if pdr_pc is None:
            print("Recovery Plan : {} does not exist inside the database".
                  format(a_name))
            return

        # print(pdr_pc.protectiongroups)
        pdr_go_do_array_list =\
            this.Map_g_do_array(pdr_pc.protectiongroups, a_site)

        if pdr_go_do_array_list is None or pdr_go_do_array_list.__len__() == 0:
            print("Oh oh~, "
                  "mapping from pdr_plancontents.protectionsgroups: {} "
                  "to go_do_array has problems..".
                  format(pdr_pc.protectiongroups))
            return

        # print(pdr_go_do_array.db_id)
        pdr_pg_list = this.List_pdr_protectiongroupmap(
            pdr_go_do_array_list,
            a_site)
        # print(pdr_pg.localgroupmoid)

        # backup
        try:
            this.Backup([pdr_pp], a_site)
            this.Backup([pdr_pc], a_site)
            this.Backup(pdr_pg_list, a_site)
            this.Backup(pdr_go_do_array_list, a_site)
        except Exception as e:
            print(MODULE_EXCEPT_FORMAT.format(__name__, e))
        else:
            this.Remove(pdr_pp, a_site)
            this.Remove(pdr_pc, a_site)
            for pdr_pg in pdr_pg_list:
                this.Remove(pdr_pg, a_site)
