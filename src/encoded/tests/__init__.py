# This has to be part of a plugin to support adding the command line option


def pytest_addoption(parser):
    parser.addoption('--engine-url', dest='engine_url', default='sqlite://')
