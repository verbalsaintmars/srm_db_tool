from . import create_dialect as cd
from . import engine as engine_base


class Sqlite(cd.CreateDialect):
    """
    http://docs.sqlalchemy.org/en/rel_0_9/dialects/sqlite.html#module-sqlalchemy.dialects.sqlite.pysqlite
    Default driver is pysqlite
    """
    db_type = "sqlite"
    driver = "pysqlite"

    def __init__(this):
        super(Sqlite, this).__init__(this.db_type, this.driver)

    def __call__(this, a_params):
        engine = engine_base.Engine()
        """
        If ECHO == True , print all sql transaction
        """
        engine.ECHO = False
        engine.ENCODING = 'utf-8'

        """
        Test if passing in parameter is for sqlite connection
        if not, return None
        """
        if a_params.DBTYPE == 3:
            if a_params.PATH:
                this.PATH = a_params.PATH
            else:
                """
                use default in memory sqlite db
                """
                this.PATH = ":memory:"

            engine.URL = this.GenUrl(a_dsn=False)
            return engine.GetEngine()
        else:
            return None
