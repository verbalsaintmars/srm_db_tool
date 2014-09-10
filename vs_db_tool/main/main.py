from ..config_mgr import dummy as connection

from ..modules import *

lsrp = ListRecoveryPlan(connection.HQconn, connection.RHconn)
pp_result = lsrp.pp('HQ-DATA24-RecoveryPlan')
lsrp.pp()
ss_result = lsrp.ss('HQ-DATA24-RecoveryPlan')
lsrp.ss()

from ..backup_tables_mgr import dbop
from ..backup_tables_mgr import fm

tableop = dbop.TableOp()
tableop.Backup([pp_result], a_site="pp")
tableop.Backup([ss_result], a_site="ss")

from vs_db_tool.orm.srm import pdr_planproperties

pp_restore_result =\
    tableop.Restore(pdr_plancontents.GetTable(connection.HQconn.GetEngine()), a_site='pp')
ss_restore_result =\
    tableop.Restore(pdr_plancontents.GetTable(connection.RHconn.GetEngine()), a_site='ss')
