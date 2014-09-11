from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy import Table, MetaData
from sqlalchemy.sql.schema import Column
from sqlalchemy import Integer

# TODO
# Should cache the created table inside the same MetaData object


def GenTable(a_table_name, a_engine):

    __table__ = Table(a_table_name, MetaData(bind=a_engine), autoload=True)
    #__table__ = Table(a_table_name, MetaData(), Column('seq_id', Integer, primary_key=True),
    #                  autoload=True, autoload_with = a_engine)
                          # check for primary key
    if __table__.primary_key.__len__() == 0:
        """
        for c in __table__.c:
            c.primary_key = True
            print(c.name)
        """
        col_names = [str(c.name) for c in __table__.c]
        p = PrimaryKeyConstraint(*col_names)
        __table__.append_constraint(p)

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
