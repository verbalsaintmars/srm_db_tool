from srm_db_tool.formatter.layout import PrintResult
from srm_db_tool.orm.gentable import GenTable
from srm_db_tool.backup_tables_mgr.module import Module
from srm_db_tool.backup_tables_mgr.generaldbop import GeneralDbOp

from srm_db_tool.exception.predefined import MODULE_EXCEPT_FORMAT


class RestoreRecoveryPlan(object):

    def __init__(
        this,
        a_conn,
        a_tableop,
            a_formatter=PrintResult()):

        this.the_conn = a_conn
        this.formatter = a_formatter
        this.tableop = a_tableop

        this.pdr_planproperties_c =\
            GenTable("pdr_planproperties", this.the_conn.GetEngine())

        this.pdr_plancontents_c =\
            GenTable("pdr_plancontents", this.the_conn.GetEngine())

        this.pdr_protectiongroupmap_c =\
            GenTable("pdr_protectiongroupmap", this.the_conn.GetEngine())

        this.g_do_array_c =\
            GenTable("g_do_array", this.the_conn.GetEngine())

    def PrintResult(this, a_result):
        this.formatter.PrintRecoveryPlan(a_result)

    def list(this, a_site="pp"):
        """
        List backed-up RP
        """
        result = this.tableop.Restore(this.pdr_planproperties_c, a_site)

        try:
            for r in result:
                this.PrintResult(r)
        except Exception:
            return

    def Recover(this, a_name):

        pp_result = this.tableop.Restore("pdr_planproperties")
        pc_result = this.tableop.Restore("pdr_plancontents")
        pg_result = this.tableop.Restore("pdr_protectiongroupmap")
        g_do_array_result = this.tableop.Restore("g_do_array")

        pdr_pp = [r for r in pp_result if r.name == a_name][0]

        pdr_pc = [r for r in pc_result if r.db_id == pdr_pp.contents][0]

        go_id_list =\
            [r for r in g_do_array_result
             if r.seq_id == pdr_pc.protectiongroups]

        pdr_pg_list = []

        for go_id in go_id_list:
            pdr_pg_list.append(
                [r for r in pg_result if r.db_id == go_id.db_id][0])

        session = this.the_conn.GetSession()

        pp_obj = this.pdr_planproperties_c()
        pc_obj = this.pdr_plancontents_c()

        for c in this.pdr_planproperties_c.__table__.c:
            setattr(pp_obj, c.name, getattr(pdr_pp, c.name))

        for c in this.pdr_plancontents_c.__table__.c:
            setattr(pc_obj, c.name, getattr(pdr_pc, c.name))

        for pdr_pg in pdr_pg_list:
            pg_obj = this.pdr_protectiongroupmap_c()
            for c in this.pdr_protectiongroupmap_c.__table__.c:
                setattr(pg_obj, c.name, getattr(pdr_pg, c.name))
            session.add(pg_obj)
            session.commit()

        # for c in this.g_do_array_c.__table__.c:
            # setattr(dor_obj, c.name, getattr(go_id, c.name))
        try:
            session.add(pp_obj)
            session.add(pc_obj)
            session.commit()
        except Exception as e:
            print(MODULE_EXCEPT_FORMAT.format(__name__, e))
        else:
            pass
            """ don't remove backup data
            try:
                this.RemoveBackup(pdr_pp)
                this.RemoveBackup(pdr_pc)
                this.RemoveBackup(pdr_pg)
                this.RemoveBackup(go_id)
            except Exception as e:
                print(MODULE_EXCEPT_FORMAT.format(__name__, e))
             """

    def RemoveBackup(this, a_datum):
        this.tableop.Remove(a_datum)

    def __call__(this, a_name=None):
        if a_name is None:
            print("Please enter the Recover Plan we want to restore...")
            return

        this.Recover(a_name)

        """
        Insert into srm_meta_table_fixby table if possible
        """
        gdbop = GeneralDbOp(this.the_conn)
        if gdbop.LOCK:
            gdbop.LOCK = 0

        if gdbop.MODULE is not None:
            """
            Create a Module type instance to describe and insert into
                srm_meta_table_fixby table
            """
            module = Module()
            module.NAME = "restorerp"
            module.DESC = "restore recovery plan"
            gdbop.MODULE = module

        if gdbop.LOCK == 0:
            gdbop.LOCK = 1
