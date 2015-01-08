from srm_db_tool.orm.gentable import GenTable
from srm_db_tool.modules.tools.version_check.version_check import GetSrmVersion
from srm_db_tool.formatter.layout import PrintResult
from srm_db_tool.exception.predefined import MODULE_EXCEPT_FORMAT
from srm_db_tool.backup_tables_mgr.dumptype import DumpType
from srm_db_tool.backup_tables_mgr.module import Module
from srm_db_tool.backup_tables_mgr.generaldbop import GeneralDbOp

from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound


class RemoveRecoveryPlan(object):

    def __init__(
        this,
        a_conn,
        a_tableop,
        a_pr=None,
        a_kb=None,
        a_desc=None,
            a_formatter=PrintResult()):

        this.conn = a_conn
        this.formatter = a_formatter
        # this.tableop = TableOp()
        this.tableop = a_tableop
        this.pr = a_pr
        this.kb = a_kb
        this.desc = a_desc
        this.pdr_planproperties_c = None
        this.pdr_plancontents_c = None
        this.pdr_protectiongroupmap_c = None

    def Backup(this, a_result_list, a_site="pp", a_version=None):
        dumptype = DumpType.CUSTOMIZED
        dumptype.TYPE = 'rmrp'

        this.tableop.Backup(
            a_result_list,
            a_version,
            "primary" if a_site == 'pp' else "secondary",
            dumptype,
            None,
            this.pr,
            this.kb,
            this.desc,
            False)

    def Remove(this, a_datum):
        session = this.conn.GetSession()
        session.delete(a_datum)
        session.commit()

    def CreateTableSessionPair(this, a_table_name):
        session = this.conn.GetSession()
        table_c = GenTable(a_table_name, this.conn.GetEngine())

        return (table_c, session)

    def List_pdr_planproperties(this, a_name):
        pair = this.CreateTableSessionPair(
            "pdr_planproperties")

        this.pdr_planproperties_c = pair[0]

        try:
            result = pair[1].query(pair[0]).filter(
                pair[0].name.like(a_name)).one()

            return result

        except (MultipleResultsFound, NoResultFound) as e:
            print(MODULE_EXCEPT_FORMAT.format(__name__, e))
            return None

    def List_pdr_plancontents(this, a_db_id):
        pair = this.CreateTableSessionPair(
            "pdr_plancontents")

        this.pdr_plancontents_c = pair[0]

        try:
            result = pair[1].query(pair[0]).filter(
                pair[0].db_id == a_db_id).one()

            return result

        except (MultipleResultsFound, NoResultFound) as e:
            print(MODULE_EXCEPT_FORMAT.format(__name__, e))
            return None

    def Map_g_do_array(this, a_protectiongroups):
        pair = this.CreateTableSessionPair(
            "g_do_array")

        try:
            result = pair[1].query(pair[0]).filter(
                pair[0].seq_id == a_protectiongroups).all()

            return result

        except (MultipleResultsFound, NoResultFound) as e:
            print(MODULE_EXCEPT_FORMAT.format(__name__, e))
            return None

    def List_pdr_protectiongroupmap(this, a_list):
        pair = this.CreateTableSessionPair(
            "pdr_protectiongroupmap")

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

        from srm_db_tool.backup_tables_mgr.dumptype import DumpType

        sqlop = GeneralDbOp(a_conn=this.conn, a_create_meta_table=False)

        if sqlop.DUMPTYPE is not None and\
           sqlop.DUMPTYPE != DumpType.ALL and\
           sqlop.DUMPTYPE.TYPE != 'rp':
            print("Dumped database does not contain Recovery Plan tables.")
            return

        version = GetSrmVersion(this.conn, a_site)[1]

        pdr_pp = this.List_pdr_planproperties(a_name)
        if pdr_pp is None:
            print("Recovery Plan : {} does not exist inside the database".
                  format(a_name))
            return

        # print(pdr_pp.contents)
        pdr_pc = this.List_pdr_plancontents(pdr_pp.contents)
        if pdr_pc is None:
            print("Recovery Plan : {} : pdr_plancontents does not has"
                  " pdr_planproperties.contents' reference".
                  format(a_name))
            return

        # print(pdr_pc.protectiongroups)
        pdr_go_do_array_list =\
            this.Map_g_do_array(pdr_pc.protectiongroups)

        if pdr_go_do_array_list is None or pdr_go_do_array_list.__len__() == 0:
            print("Oh oh~, "
                  "mapping from pdr_plancontents.protectionsgroups: {} "
                  "to go_do_array has problems..".
                  format(pdr_pc.protectiongroups))
            return

        # print(pdr_go_do_array.db_id)
        pdr_pg_list = this.List_pdr_protectiongroupmap(
            pdr_go_do_array_list)
        # print(pdr_pg.localgroupmoid)

        # backup
        try:
            backup_data = [pdr_pp, pdr_pc]

            for o in pdr_pg_list:
                backup_data.append(o)

            for o in pdr_go_do_array_list:
                backup_data.append(o)

            this.Backup(backup_data, a_site, version)
            """
            this.Backup([pdr_pc], a_site, version)
            this.Backup(pdr_pg_list, a_site, version)
            this.Backup(pdr_go_do_array_list, a_site, version)
            """
        except Exception as e:
            print(MODULE_EXCEPT_FORMAT.format(__name__, e))
        else:
            this.Remove(pdr_pp)
            this.Remove(pdr_pc)
            for pdr_pg in pdr_pg_list:
                this.Remove(pdr_pg)
            """
            Insert into srm_meta_table_fixby table if possible
            """
            gdbop = None

            gdbop = GeneralDbOp(this.conn)

            if gdbop.LOCK:
                gdbop.LOCK = 0

            if gdbop.MODULE is not None:
                """
                Create a Module type instance to describe and insert into
                    srm_meta_table_fixby table
                """
                module = Module()
                module.NAME = "rmrp"
                module.DESC = "remove recovery plan"
                gdbop.MODULE = module

            if gdbop.LOCK == 0:
                gdbop.LOCK = 1
