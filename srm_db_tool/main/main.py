from ..config_mgr.dummy import *

from ..modules import *



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



#from ..backup_tables_mgr import dbop
#tableop = dbop.TableOp(
#    r'C:\Source\db-tool\vs_db_tool\backup_tables_mgr\sqlite_tmp\sqlite_db_0024.db')

#recoverrp = RecoverRecoveryPlan(
#    connection.ProtectedSiteConn,
#    connection.ReconverSiteConn,
#    tableop)

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

"""
from ..orm.srm import g_do_array
from ..backup_tables_mgr import dbop

tableop = dbop.TableOp()

g_do_array_c = g_do_array.GetTable(connection.ProtectedSiteConn.GetEngine())
pp_session = connection.ProtectedSiteConn.GetSession()

result = pp_session.query(g_do_array_c).all()

tableop.Backup(result)
"""









from ..backup_tables_mgr.dbop import TableOp


# list recovery plan module
lsrp = ListRecoveryPlan(pp_conn, ss_conn)

# remove recovery plan module
rmrp = RemoveRecoveryPlan(pp_conn, ss_conn)

# recover recovery plan module
recoverrp = RecoverRecoveryPlan(
            pp_conn,
            ss_conn,
            rmrp.TABLEOP)

"""
GSS/CU user

# lsrp()
List Recovery Plan that is healthy on both site

# lsrp('Recovery Plan Name')
Print out Recovery Plan details on both site. Including moid info

# lsrp.pp()
list Recovery Plan on Protected site

# lsrp.pp('Recovery Plan Name')
Print out details of this recovery plan


# lsrp.ss()
list Recovery Plan on Recovery site

# lsrp.ss('Recovery Plan Name')
Print out details of this recovery plan


# rmrp('Recovery plan name')
Remove the recovery plan on Protected site

# rmrp('Recovery plan name', 'ss')
Remove the recovery plan on Recovery site

# recoverrp.list()
List the Recovery Plan that has been backedup on Protected Site

# recoverrp.list('ss')
List the Recovery Plan that has been backedup on Recovery Site

# recoverrp('Recovery plan name')
Recover Recovery Plan back to SRM DB on Protected Site

# recoverrp('Recovery plan name', 'ss')
Recover Recovery Plan back to SRM DB on Recovery Site

# recoverrp.DB = r'SQLITE DB FILE NAME'
this will allow recoverrp engine to recover data from this backuped sqlite db
you could always use
 recoverrp.list()
to list the recovery plans that are backedup in this sqlite db
"""






"""
For Dev

How we manipulate SRM DB Tables?

Easy.

1.
I want to manipulate with table
    dr_product_info

2.
under
    srm_db_tool\orm\srm
make a copy of the file:
    table_template.py
and rename to
    dr_product_info.py

3.
put these on the top of your python module file

    from srm_db_tool.sqlalchemy.make_conn import MakeConn
    from srm_db_tool.sqlalchemy.db_support.init_params import Init_Params

    from srm_db_tool.orm.srm import dr_product_info


4.
Have the remote DB connection info ready

    params_hq = Init_Params()
    params_hq.DBTYPE = 'mssql'
    params_hq.HOST = '10.20.233.103'
    params_hq.UID = 'ad'
    params_hq.PWD = 'ca$hc0w'
    params_hq.DB = '01_HQ'

    conn = MakeConn(params_hq)

5.
Let's get the dr_product_info table class (which magically have the schema ready)

    dr_p_i_c = dr_product_info.GetTable(conn.GetEngine())

6.
Create a session and...
    session = conn.GetSession()

7.
Grab your data...
    result = session.query(dr_p_i_c).all()
    value_list = [r.value for r in result]

8.
Want to update the value? No problem!
    value = result[0]
    value.name = 'wa hahahaha!!'
    session.commit()

That's it. How's that?

9.
Add data? No problem!
    val = dr_p_i_c(name='picacho', value='1.0.0')
    session.add(val)
    session.commit()
done~

10.
Hell, wrong adding, remove it!
    session.delete(val)
    session.commit()
done again.



Let's do some backup of SRM DB.

Auh, I mean, how about the whole table data?

1.
Add this on the first line of your python module
    from srm_db_tool.backup_tables_mgr.dbop import TableOp
    from srm_db_tool.orm.srm import g_string_array


2.
Let's backup table
    g_string_array
for testing

as previous steps, make sure
    g_string_array.py
ready under srm_db_tool\orm\srm


3.
Create the tableop object
    tableop = TableOp() # could also pass in sqlite db file location to use that sqlite db


4.
    gsa_c = g_string_array.GetTable(conn.GetEngine())
    result = session.query(gsa_c).all()
    tableop.Backup(result)
done~

5.
List the tables inside the sqlite db
    tableop.ListTables()

6.
List version of the table
    tableop.ListVersion(gsa_c) # protected site
    tableop.ListVersion(gsa_c, 'ss') # recovery site

7.
Get backedup data from sqlite
    tableop.Restore(gsa_c, 'pp', 1) # tablename, site(if none, default pp, version(if none, the latest)

8.
Remove the backed up data(row). Just passes in the ORM object, which contains
table info etc. Easy~
    tableop.Remove(val)


"""
