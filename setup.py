from setuptools import setup

setup(
    name='srm_db_probe',
    version='1.0.1',
    description='SRM DB Probe Kit Project',
    url=r'https://github.com/verbalsaintmars/srm_db_tool',
    author='shchang',
    author_email=r'shchang@vmware.com',
    install_requires=[
        "SQLAlchemy",
        "pyodbc >= 3.0.7",
        "pyyaml >= 3.0.0"],
    packages=[
        'srm_db_tool',
        'srm_db_tool.backup_tables_mgr',
        'srm_db_tool.config_mgr',
        'srm_db_tool.exception',
        'srm_db_tool.formatter',
        'srm_db_tool.modules',
        'srm_db_tool.modules.check',
        'srm_db_tool.modules.check.recovery_plan',
        'srm_db_tool.modules.tools',
        'srm_db_tool.modules.tools.backup_restore_tb',
        'srm_db_tool.modules.tools.recovery_plan',
        'srm_db_tool.modules.tools.version_check',
        'srm_db_tool.orm',
        'srm_db_tool.sqlalchemy',
        'srm_db_tool.sqlalchemy.db_support'
        ],
    scripts=[
        'srm_db_tool/bin/restoretb.py',
        'srm_db_tool/bin/deletetb.py',
        'srm_db_tool/bin/backuptb.py',
        'srm_db_tool/bin/lsrp.py',
        'srm_db_tool/bin/rmrp.py',
        'srm_db_tool/bin/restorerp.py'],
    package_data={
        'srm_db_tool.config_mgr': ['dft_dbtool.yml'],
    }
    )
