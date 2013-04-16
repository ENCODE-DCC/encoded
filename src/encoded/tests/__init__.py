# This has to be part of a plugin to support adding the command line option


def pytest_addoption(parser):
    parser.addoption('--engine-url', dest='engine_url', default='sqlite://')
    parser.addoption('--browser', dest='browser', default=None)
    parser.addoption('--browser-arg', nargs=2, dest='browser_args', action='append')
    parser.addoption('--remote-webdriver', dest='remote_webdriver', action='store_true', default=False)
