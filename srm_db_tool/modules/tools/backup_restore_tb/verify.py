"""
For Windows Console Only
"""
import msvcrt
import sys


def GetVerify():
    print("Are you sure? [Y]es/[N]o")
    c = msvcrt.getch()
    if c == 'N':
        print("Existing...")
        sys.exit()
    elif c != 'Y':
        print("Please type in [Y]es/[N]o to continue.")
        GetVerify()
