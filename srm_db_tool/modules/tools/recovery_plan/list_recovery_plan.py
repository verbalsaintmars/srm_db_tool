from srm_db_tool.formatter.layout import PrintResult

from srm_db_tool.exception.predefined import GeneralException

from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound

from srm_db_tool.orm.gentable import GenTable


class ListRecoveryPlan(object):
    def __init__(this, a_pp_conn, a_ss_conn, a_formatter=PrintResult()):
        this.pp_conn = a_pp_conn
        this.ss_conn = a_ss_conn
        this.formatter = a_formatter

    def ListSite(this, a_site, a_name=None):
        session = None
        pdr_planproperties_c = None
        result = None

        if a_site == 'pp':
            session = this.pp_conn.GetSession()
            pdr_planproperties_c = GenTable(
                "pdr_planproperties",
                this.pp_conn.GetEngine())

        if a_site == 'ss':
            session = this.ss_conn.GetSession()
            pdr_planproperties_c = GenTable(
                "pdr_planproperties",
                this.ss_conn.GetEngine())

        if a_name is not None:
            try:
                result = session.query(pdr_planproperties_c).filter(
                    pdr_planproperties_c.name.like(a_name)).one()

                return result

            except (MultipleResultsFound, NoResultFound) as e:
                print(
                    GeneralException(
                        "SA",
                        "session query failed with not having exact 1 result",
                        __name__,
                        e))
                return None
        else:
            result = session.query(
                pdr_planproperties_c.name,
                pdr_planproperties_c.mo_id,
                pdr_planproperties_c.peerplanmoid).all()
            return result

    def PrintResult(this, a_result, a_name):
        if a_name is not None and a_result is not None:
            print("\n\n")
            print("{:>25}: {:<25}".format("Recovery plan", a_name))
            this.formatter.PrintNameValue(a_result.__val_dict__())
        elif a_result is not None:
            print("\n\n")
            name_list = a_result[0].keys()
            this.formatter.PrintValue(name_list, a_result)
        return a_result

    def site(this, a_name=None, a_site='pp'):
        if a_site == 'pp':
            return this.PrintResult(this.ListSite("pp", a_name), a_name)
        else:
            return this.PrintResult(this.ListSite("ss", a_name), a_name)

    def __call__(this, a_name=None):
        pp_result = this.ListSite('pp', a_name)
        ss_result = this.ListSite('ss', a_name)

        if a_name is not None:
            result = (True if pp_result is not None else False) &\
                (True if ss_result is not None else False)

            if result:

                if pp_result.peerplanmoid == ss_result.mo_id:
                    print("--Protected Site--")
                    this.PrintResult(pp_result, a_name)
                    print("\n--Recovery Site--")
                    this.PrintResult(ss_result, a_name)

                else:
                    print("moid doesn't match :\
                          {} in Protected Site's peerplanmoid".format(
                        pp_result.peerplanmoid))
            else:
                if pp_result is None:
                    print(
                        "Can not find {} recovery plan on Protected Site ".
                        format(a_name))

                if ss_result is None:
                    print(
                        "Can not find {} recovery plan on Recovery Site ".
                        format(a_name))
        else:
            p_set = {p_res.peerplanmoid for p_res in pp_result}
            s_set = {s_res.mo_id for s_res in ss_result}
            p_set &= s_set

            result =\
                [p_res for p_res in pp_result if p_res.peerplanmoid in p_set]

            this.PrintResult(result, a_name)
