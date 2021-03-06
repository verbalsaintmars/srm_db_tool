from . import create_dialect as cd
from . import engine as engine_base


class MsSql(cd.CreateDialect):
    """
        Usage:
        msobj = MsSql()
        msobj.DSN or msobj.HOST msobj.PORT
        msobj.UID
        msobj.PWD
        msobj.LANG
        msobj(Init_Params())
        consume engine_base.Engine instance
    """
    db_type = "mssql"
    driver = "pyodbc"

    def __init__(this):
        """
            driver default as pyodbc
        """
        super(MsSql, this).__init__(this.db_type, this.driver)

    def __call__(this, a_params):
        engine = engine_base.Engine()
        engine.ECHO = False
        engine.ENCODING = 'utf-8'

        if a_params.DBTYPE == 1:
            this.UID = a_params.UID
            this.PWD = a_params.PWD
            this.DB = a_params.DB
            this.LANG = a_params.LANG

            if a_params.DSN:
                this.DSN = a_params.DSN
                engine.URL = this.GenUrl(a_dsn=True)
            else:
                this.HOST = a_params.HOST
                this.PORT = "1433" if not a_params.PORT else a_params.PORT
                engine.URL = this.GenUrl(a_dsn=False)

            return engine.GetEngine()

        else:
            return None
