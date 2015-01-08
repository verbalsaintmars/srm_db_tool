# Interface:
# PrintValue : Print out column name in the first line
#              Values follows
# PrintNameValue : Print out column name on the left, value on the right


class PrintResult(object):
    NameValueHeader = "{NAME:^10} : {VALUE:^10}"
    SPACER = " " * 5

    def __init__(this):
        this.TableNameValueHeader = None

    def PrintValue(this, a_name_list, a_value_list):
        format_str = ""
        for (cnt, name) in enumerate(a_name_list):
            if cnt != 0:
                format_str += this.SPACER

            format_str += "{" + str(cnt) + ":<38}"

        header_str = format_str.format(*a_name_list)

        print(header_str)

        for value in a_value_list:
            print(format_str.format(*value))

    def PrintNameValue(this, a_value_dict):
        print("{:>25}: {:<25}".format("Column Name", "Value"))
        print("-------------------------------------------")
        for name, value in sorted(a_value_dict.items()):
            print("{:>25}: {:<25}".format(name, value))

    def PrintRecoveryPlan(this, a_pdr_planproperties):
        print("Recovery Plan : {}".format(a_pdr_planproperties.name))

    def PrintPgVm(this, a_vm_list):
        """
        Format:
        [(vm_gui_name, vm_moid, protected_vm_moid, peer_protected_vm_moid),
         (protection group gui name, pg_moid, peer_pg_moid)]
        """
        ProtectionGrp_Format = "{:^28} {:^25} {:^28}"
        VM_Format = "{:^18} {:^18} {:^25} {:^25}"

        print(ProtectionGrp_Format.format(
            "--PG Name--", "--PG moid--", "--PG Peer moid--"))

        pg_info = a_vm_list[0][1]

        print(ProtectionGrp_Format.format(*pg_info))
        print('\n\n')

        print(VM_Format.format(
            "--VM Name--", "--VM moid--", "--Protected VM moid--",
            "--Peer Protected VM moid--"))

        for vm in a_vm_list:
            print(VM_Format.format(*vm[0]))
