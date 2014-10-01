import argparse

version_parser = argparse.ArgumentParser(add_help=False)
version_parser.add_argument('--version',
                            action='version',
                            version='%(prog)s script version: 1.0')
