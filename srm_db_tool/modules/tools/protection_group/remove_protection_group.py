from srm_db_tool.orm.gentable import GenTable
from srm_db_tool.modules.tools.version_check.version_check import GetSrmVersion
from srm_db_tool.formatter.layout import PrintResult
from srm_db_tool.exception.predefined import MODULE_EXCEPT_FORMAT
from srm_db_tool.backup_tables_mgr.dumptype import DumpType
from srm_db_tool.backup_tables_mgr.module import Module
from srm_db_tool.backup_tables_mgr.generaldbop import GeneralDbOp

from sqlalchemy.orm.exc import NoResultFound


class RemoveProtectionGroup(object):

    def __init__(
        this,
        a_conn,
        a_tableop,
        a_pr=None,
        a_kb=None,
        a_desc=None,
            a_formatter=PrintResult()):

        this.conn = a_conn
        this.formatter = a_formatter
        this.tableop = a_tableop
        this.pr = a_pr
        this.kb = a_kb
        this.desc = a_desc

    def Backup(this, a_result_list, a_site="pp", a_version=None):
        dumptype = DumpType.CUSTOMIZED
        dumptype.TYPE = 'rmpg'

        this.tableop.Backup(
            a_result_list,
            a_version,
            "primary" if a_site == 'pp' else "secondary",
            dumptype,
            None,
            this.pr,
            this.kb,
            this.desc,
            True)

    def Remove(this, a_datum):
        session = this.conn.GetSession()
        session.delete(a_datum)
        session.commit()

    def GetSession(this):
        session = this.conn.GetSession()
        return session

    def GetTable(this, a_table_name):
        return GenTable(a_table_name, this.conn.GetEngine())

    def FilterOneTable(this, a_table, a_session, criteria):
        try:
            result = a_session.query(a_table).filter(
                criteria).all()
            return result

        except NoResultFound:
            return None

    def ExtractFromMultiTable(this, a_res, a_res_list):
        '''For multiple talbes query, get the first table'''
        local_ = []

        for a in a_res:
            local_.append(a[0])

        if len(local_) > 0:
            a_res_list.append(local_)

    def Update_pds_datastore(this, a_pg_moid, a_session):
        pds_ds_c = this.GetTable("pds_datastore")

        ds_list = a_session.query(pds_ds_c).filter(
            pds_ds_c.protectiongroupmoid.like(a_pg_moid)).all()

        for ds in ds_list:
            ds.protectiongroupmoid = ''
            ds.protectiongroupmoidhasvalue = ''

    def ListTables(this, a_pg_name, a_session):
        try:
            pg_c = this.GetTable("pdr_protectiongroup")
            pvm_c = this.GetTable("pdr_protectedvm")
            vminfo_c = this.GetTable("pdr_vminfo")
            dev_info_c = this.GetTable("pdv_deviceinfo")
            g_do_array_c = this.GetTable("g_do_array")
            file_loc_c = this.GetTable("pdv_filelocation")

            result = []

            res = this.FilterOneTable(
                pg_c,
                a_session,
                pg_c.name.like(a_pg_name))

            if res is None or len(res) < 1:
                print("\nCan't find Protection Group \'{}\'"
                      .format(a_pg_name))
                return None

            pg_moid = res[0].mo_id

            # -- update pds_datastore
            this.Update_pds_datastore(pg_moid, a_session)

            # -- delete from pdr_protectiongroupfailoverin, mo_id == @PG_MOID
            pg_failover_c = this.GetTable("pdr_protectiongroupfailoverin")

            res = this.FilterOneTable(
                pg_failover_c,
                a_session,
                pg_failover_c.mo_id.like(pg_moid))

            if len(res) > 0:
                result.append(res)

            # -- delete from pdr_objinfo mo_id == @PG_MOID
            obj_info_c = this.GetTable("pdr_objinfo")

            res = this.FilterOneTable(
                obj_info_c,
                a_session,
                obj_info_c.mo_id.like(pg_moid))

            if len(res) > 0:
                result.append(res)

            # -- delete from pdr_opupdate  objid == @PG_MOID
            op_update_c = this.GetTable("pdr_opupdate")

            res = this.FilterOneTable(
                op_update_c,
                a_session,
                op_update_c.objid.like(pg_moid))

            if len(res) > 0:
                result.append(res)

            # -- delete from pdp_persistablemapentry for pg
            persist_map_c = this.GetTable("pdp_persistablemapentry")

            res = this.FilterOneTable(
                persist_map_c,
                a_session,
                persist_map_c.mapdata.contains('<moid>' + pg_moid + '</moid>'))

            if len(res) > 0:
                result.append(res)

            # -- delete from pdp_persistablemapentry for pvm
            res = a_session.query(persist_map_c, pvm_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter(persist_map_c.mapdata.contains(
                    '<moid>' + pvm_c.mo_id + '</moid>')).all()

            this.ExtractFromMultiTable(res, result)

            # -- delete from pd_licensereservation,
            # protectedvmmoid == pdr_protectedvm.mo_id
            plicensereserv_c = this.GetTable("pd_licensereservation")

            res = a_session.query(plicensereserv_c, pvm_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter(plicensereserv_c.protectedvmmoid.like(pvm_c.mo_id)).\
                all()

            this.ExtractFromMultiTable(res, result)

            # -- delete from pdv_directorylocation
            dir_loc_c = this.GetTable("pdv_directorylocation")
            res = a_session.query(dir_loc_c, file_loc_c, pvm_c, vminfo_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter(vminfo_c.db_id.like(pvm_c.vminfo)).\
                filter(vminfo_c.configfilelocation.like(file_loc_c.db_id)).\
                filter(dir_loc_c.db_id.like(file_loc_c.directory) |
                       dir_loc_c.db_id.like(vminfo_c.snapshotdirectory) |
                       dir_loc_c.db_id.like(vminfo_c.suspenddirectory) |
                       dir_loc_c.db_id.like(vminfo_c.logdirectory)).all()

            this.ExtractFromMultiTable(res, result)

            # for pdv_filelocation
            res = a_session.query(file_loc_c, pvm_c, vminfo_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter(vminfo_c.db_id == pvm_c.vminfo).\
                filter(vminfo_c.configfilelocation == file_loc_c.db_id).all()

            this.ExtractFromMultiTable(res, result)

            # -- delete from g_string_array for replicabledevice
            str_arr_c = this.GetTable("g_string_array")

            res = a_session.query(str_arr_c, pvm_c, vminfo_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter(vminfo_c.db_id == pvm_c.vminfo).\
                filter(vminfo_c.replicabledevice.like(str_arr_c.seq_id)).all()

            '''this.ExtractFromMultiTable(res, result)'''
            # -- delete from pdr_vminfo, db_id == pdr_protectedvm.vminfo
            res = a_session.query(vminfo_c, pvm_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter(vminfo_c.db_id == pvm_c.vminfo).all()

            this.ExtractFromMultiTable(res, result)

            # -- delete from pdr_vmprotectionsettings,
            # db_id == pdr_protectedvm.protectionsettings
            vm_set_c = this.GetTable("pdr_vmprotectionsettings")
            res = a_session.query(vm_set_c, pvm_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter(vm_set_c.db_id == pvm_c.protectionsettings).all()

            this.ExtractFromMultiTable(res, result)

            # -- delete from pdr_objinfo,
            #  db_id == pdr_protectedvm.excludeddevicekey
            obj_c = this.GetTable("pdr_objinfo")
            res = a_session.query(obj_c, pvm_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter(vm_set_c.db_id == pvm_c.excludeddevicekey).all()

            this.ExtractFromMultiTable(res, result)

            # -- delete from pdv_devicebackinglocator,
            # db_id == pdv_deviceinfo.backing
            dev_loc_c = this.GetTable("pdv_devicebackinglocator")

            res = a_session.query(dev_loc_c, dev_info_c, g_do_array_c, pvm_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter(((g_do_array_c.seq_id == pvm_c.userprotecteddevice) &
                       (g_do_array_c.db_id == dev_info_c.db_id)) |
                       ((g_do_array_c.seq_id ==
                         pvm_c.providerprotecteddevice) &
                       (g_do_array_c.db_id == dev_info_c.db_id))).\
                filter(dev_loc_c.db_id == dev_info_c.backing).all()

            this.ExtractFromMultiTable(res, result)

            # -- delete from pdv_networkdevicebackinglocat,
            #  db_id == pdv_deviceinfo.backing
            net_loc_c = this.GetTable("pdv_networkdevicebackinglocat")
            res = a_session.query(net_loc_c, dev_info_c, g_do_array_c, pvm_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter(((g_do_array_c.seq_id == pvm_c.userprotecteddevice) &
                       (g_do_array_c.db_id == dev_info_c.db_id)) |
                       ((g_do_array_c.seq_id ==
                         pvm_c.providerprotecteddevice) &
                       (g_do_array_c.db_id == dev_info_c.db_id))).\
                filter(net_loc_c.db_id == dev_info_c.backing).all()

            this.ExtractFromMultiTable(res, result)

            # -- delete from pdv_diskbackinglocator,
            # db_id == pdv_deviceinfo.backing
            disk_loc_c = this.GetTable("pdv_diskbackinglocator")
            res = a_session.query(disk_loc_c, dev_info_c, g_do_array_c, pvm_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter(((g_do_array_c.seq_id == pvm_c.userprotecteddevice) &
                       (g_do_array_c.db_id == dev_info_c.db_id)) |
                       ((g_do_array_c.seq_id ==
                         pvm_c.providerprotecteddevice) &
                       (g_do_array_c.db_id == dev_info_c.db_id))).\
                filter(disk_loc_c.db_id == dev_info_c.backing).all()
            this.ExtractFromMultiTable(res, result)

            # -- delete from pdv_storageproviderdatastorel,
            # db_id == pdv_datastorelocator.db_id
            spds_c = this.GetTable("pdv_storageproviderdatastorel")
            file_info_c = this.GetTable("pdv_fileinfo")
            dir_locator_c = this.GetTable("pdv_directorylocator")
            ds_loc_c = this.GetTable("pdv_datastorelocator")
            res = a_session.query(
                spds_c, file_info_c, dir_locator_c, ds_loc_c, pvm_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter((pvm_c.fileinfo == file_info_c.db_id) &
                       (file_info_c.vmconfigdirectory == dir_locator_c.db_id) &
                       (dir_locator_c.datastore == ds_loc_c.db_id) &
                       (ds_loc_c.db_id == spds_c.db_id)).all()
            this.ExtractFromMultiTable(res, result)

            # -- delete from pdv_datastorelocator,
            # db_id == pdv_directorylocator.datastore
            ds_loc_c = this.GetTable("pdv_datastorelocator")
            file_info_c = this.GetTable("pdv_fileinfo")
            res = a_session.query(
                ds_loc_c, dir_locator_c, file_info_c, pvm_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter((file_info_c.db_id == pvm_c.fileinfo) &
                       (file_info_c.vmconfigdirectory == dir_locator_c.db_id) &
                       (dir_locator_c.datastore == ds_loc_c.db_id)).all()
            this.ExtractFromMultiTable(res, result)

            # -- delete from pdv_deviceinfo,
            # db_id == g_do_array.db_id, g_do_array.seq_id ==
            # (pdr_protectedvm..userprotecteddevice or
            # pdr_protectedvm.providerprotecteddevice)
            res = a_session.query(dev_info_c, g_do_array_c, pvm_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter(((g_do_array_c.seq_id == pvm_c.userprotecteddevice) &
                       (g_do_array_c.db_id == dev_info_c.db_id)) |
                       ((g_do_array_c.seq_id ==
                        pvm_c.providerprotecteddevice) &
                        (g_do_array_c.db_id == dev_info_c.db_id))).all()
            this.ExtractFromMultiTable(res, result)

            # -- delete from g_do_array
            res = a_session.query(g_do_array_c, pvm_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter(((g_do_array_c.seq_id == pvm_c.userprotecteddevice) |
                       (g_do_array_c.seq_id ==
                        pvm_c.providerprotecteddevice))).all()
            this.ExtractFromMultiTable(res, result)

            # -- delete from pdv_directorylocator
            # db_id == pdv_fileinfo.vmconfigdirectory
            res = a_session.query(dir_locator_c, file_info_c, pvm_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter(((file_info_c.db_id == pvm_c.fileinfo) &
                       (file_info_c.vmconfigdirectory ==
                        dir_locator_c.db_id))).all()
            this.ExtractFromMultiTable(res, result)

            # -- delete from pdv_fileinfo
            res = a_session.query(file_info_c, pvm_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter(file_info_c.db_id == pvm_c.fileinfo).all()
            this.ExtractFromMultiTable(res, result)

            # -- delete from pdr_protectedvmpeer,
            # db_id == pdr_protectedvm.peer
            pvm_peer_c = this.GetTable("pdr_protectedvmpeer")
            res = a_session.query(
                pvm_peer_c, dir_locator_c, file_info_c, pvm_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter(pvm_peer_c.db_id == pvm_c.peer).all()
            this.ExtractFromMultiTable(res, result)

            # -- delete from pdp_persistablelock,
            # db_id == pdr_protectedvm.operationlockid
            plock_c = this.GetTable("pdp_persistablelock")
            res = a_session.query(plock_c, pvm_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter(plock_c.db_id == pvm_c.operationlockid).all()
            this.ExtractFromMultiTable(res, result)

            # -- delete from pdr_placeholdervm,
            # mo_id == pdr_protectedvm.mo_id
            holder_vm_c = this.GetTable("pdr_placeholdervm")
            res = a_session.query(holder_vm_c, pvm_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter(holder_vm_c.mo_id == pvm_c.mo_id).all()
            this.ExtractFromMultiTable(res, result)

            # -- delete from pdr_vmrecoverysettings,
            # protectedvmmoidint == right number part of pdr_protectedvm.mo_id
            # -- we need to get the number from the right part of pvm's mo_id.
            # e.g. get '4236' out of pvm_c = 'protected-vm-4236'
            rec_setting_c = this.GetTable("pdr_vmrecoverysettings")
            res = a_session.query(rec_setting_c, pvm_c).\
                filter(pvm_c.parentgroupmoid.like(pg_moid)).\
                filter(('protected-vm-' +
                        str(rec_setting_c.protectedvmmoidint)) ==
                       pvm_c.mo_id).all()
            this.ExtractFromMultiTable(res, result)

            #   where pvm.parentgroupmoid LIKE
            #   @PG_MOID and RIGHT(pvm.mo_id,LEN(pvm.mo_id) -13)
            #   LIKE rc.protectedvmmoidint

            # -- delete from pdr_protectedvm, parentgroupmoid == @PG_MOID
            res = this.FilterOneTable(
                pvm_c,
                a_session,
                pvm_c.parentgroupmoid.like(pg_moid))

            if len(res) > 0:
                result.append(res)

            # -- pdr_protectiongroup related ---
            # -- delete from pdr_protectiongrouppeer,
            # db_id == pdr_protectiongroup.peer
            pg_peer_c = this.GetTable("pdr_protectiongrouppeer")
            res = a_session.query(pg_peer_c, pg_c).\
                filter(pg_c.name.like(a_pg_name)).\
                filter(pg_c.peer.like(pg_peer_c.db_id)).all()
            this.ExtractFromMultiTable(res, result)

            # -- delete from pds_groupprotectiondetails,
            # groupmoid == @PG_MOID
            gp_detail_c = this.GetTable("pds_groupprotectiondetails")
            res = this.FilterOneTable(
                gp_detail_c,
                a_session,
                gp_detail_c.groupmoid.like(pg_moid))

            if len(res) > 0:
                result.append(res)

            # -- delete from pds_protectiongroup,
            # groupmoid == @PG_MOID
            pds_pg_c = this.GetTable("pds_protectiongroup")
            res = this.FilterOneTable(
                pds_pg_c,
                a_session,
                pds_pg_c.groupmoid.like(pg_moid))
            if len(res) > 0:
                result.append(res)

            # -- delete from pds_protectedvm,
            # groupmoid == @PG_MOID
            pds_pvm_c = this.GetTable("pds_protectedvm")
            res = this.FilterOneTable(
                pds_pvm_c,
                a_session,
                pds_pvm_c.groupmoid.like(pg_moid))

            if len(res) > 0:
                result.append(res)

            # -- delete from pds_nfsrecoveryspec,
            # db_id == pds_datastorerecoveryspec.db_id
            gr_detail_c = this.GetTable("pds_grouprecoverydetails")
            ds_rec_spec_c = this.GetTable("pds_datastorerecoveryspec")
            # nfs spec not used if CU does not have nfs device used in srm
            nfs_spec_c = this.GetTable("pds_nfsrecoveryspec")

            if nfs_spec_c is None:
                res = a_session.query(
                    ds_rec_spec_c,
                    gr_detail_c,
                    g_do_array_c).\
                    filter(gr_detail_c.groupmoid.like(pg_moid)).\
                    filter(gr_detail_c.datastores.like(g_do_array_c.seq_id) &
                           (g_do_array_c.db_id == ds_rec_spec_c.db_id)).all()
            else:
                res = a_session.query(
                    nfs_spec_c,
                    ds_rec_spec_c,
                    gr_detail_c,
                    g_do_array_c).\
                    filter(gr_detail_c.groupmoid.like(pg_moid)).\
                    filter(gr_detail_c.datastores.like(g_do_array_c.seq_id) &
                           (g_do_array_c.db_id == ds_rec_spec_c.db_id) &
                           (nfs_spec_c.db_id == ds_rec_spec_c.db_id)).all()

            this.ExtractFromMultiTable(res, result)

            # -- delete from pds_datastorerecoveryspec,
            # db_id == g_do_array.db_id,
            # g_do_array.seq_id == pds_grouprecoverydetails.datastores
            res = a_session.query(
                ds_rec_spec_c,
                gr_detail_c,
                g_do_array_c).\
                filter(gr_detail_c.groupmoid.like(pg_moid)).\
                filter(gr_detail_c.datastores.like(g_do_array_c.seq_id) &
                       (g_do_array_c.db_id == ds_rec_spec_c.db_id)).all()
            this.ExtractFromMultiTable(res, result)

            # -- delete from g_do_array
            res = a_session.query(g_do_array_c, gr_detail_c).\
                filter(gr_detail_c.groupmoid.like(pg_moid)).\
                filter(gr_detail_c.datastores.like(g_do_array_c.seq_id)).all()
            this.ExtractFromMultiTable(res, result)

            # ?? -- delete from pds_vmfsextentrecoveryspec,
            # db_id == pds_vmfsrecoveryspec.extents
            vmfs_ext_spec_c = this.GetTable("pds_vmfsextentrecoveryspec")
            vmfs_spec_c = this.GetTable("pds_vmfsrecoveryspec")

            res = a_session.query(
                vmfs_ext_spec_c,
                vmfs_spec_c,
                gr_detail_c).\
                filter(gr_detail_c.groupmoid.like(pg_moid)).\
                filter(vmfs_spec_c.extents.like(vmfs_ext_spec_c.db_id)).all()
            this.ExtractFromMultiTable(res, result)

            # -- delete from pds_vmfsrecoveryspec,
            # db_id == pds_grouprecoverydetails.datastores,
            res = a_session.query(vmfs_spec_c, gr_detail_c).\
                filter(gr_detail_c.groupmoid.like(pg_moid)).\
                filter(gr_detail_c.datastores.like(vmfs_spec_c.db_id)).all()
            this.ExtractFromMultiTable(res, result)

            # -- delete from pds_grouprecoverydetails,
            # groupmoid == @PG_MOID
            res = this.FilterOneTable(
                gr_detail_c,
                a_session,
                gr_detail_c.groupmoid.like(pg_moid))

            if len(res) > 0:
                result.append(res)

            # -- delete from g_string_array,
            # string_val == @PG_MOID
            # res =
            #   this.FilterOneTable(
            #       str_arr_c, a_session, str_arr_c.string_val.like(pg_moid))
            # if len(res) > 0:
            #   result.append(res)

            # -- delete from pdr_protectiongroup
            res = this.FilterOneTable(
                pg_c,
                a_session,
                pg_c.name.like(a_pg_name))

            if len(res) > 0:
                result.append(res)

            if(len(result) > 0):
                return result
            else:
                return None

        except NoResultFound:
            return None

    def __call__(this, a_pg_name=None, a_site="pp"):
        if a_pg_name is None:
            print("Please enter the Protection Group "
                  "name we want to remove...")
            return
        """
        Check for while the database about to manipulate with
        has the proper tables for protection groups
        """
        sqlop = GeneralDbOp(a_conn=this.conn, a_create_meta_table=False)

        if sqlop.DUMPTYPE is not None and\
           sqlop.DUMPTYPE != DumpType.ALL and\
           sqlop.DUMPTYPE.TYPE != 'pg':
            print("Dumped database does not contain Protection Group tables.")
            return

        version = GetSrmVersion(this.conn, a_site)[1]
        session = this.GetSession()

        l_remove_list = this.ListTables(a_pg_name, session)

        if l_remove_list is None or len(l_remove_list) < 1:
            return

        # backup
        try:
            backup_data = []

            print "\n--------------------------------------------------------"
            print "below tables will be modified:"
            print "---------------------------------------------------------"
            for records in l_remove_list:
                print '{:<30} \t{} rows'.format(
                    records[0].__table__.name, len(records))

                for rec in records:
                    backup_data.append(rec)
            print("11")
            this.Backup(backup_data, a_site, version)
            print("22")

            # -- update pds_datastore, query for backuping first
            pg_c = this.GetTable("pdr_protectiongroup")
            pg_rec = this.FilterOneTable(
                pg_c,
                session,
                pg_c.name.like(a_pg_name))

            pg_moid = pg_rec[0].mo_id

            pds_ds_c = this.GetTable("pds_datastore")
            res = this.FilterOneTable(
                pds_ds_c,
                session,
                pds_ds_c.protectiongroupmoid.like(pg_moid))

            if len(res) > 0:
                print('{:<30} \t{} rows'.
                      format(res[0].__table__.name, len(res)))

                # this.Backup(res, a_site, version)
        except Exception as e:
            print(MODULE_EXCEPT_FORMAT.format(__name__, e))

        else:
            print "\n--------------------------------------------------------"
            print "removing records..."
            print "--------------------------------------------------------"
            for records in l_remove_list:
                print 'removing %s' % records[0].__table__.name
                for rec in records:
                    # print str(rec)
                    this.Remove(rec, a_site)

            """
            Insert into srm_meta_table_fixby table if possible
            i.e , the database we are about to manipulate with
            has the fixby meta tables.
            """
            gdbop = GeneralDbOp(this.conn)

            if gdbop.LOCK:
                gdbop.LOCK = 0

            if gdbop.MODULE is not None:
                """
                Create a Module type instance to describe and insert into
                    srm_meta_table_fixby table
                """
                module = Module()
                module.NAME = "rmpg"
                module.DESC = "remove protection group"
                gdbop.MODULE = module

            if gdbop.LOCK == 0:
                gdbop.LOCK = 1
