class DumpType(object):
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
    RecoveryPlan = RecoveryPlan()
    ProtectionGrp = ProtectionGrp()
