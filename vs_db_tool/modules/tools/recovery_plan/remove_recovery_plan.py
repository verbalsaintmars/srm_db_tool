from vs_db_tool.orm.srm import pdr_planproperties
from vs_db_tool.orm.srm import pdr_plancontents
from vs_db_tool.orm.srm import pdr_protectiongroupmap
from vs_db_tool.orm.srm import g_do_array

from vs_db_tool.formatter.layout import PrintResult

from vs_db_tool.backup_tables_mgr.dbop import TableOp
from vs_db_tool.backup_tables_mgr.fm import DbFileOp

tableop = dbop.TableOp()
tableop.Backup([pp_result], a_site="pp")
tableop.Backup([ss_result], a_site="ss")


class RemoveRecoveryPlan(object):

    def __init__(this, a_pp_conn, a_ss_conn, a_formatter=PrintResult()):
        this.pp_conn = a_pp_conn
        this.ss_conn = a_ss_conn
        this.formatter = a_formatter

    def __call__(this, a_name=None):
        if a_name is None:
            print("Please enter the Recover Plan we want to remove...")
            return



