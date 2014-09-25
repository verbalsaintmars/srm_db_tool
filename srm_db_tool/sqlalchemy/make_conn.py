from .db_support import create_session
from .db_support import mssql
from .db_support import oracle
from .db_support import sqlite
from .db_support import postgresql


class MakeConn(object):
    """
    Each MakeConn instance will cache the created engine object,
    as well as session object.
    """
    def __init__(this, a_param):
        """
        a_param is the type of Init_Params
        """
        this.param = a_param
        this.engine = None
        this.session = None

    def Dispose(this):
        this.session.close()
        this.engine.dispose()
        this.session = None
        this.engine = None

    def GetEngine(this):

        eng_map = {1: mssql.MsSql,
                   2: oracle.Oracle,
                   3: sqlite.Sqlite,
                   4: postgresql.Postgresql}

        if not this.engine:
            this.engine = eng_map[this.param.DBTYPE]()(this.param)

        return this.engine

    def GetSession(this):
        if not this.session:
            if this.engine:
                this.session = create_session.Session(
                    this.engine)()

                return this.session
            else:
                this.session = create_session.Session(
                    this.GetEngine())()
                return this.session
        else:
            return this.session
