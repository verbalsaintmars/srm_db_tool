from ..config_mgr import dummy as connection

from ..modules import *
lsrp = ListRecoveryPlan(connection.ProtectedSiteConn, connection.ReconverSiteConn)



"""
from ..backup_tables_mgr import dbop
from ..backup_tables_mgr import fm

tableop = dbop.TableOp()
tableop.Backup([pp_result], a_site="pp")
tableop.Backup([ss_result], a_site="ss")
"""

"""
from vs_db_tool.orm.srm import pdr_planproperties

pp_restore_result =\
    tableop.Restore(pdr_planproperties.GetTable(connection.ProtectedSiteConn.GetEngine()), a_site='pp')
ss_restore_result =\
    tableop.Restore(pdr_planproperties.GetTable(connection.ReconverSiteConn.GetEngine()), a_site='ss')
"""

rmrp = RemoveRecoveryPlan(connection.ProtectedSiteConn, connection.ReconverSiteConn)


from ..backup_tables_mgr import dbop
tableop = dbop.TableOp(
    r'C:\Source\db-tool\vs_db_tool\backup_tables_mgr\sqlite_tmp\sqlite_db_0024.db')

recoverrp = RecoverRecoveryPlan(
    connection.ProtectedSiteConn,
    connection.ReconverSiteConn,
    tableop)

"""
tableop = dbop.TableOp(
    r'C:\Source\db-tool\vs_db_tool\backup_tables_mgr\sqlite_tmp\sqlite_db_0009.db')

recoverp = RecoveryRecoveryPlan(
    connection.ProtectedSiteConn,
    connection.ReconverSiteConn,
    tableop)

re = recoverp.list()
re = recoverp.list('ss')
#re = rmrp('HQ-DATA24-RecoveryPlan', 'pp')
#re = rmrp('HQ-DATA24-RecoveryPlan', 'ss')
"""
