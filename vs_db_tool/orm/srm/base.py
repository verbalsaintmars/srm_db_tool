from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, MetaData


def GenTable(a_table_name, a_engine):

    __table__ = Table(a_table_name, MetaData(bind=a_engine), autoload=True)

    def __str__(this):
        data = {col.name: getattr(this, col.name) for col in this.__table__.c}

        str_data = ""

        for (cnt,val) in enumerate(this.__table__.c):
            if cnt != 0:
                str_data += ", "
            str_data += "{" + val.name + "} : " + str(data[val.name])

        return str_data

    def __val_dict__(this):
        return {col.name: getattr(this, col.name) for col in this.__table__.c}


    return type(a_table_name, (declarative_base(),),
                {'__table__': __table__,
                 '__str__': __str__,
                 '__val_dict__': __val_dict__})

"""
class pd_licenseasset(OrmBase):
    __table__ = Table("pd_licenseasset", MetaData(bind=a_engine), autoload=True)

    def __str__(this):
       data = {col.name : getattr(this, col.name) for col in this.__table__.c}
       str_data = ""
       for col in this.__table__.c:
          str_data += "{" + col.name + "} : " + str(data[col.name]) + ", "
       return str_data

"""
