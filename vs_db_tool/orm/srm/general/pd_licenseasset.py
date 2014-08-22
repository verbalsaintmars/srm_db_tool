from vs_db_tool.sqlalchemy.orm.declare_mapping import OrmBase
from sqlalchemy import Column, Integer, String, Sequence


class pd_licenseasset(OrmBase):
    repr_format = "db_id : {db_id}, mo_id : {mo_id}, ref_count : {ref_count}, " \
    "assetid : {assetid}, productname : {productname}, "\
    "productversion : {productversion}, licensetype : {licensetype}, " \
    "evaluationexpirydate : {evaluationexpirydate}, licensekey : {licensekey}, " \
    "costunit : {costunit}, used : {used}, featuresinuse : {featuresinuse}, " \
    "vmids : {vmids}, waslicensed : {waslicensed}, displayname : {displayname}, " \
    "evaluationlicensekey : {evaluationlicensekey}, waseelicensed : {waseelicensed}"

    no_value = r'No_Value'

    __tablename__ = 'pd_licenseasset'

    db_id = Column(Integer, Sequence('user_id_seq'), primary_key = True)
    mo_id = Column(String(255))
    ref_count = Column(Integer)
    assetid = Column(String)
    productname = Column(String)
    productversion = Column(String)
    licensetype = Column(Integer)
    evaluationexpirydate = Column(String)
    licensekey = Column(String)
    costunit = Column(Integer)
    used = Column(Integer)
    featuresinuse = Column(Integer)
    vmids = Column(Integer)
    waslicensed = Column(Integer)
    displayname = Column(String)
    evaluationlicensekey = Column(String)
    waseelicensed = Column(Integer)

    def __repr__(this):
        return this.repr_format.format(
            db_id = this.db_id,
            mo_id = this.mo_id if this.mo_id.__len__() != 0 else this.no_value,
            ref_count = this.ref_count,
            assetid = this.assetid if this.assetid.__len__() != 0 else this.no_value,
            productname = \
                this.productname if this.productname.__len__() != 0 else this.no_value,
            productversion = \
                this.productversion if this.productversion.__len__() != 0 else this.no_value,
            licensetype = this.licensetype,
            evaluationexpirydate = \
                this.evaluationexpirydate if this.evaluationexpirydate.__len__() != 0 \
                    else this.no_value,
            licensekey = this.licensekey,
            costunit = this.costunit,
            used = this.used,
            featuresinuse = this.featuresinuse,
            vmids = this.vmids,
            waslicensed = this.waslicensed,
            displayname = this.displayname if this.displayname.__len__() != 0 else \
                    this.no_value,
            evaluationlicensekey = this.evaluationlicensekey \
                    if this.evaluationlicensekey.__len__() != 0 else this.no_value,
            waseelicensed = this.waseelicensed)
