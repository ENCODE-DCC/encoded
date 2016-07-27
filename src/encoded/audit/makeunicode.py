import sys

if sys.version_info < (3,):

    def u(x):
        if isinstance(x, basestring):
            if not isinstance(x, unicode):
                x = unicode(x, 'utf-8')
        return x
else:

    def u(x):
        return x
