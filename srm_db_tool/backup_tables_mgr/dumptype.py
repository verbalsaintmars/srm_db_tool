class DumpType(object):
    class CUSTOMIZED(object):
        def __str__(this):
            return 'customized'

    class ALL(object):
        def __str__(this):
            return 'all'

    class RecoveryPlan(object):
        def __str__(this):
            return 'recovery_plan'

    class ProtectionGrp(object):
        def __str__(this):
            return 'protection_grp'

    ALL = ALL()
    CUSTOMIZED = CUSTOMIZED()
    RecoveryPlan = RecoveryPlan()
    ProtectionGrp = ProtectionGrp()
