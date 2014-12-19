from srm_db_tool.sqlalchemy.make_conn import MakeConn


def MakeConns(a_param_pp, a_param_ss):
    pp_conn = None
    ss_conn = None
    if a_param_pp is not None:
        pp_conn = MakeConn(a_param_pp)
    if a_param_ss is not None:
        ss_conn = MakeConn(a_param_ss)
    return (pp_conn, ss_conn)


def CheckConns(a_conn):
    if a_conn is None:
        return False
    else:
        return True
