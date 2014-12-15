from srm_db_tool.exception.predefined import GeneralException


class TableOp(object):
    """
    Each TableOb instance uses single sqlite db file.
    """

    def __enter__(this):
        return this

    def __exit__(this, exc_type, exc_value, exc_tb):
        if exc_type is None:
            # print('exited normally\n')
            this.Dispose()
        else:
            # print('raise an exception!', exc_type)
            this.Dispose()
            return False

    def __init__(this, a_dbop):
        """
        a_dbop:
            which kind of database to manipulate.
            Follow the sqlitedbop interface.
        """

        """
        the local sqlite db interface has estabilished.
        """
        this.dbOp = a_dbop

    def Backup(
        this,
        a_value_list,
        a_version,
        a_site,
        a_dumpType,
        a_pairdb=None,
        a_prNum=None,
        a_kburl=None,
            a_desc=None, a_force=False):

        """
        a_value_list : list of orm objects, which have table information
        a_site : pp for primary , ss for secondary, or other value
        """
        if not a_force:
            if this.dbOp.LOCK and this.dbOp.LOCK != 0:
                print("db dump : {} has backed up data.\n"
                      "Please choose a new db for backup.\n"
                      .format(this.dbOp.DBFILEPATH))
                return

        try:
            if type(a_value_list) is not list:
                raise GeneralException(
                    "I0", "Backup accept only list of ORM objects", __name__)
        except GeneralException as e:
            print(e)
            return

        this.dbOp.VERSION = a_version
        this.dbOp.SITE = a_site
        this.dbOp.DUMPTYPE = a_dumpType
        this.dbOp.PAIRDB = a_pairdb
        this.dbOp.PRNUM = a_prNum
        this.dbOp.KBURL = a_kburl
        this.dbOp.DESC = a_desc

        try:
            this.dbOp.Backup(a_value_list)
        except:
            print("to be implemented...")
        else:
            this.dbOp.LOCK = 1

    def ListTables(this):
        """
        List this TableOp instance's sqlite db file's tables
        """
        return this.dbOp.ListTables()

    def GetMetaData(this):
        return \
            {"version": this.dbOp.VERSION,
             "site": this.dbOP.SITE,
             "lock": this.dbOp.LOCK,
             "pairDB": this.dbOp.PAIRDB,
             "dumptype": this.dbOp.DUMPTYPE,
             "prnum": this.dbOp.PRNUM,
             "kburl": this.dbOp.KBURL,
             "desc": this.dbOp.DESC}

    def GetFixByModule(this):
        return this.dbOp.MODULE

    def Restore(this, a_table_name):
        """
        a_table_name:
            the table that we want to restore from.
        """
        return this.dbOp.Restore(a_table_name)

    def Remove(this, a_table_name):
        """
        Remove data from table.
        This is not dropping the table.
        """
        this.dbOp.LOCK = 0
        num_rows = this.dbOp.Remove(a_table_name)
        this.dbOp.LOCK = 1

        return num_rows

    def Dispose(this):
        """
        TODO:
            Make use for Context Managers
        """
        this.dbOp.Dispose()
