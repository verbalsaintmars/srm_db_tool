"""
Get information from:

dr_product_info

Version information is used for logics
Different SRM version might have different logics
against each work-flow.

We don't care about schema change between SRM version,
since we are inspecting the DB dynamically.
"""
from srm_db_tool.orm.gentable import GenTable


def GetSrmVersion(a_conn, a_base=None):
    session = a_conn.GetSession()
    engine = a_conn.GetEngine()

    dr_product_info_c = GenTable(
        "dr_product_info",
        a_engine=engine,
        a_base=a_base)

    list_data = [(o.name, o.value) for o in
                 session.query(dr_product_info_c).all()]

    data_version = None
    version = None

    for o in list_data:
        if o[0] == 'data_version':
            data_version = o[1]
        if o[0] == 'version':
            version = o[1]

    return (data_version, version)
