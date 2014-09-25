# TODO Oracle DB
# TODO postgresql DB


class UrlGenerator(object):
    """
    Connnection URL Generator
    """
    __dbtype__ = {1: "mssql", 2: "oracle", 3: "sqlite", 4: "postgresql"}

    def __init__(this, a_CdObject):
        this.cd = a_CdObject
        this.url = None

    def GenUrl(this, a_dbtype, a_dsn):
        this.url = this.__dbtype__[a_dbtype]

        this.url += "" if this.cd.driver is None else "+" + this.cd.driver

        this.url += ("://", ":///")[1 if a_dbtype == 3 else 0]

        if a_dbtype == 3:
            """
            create_engine('sqlite:///:memory:', echo=True)
            """
            this.url += this.cd.PATH
        else:
            this.url += this.cd.UID + ":" + this.cd.PWD + "@"

            this.url += this.cd.DSN if a_dsn else this.cd.HOST + ":" +\
                this.cd.PORT

            this.url += "/" + this.cd.DB if this.cd.DB else ""

            this.url += "?LANGUAGE=" + this.cd.LANG if this.cd.DB and this.cd.LANG else \
                "/?LANGUAGE=" + this.cd.LANG if this.cd.LANG else ""

        return this.url


class CreateDialect(object):
    """
    Typical form of a database URL is:
    dialect+driver://username:password@host:port/database
    This class is in charge of creating dialect base on
    different DB type
    """

    def __init__(this, a_dbtype, a_driver=None):
        """
            UID
            PWD
            DSN
                or
            HOST
            PORT
        """
        this.dbtype = a_dbtype.lower()
        this.driver = a_driver.lower() if a_driver is not None else None
        this.UID = None
        this.PWD = None
        this.HOST = None
        this.PORT = None
        this.DB = None
        this.DSN = None
        this.LANG = None
        this.PATH = None

    def GenMsSqlUrl(this, a_dsn):
        return UrlGenerator(this).GenUrl(1, a_dsn)

    def GenOracleUrl(this, a_dsn=None): pass

    def GenSqliteUrl(this, a_dsn=None):
        return UrlGenerator(this).GenUrl(3, a_dsn)

    def GenPostgresqlUrl(this, a_dsn=None): pass

    def SetUser(this, a_user):
        this.user = a_user

    def GetUser(this):
        return this.user

    def SetPassword(this, a_pwd):
        this.pwd = a_pwd

    def GetPassword(this):
        return this.pwd

    def SetHost(this, a_host):
        this.host = a_host

    def GetHost(this):
        return this.host

    def SetPort(this, a_port):
        this.port = str(a_port)

    def GetPort(this):
        return this.port

    def SetDatabase(this, a_db):
        this.database = a_db

    def GetDatabase(this):
        return this.database

    def SetDsn(this, a_dsn):
        this.dsn = a_dsn

    def GetDsn(this):
        return this.dsn

    def SetLang(this, a_lang):
        this.lang = a_lang

    def GetLang(this):
        return this.lang

    def SetPATH(this, a_path):
        this.path = a_path

    def GetPATH(this):
        return this.path

    UID = property(GetUser, SetUser)
    PWD = property(GetPassword, SetPassword)
    HOST = property(GetHost, SetHost)
    PORT = property(GetPort, SetPort)
    DB = property(GetDatabase, SetDatabase)
    DSN = property(GetDsn, SetDsn)
    LANG = property(GetLang, SetLang)
    PATH = property(GetPATH, SetPATH)

    def GenUrl(this, a_dsn=False):
        """
            2 types:
            1. DSN
            2. Non-DSN
        """

        """
        Testing:

        this.UID = "joe"
        this.PWD = "pwd"
        this.HOST = "vmware.com"
        this.PORT = 123
        this.DB = "SRM"
        this.LANG = "eng"
        """
        return this.GenUrlMap[this.dbtype](this, a_dsn)

    GenUrlMap = \
        {"mssql": GenMsSqlUrl, "oracle": GenOracleUrl,
         "sqlite": GenSqliteUrl, "postgresql": GenPostgresqlUrl}
