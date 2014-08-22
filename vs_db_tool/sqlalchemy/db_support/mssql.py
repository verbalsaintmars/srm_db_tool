"""
TODO: 1. derive from CreateDialect class
"""

from . import create_dialect as cd
from . import base as engine_base


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
            driver default with pyodbc
        """
        super(MsSql, this).__init__(this.db_type, this.driver)

    def __call__(this, a_params):

        engine = engine_base.Engine()
        engine.ECHO = True
        engine.ENCODING = 'utf-8'

        this.UID = a_params.UID
        this.PWD = a_params.PWD
        this.DB = a_params.DB
        this.LANG = a_params.LANG

        if a_params.DSN:
            this.DSN = a_params.DSN
            engine.URL = this.GenUrl(True)
        else:
            this.HOST = a_params.HOST
            this.PORT = "1433" if not a_params.PORT else a_params.PORT
            engine.URL = this.GenUrl(False)

        return engine.GetEngine()



