from srm_db_tool.formatter.layout import PrintResult
from srm_db_tool.orm.gentable import GenTable

from srm_db_tool.exception.predefined import SaException

from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound


class ListVm(object):
    def __init__(this, a_conn, a_formatter=PrintResult()):
        """
        Each ListPg object is a connection to single site.
        TODO : a new formatter
        """
        this.conn = a_conn
        this.engine = a_conn.GetEngine()
        this.session = a_conn.GetSession()

        this.formatter = a_formatter

    def _create_table_c(this, a_table_name):
        if not a_table_name:
            return None
        try:
            table_c = GenTable(a_table_name, this.conn.GetEngine())
            return table_c
        except Exception as e:
            print(SaException(
                "SA",
                "Generate Table_C error.",
                __name__,
                e))
            return None

    def PrintResult(this, a_vm_list):
        this.formatter.PrintPgVm(a_vm_list)

    def GetProtectedVms(this, a_pg_name):
        """
        pdr_protectiongroup.name => pdr_protectiongroup.mo_id


        pdr_protectedvm.parentgroupmoid == pdr_protectiongroup.mo_id
        pdr_protectedvm.mo_id
        pdr_protectedvm.vminfo == pdr_vminfo.db_id
        pdr_protectedvm.protectionsettings ==
            [pdr_vmprotectionsettings].[db_id]

        userprotecteddevice = reference to
            [g_do_array].[seq_id],
            reference to
            [pdv_deviceinfo].[db_id]

        providerprotecteddevice = reference to
            [g_do_array].[seq_id],
            reference to
            [pdv_deviceinfo].[db_id]

        fileinfo = reference to [pdv_fileinfo].[db_id]

        unresolveddevicekey = reference to remote site:
            [pdr_vmrecoverysettings].[remotenicinfo]

        peer = reference to [pdr_protectedvmpeer].[db_id]

        operationlockid = reference to [pdp_persistablelock].[db_id]
        """
        if not a_pg_name:
            return None

        protection_grp_info_list = []
        protection_grp_info_list.append(a_pg_name)

        q_result = None

        pdr_protectiongroup_c = this._create_table_c('pdr_protectiongroup')
        try:
            q_result = this.session.query(pdr_protectiongroup_c).\
                filter(pdr_protectiongroup_c.name.like(a_pg_name)).\
                one()
        except MultipleResultsFound as e:
            print(SaException(
                "SA",
                "Query pdr_protectiongroup error.",
                __name__,
                e))
            return None
        except NoResultFound as e:
            print("No protection group : {} found.".format(a_pg_name))
            return None

        pg_mo_id = q_result.mo_id
        pg_peer_id = q_result.peer

        protection_grp_info_list.append(pg_mo_id)

        pdr_protectiongrouppeer_c = this._create_table_c(
            'pdr_protectiongrouppeer')
        try:
            q_result = this.session.query(pdr_protectiongrouppeer_c).\
                filter_by(db_id=pg_peer_id).one()
        except Exception as e:
            print(SaException(
                "SA",
                "Query pdr_protectiongrouppeer error.",
                __name__,
                e))
            print("No protection group peer information for pg : {}".
                  format(a_pg_name))
            return None

        pg_peer_mo_id = q_result.groupmoid
        protection_grp_info_list.append(pg_peer_mo_id)

        pdr_protectedvm_c = this._create_table_c('pdr_protectedvm')
        pdr_vminfo_c = this._create_table_c('pdr_vminfo')
        pdr_protectedvmpeer_c = this._create_table_c('pdr_protectedvmpeer')

        try:
            q_result = this.session.query(
                pdr_vminfo_c,
                pdr_protectedvm_c,
                pdr_protectedvmpeer_c).\
                filter(pdr_protectedvm_c.parentgroupmoid.like(pg_mo_id)).\
                filter(pdr_protectedvm_c.vminfo.like(pdr_vminfo_c.db_id)).\
                filter(pdr_protectedvm_c.peer.like(pdr_protectedvmpeer_c.db_id)).\
                all()
        except Exception as e:
            print(SaException(
                "SA",
                "Query pdr_protectedvm, pdr_vminfo join error.",
                __name__,
                e))
            return None

        vm_list = []

        pdr_protectedvm_vminfo_result = q_result

        for vminfo, pvm, pvm_peer in pdr_protectedvm_vminfo_result:
            single_vm =\
                (vminfo.name,
                 vminfo.vmmoid,
                 pvm.mo_id,
                 pvm_peer.protectedvmmoid)
            vm_list.append((single_vm, tuple(protection_grp_info_list)))

        """
        Format:
        [(vm_gui_name, vm_moid, protected_vm_moid, peer_protected_vm_moid),
         (protection group gui name, pg_moid, peer_pg_moid)]
        """
        return vm_list


def test():
    from srm_db_tool.sqlalchemy.make_conn import MakeConn
    from srm_db_tool.sqlalchemy.db_support.init_params import Init_Params

    params = Init_Params()
    params.UID = 'ad'
    params.PWD = 'ca$hc0w'
    params.DSN = 'fun_pp_01'
    # params.DBTYPE = 'sqlite'
    params.DBTYPE = 'mssql'
    # params.PATH = r'c:\pp.db'

    conn = MakeConn(params)
    lm = ListVm(conn)
    result = lm.GetProtectedVms(r'HQ-DATA12-ProtectionGroup')
    lm.PrintResult(result)
    return result
