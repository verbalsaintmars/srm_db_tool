from os import listdir
from os.path import isfile, join, dirname, realpath, isdir
from shutil import copyfile


class OrmFile(object):

    CURR_DIR = dirname(realpath(__file__))

    SRM_ORM_DIR = join(CURR_DIR, "srm")

    VC_ORM_DIR = join(CURR_DIR, "vc")

    def __init__(this):
        pass

    def GenOrmFile(this, a_table_name, a_app):
        # from srm_db_tool.orm.srm import pdr_planproperties
        to_dir = this.SRM_ORM_DIR if a_app == 'srm' else this.VC_ORM_DIR
        template_file = 'table_template.py'

        if isfile(
                join(to_dir,
                     a_table_name + ".py")):
            return

        else:
            copyfile(
                join(this.CURR_DIR, template_file),
                join(to_dir,
                     a_table_name + ".py"))

    def ListOrmFiles(this, a_app):
        import re
        reg = '__init__'
        pat = re.compile(reg, re.IGNORECASE)
        to_dir = this.SRM_ORM_DIR if a_app == 'srm' else this.VC_ORM_DIR

        return tuple(
            [f for f in listdir(to_dir)
             if pat.search(f) is None and not f.startswith('.')
             and not isdir(join(to_dir, f))
             ])
