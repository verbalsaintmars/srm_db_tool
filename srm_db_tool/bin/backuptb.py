"""
backuptb table_name {db file name} {pp,ss}
backuptb all {db file name} {pp,ss}
"""

import argparse

ap_args = {'description': 'Backup SRM database tables',
           'epilog': 'Contact shc for any help.',
           'fromfile_prefix_chars': '@',
           'add_help': False}

parser = argparse.ArgumentParser(**ap_args)

aa_table_name_args = {'type': str,
                      'help': "type in table name to backup "
                      "or all to back the whole database",
            }

parser.add_argument('table_name', **aa_table_name_args)

aa_dbfilename_args = {'type': str,
                      'help': "sqlite db file name or use default generated name"
            }

parser.add_argument('db_file_name', **aa_dbfilename_args)



#result = parser.parse_args(["pds_table_name"])
parser.parse_args()

