# This has to be part of a plugin to support adding the command line option


def pytest_addoption(parser):

    def int_arg(options, opt, value, parser):
        parser.values.ensure_value(options.dest, [])
        value = (value[0], int(value[1]))
        getattr(parser.values, options.dest).append(value)

    parser.addoption('--engine-url', dest='engine_url', default='sqlite://')
    parser.addoption('--browser', dest='browser', default=None)
    parser.addoption('--browser-arg', nargs=2, dest='browser_args', action='append', type='string')
    parser.addoption('--browser-arg-int', nargs=2, dest='browser_args', action='callback', callback=int_arg, type='string')
    parser.addoption('--remote-webdriver', dest='remote_webdriver', action='store_true', default=False)
