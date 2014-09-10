from ..config_mgr import dummy as connection

from ..modules import *

lsrp = ListRecoveryPlan(connection.HQconn, connection.RHconn)
lsrp.pp('HQ-DATA24-RecoveryPlan')
lsrp.pp()
lsrp.ss('HQ-DATA24-RecoveryPlan')
lsrp.ss()
