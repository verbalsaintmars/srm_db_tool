from srm_db_tool.sqlalchemy.make_conn import MakeConn


def MakeConns(a_param_pp, a_param_ss):
    pp_conn = None
    ss_conn = None
    if a_param_pp is not None:
        pp_conn = MakeConn(a_param_pp)
    if a_param_ss is not None:
        ss_conn = MakeConn(a_param_ss)
    return (pp_conn, ss_conn)


def CheckConns(a_pp_conn, a_ss_conn, a_msg_pp, a_msg_ss):
    import sys
    if a_pp_conn is None:
        print(a_msg_pp)
        sys.exit()
    if a_ss_conn is None:
        print(a_msg_ss)
        sys.exit()
