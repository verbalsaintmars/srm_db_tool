from srm_db_tool.formatter.layout import PrintResult
from srm_db_tool.orm.gentable import GenTable

from srm_db_tool.exception.predefined import MODULE_EXCEPT_FORMAT


class RestoreRecoveryPlan(object):

    def __init__(
        this,
        a_pp_conn,
        a_ss_conn,
        a_tableop,
            a_formatter=PrintResult()):

        this.pp_conn = a_pp_conn
        this.ss_conn = a_ss_conn
        this.formatter = a_formatter
        this.tableop = a_tableop

        this.pdr_planproperties_c =\
            GenTable("pdr_planproperties", this.pp_conn.GetEngine())

        this.pdr_plancontents_c =\
            GenTable("pdr_plancontents", this.pp_conn.GetEngine())

        this.pdr_protectiongroupmap_c =\
            GenTable("pdr_protectiongroupmap", this.pp_conn.GetEngine())

        this.g_do_array_c =\
            GenTable("g_do_array", this.pp_conn.GetEngine())

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
        except Exception as e:
            return

    def Recover(this, a_name, a_site):
        # TODO
        # 2 ways commit

        pp_result = this.tableop.Restore(this.pdr_planproperties_c, a_site)
        pc_result = this.tableop.Restore(this.pdr_plancontents_c, a_site)
        pg_result = this.tableop.Restore(this.pdr_protectiongroupmap_c, a_site)
        g_do_array_result = this.tableop.Restore(this.g_do_array_c, a_site)

        print("hahah: " + str(g_do_array_result.__len__()))

        pdr_pp = [r for r in pp_result if r.name == a_name][0]

        pdr_pc = [r for r in pc_result if r.db_id == pdr_pp.contents][0]

        go_id_list =\
            [r for r in g_do_array_result
             if r.seq_id == pdr_pc.protectiongroups]

        print("hahah2: " + str(go_id_list.__len__()))

        pdr_pg_list = []

        for go_id in go_id_list:
            pdr_pg_list.append(
                [r for r in pg_result if r.db_id == go_id.db_id][0])

        print("hahah3: " + str(pdr_pg_list.__len__()))

        session = None

        if a_site == 'pp':
            session = this.pp_conn.GetSession()
        if a_site == 'ss':
            session = this.ss_conn.GetSession()

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

    def __call__(this, a_name=None, a_site="pp"):
        if a_name is None:
            print("Please enter the Recover Plan we want to restore...")
            return

        this.Recover(a_name, a_site)
