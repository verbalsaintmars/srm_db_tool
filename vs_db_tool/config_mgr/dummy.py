from ..sqlalchemy.db_support.init_params import Init_Params
from ..sqlalchemy.make_conn import MakeConn

params_hq = Init_Params()
params_hq.DBTYPE = 'mssql'
params_hq.HOST = '10.20.233.103'
params_hq.UID = 'ad'
params_hq.PWD = 'ca$hc0w'
params_hq.DB = '01_HQ'

ProtectedSiteConn = MakeConn(params_hq)

params_rh = Init_Params()
params_rh.DBTYPE = 'mssql'
params_rh.HOST = '10.20.233.103'
params_rh.UID = 'ad'
params_rh.PWD = 'ca$hc0w'
params_rh.DB = '01_RH'

ReconverSiteConn= MakeConn(params_rh)
