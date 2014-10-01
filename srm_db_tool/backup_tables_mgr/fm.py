"""
Generate sqlite db file name under sqlite_tmp
Base on
1. Sequence number or (i.e sqlite_db_0001.db)
2. input string (xxxx.db)

"""
from ..exception.predefined import GeneralException

import os
import re
import tempfile


def comp_db_file_name(lhs, rhs):
    pat = re.compile("\d{4}")
    lhs_m = pat.search(lhs)
    rhs_m = pat.search(rhs)

    if int(lhs_m.group()) < int(rhs_m.group()):
        return -1
    else:
        return 1


class DbFileOp(object):
    FILE_REGEX = "sqlite_db_\d{4}\.db"
    # current_path = os.path.dirname(os.path.realpath(__file__))
    # DEFAULT_DB_PATH = os.path.join(current_path, "sqlite_tmp")
    DEFAULT_DB_PATH = tempfile.gettempdir()

    def __init__(this, a_default_path=None):
        this.path = \
            this.DEFAULT_DB_PATH if not a_default_path else a_default_path

    def GetFileName(this, a_fullpath=False):
        from os import listdir, makedirs
        from os.path import isfile, join, exists

        pat = re.compile(DbFileOp.FILE_REGEX, re.IGNORECASE)

        if not exists(this.path):
            makedirs(this.path)
            return []

        return sorted(
            [f if not a_fullpath else join(this.path, f)
             for f in listdir(this.path)
             if isfile(join(this.path, f)) and
             pat.search(f) is not None],
            key=str.lower,
            cmp=comp_db_file_name)

    def NextFileName(this):
        from os.path import join
        db_files = this.GetFileName()
        pat = re.compile("\d{4}")

        if db_files.__len__() != 0:
            return join(this.path, "sqlite_db_" + str(
                int(pat.search(db_files[-1]).group()) + 1).zfill(4) + ".db")
        else:
            return join(this.path, "sqlite_db_0001.db")

    def LatestFileName(this, a_fullpath=True):
        db_files = this.GetFileName(a_fullpath=a_fullpath)
        if db_files.__len__() != 0:
            return db_files[-1]
        else:
            return None

    def RemoveFiles(this, a_filename=None):
        from os.path import join
        if a_filename is not None:
            try:
                os.remove(join(this.path, a_filename))
            except Exception as e:
                print(
                    GeneralException(
                        'S1',
                        "Can not remove file : {}".format(a_filename),
                        __name__))
        else:
            db_files = this.GetFileName(a_fullpath=True)
            for f in db_files:
                try:
                    os.remove(f)
                except Exception as e:
                    print(
                        GeneralException(
                            'S1',
                            "Can not remove file : {}".format(f),
                            __name__,
                            e))
