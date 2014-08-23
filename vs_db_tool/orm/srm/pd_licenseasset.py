from .base import GenTable

class TheTable(object):
    __cache_engine__ = None
    __cache_table__ = None

    def __call__(this, a_engine):
        if this.__cache_engine__ is a_engine:
            return __cache_table__

        else:
            this.__cache_engine__ = a_engine
            this.__cache_table__ = GenTable('pd_licenseasset', a_engine)

        return this.__cache_table__

GetTable = TheTable()
