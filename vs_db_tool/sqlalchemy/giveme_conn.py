from .db_support import *

class CreateConn(object):
    def __init__(this, a_param):
        this.param = a_param
        this.engine = None
        this.session = None

    def GetEngine(this):
        if not this.engine:
            this.engine = {1 : mssql.MsSql, 2 : oracle.Oracle, 3 : sqlite.Sqlite,
                4 : postgresql.Postgresql}[this.param.DBTYPE]()
        return this.engine(this.param)

    def GetSession(this):
        if not this.session:
            if this.engine:
                this.session = create_session.Session(this.engine(this.param))
                return this.session()
            else:
                return None
        else:
            return this.session()

