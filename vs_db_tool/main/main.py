from vs_db_tool.config_mgr.dummy import params
from vs_db_tool.sqlalchemy import giveme_conn as gmc

from vs_db_tool.orm.srm import pd_licenseasset



cc = gmc.CreateConn(params)

pdl_table = pd_licenseasset.GetTable(cc.GetEngine())

session = cc.GetSession()

result = session.query(pdl_table).first()


"""
Test RP
"""
from vs_db_tool.modules.check.recovery_plan import chk_rp
result2 = chk_rp.CheckRP(cc).HasRP('TEST-RP-HAHAHA')








