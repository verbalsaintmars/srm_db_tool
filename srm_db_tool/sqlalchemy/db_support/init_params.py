class Init_Params(object):
    __dbtype__ = {"mssql": 1, "oracle": 2, "sqlite": 3, "postgresql": 4}

    def GetDBType(this):
        try:
            return this.dbtype
        except:
            return None

    def SetDBType(this, a_type):
        this.dbtype = this.__dbtype__[a_type]

    def GetUID(this):
        try:
            return this.uid
        except:
            return None

    def SetUID(this, a_val):
        this.uid = a_val

    def GetPWD(this):
        try:
            return this.pwd
        except:
            return None

    def SetPWD(this, a_val):
        this.pwd = a_val

    def GetHost(this):
        try:
            return this.host
        except:
            return None

    def SetHost(this, a_val):
        this.host = a_val

    def GetPort(this):
        try:
            return this.port
        except:
            return None

    def SetPort(this, a_val):
        this.port = a_val

    def GetDB(this):
        try:
            return this.db
        except:
            return None

    def SetDB(this, a_val):
        this.db = a_val

    def GetDSN(this):
        try:
            return this.dsn
        except:
            return None

    def SetDSN(this, a_val):
        this.dsn = a_val

    def GetLANG(this):
        try:
            return this.dsn
        except:
            return None

    def SetLANG(this, a_val):
        this.lang = a_val

    def GetPATH(this):
        try:
            return this.path if this.dbtype == 3 else None
        except:
            return None

    def SetPATH(this, a_val):
        """
        sqlite path. start with '/' will use absolute path
        """
        this.path = a_val

    UID = property(GetUID, SetUID)
    PWD = property(GetPWD, SetPWD)
    HOST = property(GetHost, SetHost)
    PORT = property(GetPort, SetPort)
    DB = property(GetDB, SetDB)
    DSN = property(GetDSN, SetDSN)
    LANG = property(GetLANG, SetLANG)
    DBTYPE = property(GetDBType, SetDBType)
    PATH = property(GetPATH, SetPATH)
