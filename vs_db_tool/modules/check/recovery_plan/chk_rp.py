from vs_db_tool.orm.srm import pdr_planproperties
from vs_db_tool.orm.srm import pdr_plancontents
from vs_db_tool.orm.srm import pdr_protectiongroupmap


class CheckRP(object):
    def __init__(this, a_cc):
        this.cc = a_cc

    def HasRP(this, a_rp_name):
        pp_t = pdr_planproperties.GetTable(this.cc.GetEngine())
        result = this.cc.GetSession().query(pp_t).filter(pp_t.name.like(a_rp_name)).first()
        return result
