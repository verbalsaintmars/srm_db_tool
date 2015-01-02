wf_name = 'pg'
desc = "Protection Group workflow."
table_list = []

license_tables = [
    "pd_licenseasset",
    "pd_licensereservation"]

temp_tables = [
    "pdp_persistablelock",
    "pdp_persistablemapentry"]

protection_grp_tables = [
    "pdr_protectiongroup",
    "pdr_protectiongrouppeer",
    "pds_protectiongroup",
    "pds_grouprecoverydetails",
    "pds_datastorerecoveryspec",
    "pds_vmfsrecoveryspec",
    "pds_vmfsextentrecoveryspec",
    "pds_groupprotectiondetails"]

protected_vm_tables = [
    "pdr_protectedvm",
    "pdr_vminfo",
    "pdv_filelocation",
    "pdv_directorylocation",
    "pdr_vmprotectionsettings",
    "pdr_protectedvmpeer",
    "pdr_placeholdervm",
    "pdr_vmrecoverysettings"]

device_tables = [
    "pdv_deviceinfo",
    "pdv_devicebackinglocator",
    "pdv_networkdevicebackinglocat",
    "pdv_diskbackinglocator",
    "pdv_datastorelocator",
    "pdv_storageproviderdatastorel"]


file_tables = [
    "pdv_fileinfo",
    "pdv_directorylocator"]

other_tables = [
    "pds_protectedvm",
    "pds_datastore",
    "pds_datastoregroup"]

table_list.extend(license_tables)
table_list.extend(temp_tables)
table_list.extend(protection_grp_tables)
table_list.extend(protected_vm_tables)
table_list.extend(device_tables)
table_list.extend(file_tables)
table_list.extend(other_tables)
