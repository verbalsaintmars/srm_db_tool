from sqlalchemy.ext.declarative import declarative_base
from srm_db_tool.modules.tools.backup_restore_tb.regex import \
    ms_pat_1, ms_pat_2
import unicodedata


def BuildCache(a_conn, a_file):
    base = declarative_base()
    base.metadata.bind = a_conn.GetEngine()
    base.metadata.reflect()

    table_name = \
        sorted(
            [unicodedata.normalize('NFKD', t).encode('ascii', 'ignore')
             for t in base.metadata.tables
             if ms_pat_1.search(t) is None if ms_pat_2.match(t) is None])

    with open(a_file+'.py', 'w') as f:
        f.write('tables = {\n')

        for (offset, tn) in enumerate(table_name):
            if offset != 0:
                f.write(',\n')
            f.write('"' + tn + '"')

        f.write("}")

    return __import__(a_file).tables
