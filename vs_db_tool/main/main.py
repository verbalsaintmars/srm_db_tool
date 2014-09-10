from ..config_mgr import dummy as connection

from ..modules import *

lsrp = ListRecoveryPlan(connection.ProtectedSiteConn, connection.ReconverSiteConn)

pp_result = lsrp.pp('HQ-DATA24-RecoveryPlan')
lsrp.pp()
ss_result = lsrp.ss('HQ-DATA24-RecoveryPlan')
lsrp.ss()

re = lsrp('HQ-DATA24-RecoveryPlan')


from ..backup_tables_mgr import dbop
from ..backup_tables_mgr import fm

tableop = dbop.TableOp()
tableop.Backup([pp_result], a_site="pp")
tableop.Backup([ss_result], a_site="ss")



from vs_db_tool.orm.srm import pdr_planproperties

pp_restore_result =\
    tableop.Restore(pdr_planproperties.GetTable(connection.ProtectedSiteConn.GetEngine()), a_site='pp')
ss_restore_result =\
    tableop.Restore(pdr_planproperties.GetTable(connection.ReconverSiteConn.GetEngine()), a_site='ss')
