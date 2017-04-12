# This has to be part of a plugin to support adding the command line option
import argparse


class AppendInt2(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        values = (values[0], int(values[1]))
        return super(AppendInt2, self).__call__(parser, namespace, values, option_string)


def pytest_addoption(parser):
    parser.addoption('--browser-arg', nargs=2, dest='browser_args', action='append', type='string')
    parser.addoption('--browser-arg-int', nargs=2, dest='browser_args', action=AppendInt2, type='string')
    parser.addoption('--wsgi-arg', nargs=2, dest='wsgi_args', action='append', type='string')
