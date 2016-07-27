import sys

if sys.version_info < (3,):

    def u(x):
        if isinstance(x, basestring):
            if not isinstance(x, 'utf-8'):
                x = unicode(x, 'utf-8')
        return x
else:

    def u(x):
        return x
