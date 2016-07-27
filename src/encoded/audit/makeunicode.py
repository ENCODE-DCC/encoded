import sys

if sys.version_info < (3,):

    def u(x):
        return x.decode('utf-8', 'replace')
else:

    def u(x):
        return x
