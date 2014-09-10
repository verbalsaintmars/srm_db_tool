# TODO
# Interface:
# PrintValue : Print out column name in the first line
#              Values follows
# PrintNameValue : Print out column name on the left, value on the right

class PrintResult(object):
    NameValueHeader = "{NAME:^10} : {VALUE:^10}"
    SPACER = "     "

    def __init__(this):
        this.TableNameValueHeader = None

    def PrintValue(this, a_name_list, a_value_list):
        format_str = ""
        for (cnt,name) in enumerate(a_name_list):
            if cnt != 0:
                format_str += this.SPACER

            format_str += "{" + str(cnt) + ":^5}"

        header_str = format_str.format(*a_name_list)

        print(header_str)

        for value in a_value_list:
            print(format_str.format(*value))

    def PrintNameValue(this, a_value_dict):
        for name, value in sorted(a_value_dict.items()):
            print("{} : {}".format(name, value))
