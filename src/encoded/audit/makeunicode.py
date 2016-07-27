import sys

if sys.version_info < (3,):
    import codecs

    def u(x):
        return codecs.decode(x, encoding='utf-8')
else:

    def u(x):
        return x
