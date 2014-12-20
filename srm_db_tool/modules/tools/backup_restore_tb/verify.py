"""
For Windows Console Only
"""
import msvcrt


def GetVerify():
    print("Are you sure? [Y]es/[N]o")
    c = msvcrt.getch()
    print(c)
    return c
