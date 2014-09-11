from . import create_dialect as cd
from . import engine as engine_base


class Sqlite(cd.CreateDialect):
    """
    http://docs.sqlalchemy.org/en/rel_0_9/dialects/sqlite.html#module-sqlalchemy.dialects.sqlite.pysqlite
    """
    db_type = "sqlite"
    driver = "pysqlite"

    def __init__(this):
        """
        driver default as pysqlite
        """
        super(Sqlite, this).__init__(this.db_type, this.driver)

    def __call__(this, a_params):
        engine = engine_base.Engine()
        engine.ECHO = False
        engine.ENCODING = 'utf-8'

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
