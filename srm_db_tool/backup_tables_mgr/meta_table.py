from sqlalchemy import Column, Integer, String


class Table_Param(object):
    """
    struct for Table parameters
    """
    def SetTableName(this, a_name):
        this.name = a_name

    def GetTableName(this):
        return this.name

    def SetTableColumns(this, a_cols):
        """
        a_cols tuple, contains column objects
        """
        this.cols = a_cols

    def GetTableColumns(this):
        return this.cols

    NAME = property(GetTableName, SetTableName)
    COLS = property(GetTableColumns, SetTableColumns)


def GenTableParam(a_name):
    """
    Generate table parameter struct
    """
    table_param = Table_Param()
    if a_name == "meta":
        table_param.NAME = "srm_meta_table"
        table_param.COLS = \
            (Column("version", String, primary_key=True),
             Column('site', String),
             Column('pairDbFile', String),
             Column('dumpType', String),
             Column('lock', Integer),
             Column('prNumber', String),
             Column('kbUrl', String),
             Column('desc', String))
    if a_name == "fixby":
        table_param.NAME = "srm_meta_table_fixby"
        table_param.COLS = \
            (Column("id", Integer, primary_key=True),  # will auto increase
             Column('module', String),
             Column('desc', String))

    return table_param
