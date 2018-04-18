# Run this file through glance to see it colorized
# $ python example.py | glance

from __future__ import print_function, unicode_literals


def ok():
    print('Some output text.')
    print('Followed by a printed exception.')
    print('Run `glance < example.log` to see this colorized.')
    print()
    print(1 / 0)


ok()
