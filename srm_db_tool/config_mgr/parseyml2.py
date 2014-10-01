from ..exception.predefined import GeneralException

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import yaml

from os import getcwd
from os.path import join, realpath, dirname

"""
Reads the default directory .yml filename setting
"""
DEFAULT_YML_FILE = 'dft_dbtool.yml'


class ParseYml(object):
    def __init__(this):
        dft_yaml = yaml.load(
            open(join(dirname(realpath(__file__)), DEFAULT_YML_FILE), 'r'))
        this.default_yml_file = dft_yaml['default_config_file_name']
        del dft_yaml

    def _ParseSrm(this, a_result_dict, a_site):
        from ..sqlalchemy.db_support.init_params import Init_Params as DBParams

        site_val = None
        site_param = None

        if a_site == 'pp':
            site_val = 'srmdb_protect'
        else:
            site_val = 'srmdb_recovery'

        site_param = DBParams()

        try:
            site_param.DBTYPE = a_result_dict[site_val]['dbtype']
            site_param.UID = a_result_dict[site_val]['uid']
            site_param.PWD = a_result_dict[site_val]['pwd']
            try:
                site_param.DSN = a_result_dict[site_val]['dsn']
            except:
                try:
                    site_param.HOST = a_result_dict[site_val]['host']
                except:
                    print("Neither DSN or Host is provided for " + site_val)
                    #srm_pp = None
                    site_param = None
                else:
                    try:
                        site_param.PORT = a_result_dict[site_val]['port']
                    except:
                        print("using default port for " + site_val)
                    try:
                        site_param.DB = a_result_dict[site_val]['db']
                    except:
                        print("Provided host for " + site_val + " but no db provided.")
                        #srm_pp = None
                        site_param = None


        except KeyError as ke:
            print("{" + ke.message + "}" + " attribute does not exist")
            #srm_pp = None
            site_param = None

        return site_param

    def _SrmParser(this, a_result_dict):
        srm_pp = None
        srm_ss = None

        try:
            srm_pp = a_result_dict['srmdb_protect']
        except KeyError as ke:
            print("{" + ke.message + "}" + " attribute does not exist")
            print("No protected site SRM DB available.")
        else:
            srm_pp = this._ParseSrm(a_result_dict, 'pp')

        try:
            srm_ss = a_result_dict['srmdb_recovery']
        except KeyError as ke:
            print("{" + ke.message + "}" + " attribute does not exist")
            print("No recovery site SRM DB available.")
        else:
            srm_ss = this._ParseSrm(a_result_dict, 'ss')

        if srm_pp is None and srm_ss is None:
            print("No SRM db to manipulate...")
            return

        return (srm_pp, srm_ss)

    def _DbDirParser(this, a_result_dict):
        sqlite_db_dir = None
        try:
            sqlite_db_dir = a_result_dict['sqlite_db_dir']
        except KeyError as ke:
            print("{" + ke.message + "}" + " attribute does not exist")
            print("using system's tmp director for sqlite db files")
        return sqlite_db_dir

    def LoadYml(this):

        fd = None

        try:
            fd = open(join(getcwd(), this.default_yml_file), 'r')
        except Exception as e:
            print(GeneralException(
                "IO",
                "Could not load " + this.default_yml_file,
                 __name__))
            return

        result_dict = yaml.load(fd, Loader=Loader)

        sqlite_db_dir = this._DbDirParser(result_dict)
        srm_result = this._SrmParser(result_dict

        return (sqlite_db_dir, srm_result)
