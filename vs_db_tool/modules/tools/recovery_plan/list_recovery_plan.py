from vs_db_tool.orm.srm import pdr_planproperties
from vs_db_tool.formatter.layout import PrintResult

from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound

class ListRecoveryPlan(object):
    def __init__(this, a_pp_conn, a_ss_conn, a_formatter=PrintResult()):
        this.pp_conn = a_pp_conn
        this.ss_conn = a_ss_conn
        this.formatter = a_formatter

    def ListSite(this, a_site, a_name):
        session = None
        pdr_planproperties_c = None
        result = None

        if a_site == 'pp':
            session = this.pp_conn.GetSession()
            pdr_planproperties_c = pdr_planproperties.GetTable(this.pp_conn.GetEngine())
        if a_site == 'ss':
            session = this.ss_conn.GetSession()
            pdr_planproperties_c = pdr_planproperties.GetTable(this.ss_conn.GetEngine())

        if a_name is not None:
            try:
                result = session.query(pdr_planproperties_c).filter(
                    pdr_planproperties_c.name.like(a_name)).one()

                this.formatter.PrintNameValue(result.__val_dict__())

            except (MultipleResultsFound, NoResultFound), e:
                print(e)
        else:
            result = session.query(
                pdr_planproperties_c.name,
                pdr_planproperties_c.mo_id,
                pdr_planproperties_c.peerplanmoid).all()

            if result is not None:
                name_list = result[0].keys()
                this.formatter.PrintValue(name_list, result)

    def pp(this, a_name=None):
        this.ListSite("pp", a_name)

    def ss(this, a_name=None):
        this.ListSite("ss", a_name)

    def __call__(this, a_name=None):
        # TODO
        # join both side with peerplanmoid
        return None


