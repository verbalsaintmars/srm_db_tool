from os import listdir
from os.path import isfile, join, dirname, abspath, splitext


class WorkFlow(object):
    def __init__(this):
        current_path = dirname(abspath(__file__))  # path the script being run
        # os.getcwd #  current working directory

        this.wf_files = sorted([
            splitext(fn)[0] for fn in listdir(current_path)
            if isfile(join(current_path, fn))
            if fn.endswith('.py')
            if fn != "workflow.py"
            if fn != "__init__.py"])

    def GetWfList(this):
        from importlib import import_module

        module_list = []

        for fn in this.wf_files:

            wf_module = import_module(
                'srm_db_tool.backup_tables_mgr.tables.' + fn)

            module_list.append(
                (wf_module.wf_name,
                 wf_module.desc,
                 wf_module.table_list))

        return module_list
