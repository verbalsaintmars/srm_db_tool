# Predefined Error String
MODULE_EXCEPT_FORMAT = "Module : {} , Exception : {}"
GENERAL_EXCEPT_FORMAT = "[{}] : {} : {}"
SA_EXCEPT_FORMAT = "[{}] : {} : {} : Orig except : {}"

"""
I0 : argument input error

O0 : output value unexpected

IO : io related errors

S0 : System Error
S1 : File Error

SA : SqlAlchemy error

DB: Dump DB manipulation error

U0 : Unknown error
"""


class GeneralException(Exception):
    def __init__(this, a_err, a_msg, a_name, a_except=None):
        super(GeneralException, this).__init__(a_msg)
        this.err = a_err
        this.name = a_name
        this.excpt = a_except

    def __str__(this):
        return GENERAL_EXCEPT_FORMAT.format(this.err, this.message, this.name)


class SaException(Exception):
    def __init__(this, a_err, a_msg, a_name, a_sa_e):
        super(SaException, this).__init__(a_msg)
        this.err = a_err
        this.name = a_name
        this.sae = a_sa_e

    def __str__(this):
        return SA_EXCEPT_FORMAT.format(
            this.err, this.message, this.name, this.sae.message)


class FixbyModuleException(Exception):
    def __init__(this, a_err, a_msg, a_name):
        super(FixbyModuleException, this).__init__(a_msg)
        this.err = a_err
        this.name = a_name

    def __str__(this):
        return GENERAL_EXCEPT_FORMAT.format(
            this.err, this.message, this.name)
