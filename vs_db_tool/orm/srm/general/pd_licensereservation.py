from vs_db_tool.sqlalchemy.orm.declare_mapping import OrmBase
from sqlalchemy import Column, Integer, String, Sequence


class pd_licensereservation(OrmBase):
    repr_format = "db_id : {db_id}, mo_id : {mo_id}, ref_count : {ref_count}, " \
    "protectedvmmoid : {protectedvmmoid}, vmmoid : {vmmoid}, "\
    "protectedvmtype : {protectedvmtype}, reservationstate : {reservationstate}"

    no_value = r'No_Value'

    __tablename__ = 'pd_licensereservation'

    db_id = Column(Integer, Sequence('user_id_seq'), primary_key = True)
    mo_id = Column(String(255))
    ref_count = Column(Integer)
    protectedvmmoid = Column(String)
    vmmoid = Column(String)
    protectedvmtype = Column(Integer)
    reservationstate = Column(Integer)

    def __repr__(this):
        return this.repr_format.format(
            db_id = this.db_id,
            mo_id = this.mo_id if this.mo_id.__len__() != 0 else this.no_value,
            ref_count = this.ref_count,
            protectedvmmoid = \
                this.protectedvmmoid if this.protectedvmmoid.__len__() != 0 else this.no_value,
            vmmoid = \
                this.vmmoid if this.vmmoid.__len__() != 0 else this.no_value,
            protectedvmtype = this.protectedvmtype,
            reservationstate = this.reservationstate)
