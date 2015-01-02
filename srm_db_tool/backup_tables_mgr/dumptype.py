class DumpType(object):
    """
    This type is used for determine which tables are being backedup
    by each module.

    THis is important.

    That is to say, you don't want to run RecoverPlan check to against
    a ProtectionGroup dump. Since there's no RecoverPlan tables in the dump.

    U got the picture~
    """
    class CUSTOMIZED(object):
        def __init__(this):
            this.dtype = "customized"

        def SetType(this, a_msg):
            this.dtype = a_msg

        def GetType(this):
            return this.dtype

        def __str__(this):
            return this.dtype

        TYPE = property(GetType, SetType)

    class ALL(object):
        def __str__(this):
            return 'all'

    ALL = ALL()
    CUSTOMIZED = CUSTOMIZED()
