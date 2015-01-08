from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy import Table, MetaData
from sqlalchemy.exc import NoSuchTableError


def GenTable(a_table_name, a_engine=None, a_table=None, a_base=None):

    if a_table is not None:
        __table__ = a_table
    else:
        try:
            if a_base is not None and a_base.metadata.is_bound():
                __table__ = Table(a_table_name, a_base.metadata, autoload=True)
            else:
                __table__ = Table(a_table_name, MetaData(bind=a_engine),
                                  autoload=True)
        except NoSuchTableError:
            return None

    if __table__.primary_key.__len__() == 0:
        """
        Dealing with tables that do not have Primary Key.
        Making all columns as Primary Key union
        """
        col_names = [str(c.name) for c in __table__.c]
        p = PrimaryKeyConstraint(*col_names)
        __table__.append_constraint(p)

    def __str__(this):
        """
        return the string of dict.
        column name : value
        """
        data = {col.name: getattr(this, col.name) for col in this.__table__.c}

        str_data = ""

        for (cnt, val) in enumerate(this.__table__.c):
            if cnt != 0:
                str_data += ", "
            str_data += "{" + val.name + "} : " + str(data[val.name])

        return str_data

    def __val_dict__(this):
        """
        Return a dict of column name : value
        """
        return {col.name: getattr(this, col.name) for col in this.__table__.c}

    """
    Dynamic generate table ORM class object
    """
    return type(a_table_name,
                (a_base
                    if a_base is not None
                    and a_base.metadata.is_bound() is True
                    else declarative_base(),),
                {'__table__': __table__,
                 '__str__': __str__,
                 '__val_dict__': __val_dict__})
