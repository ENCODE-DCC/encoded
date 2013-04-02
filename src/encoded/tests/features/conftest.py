""" Behave testing with pytest

This module combines behave testing with pytest
"""
from contextlib import contextmanager
import pytest
from _pytest.python import FixtureRequest, FuncFixtureInfo


@contextmanager
def fixture_context(fixture_request):
    from pytest.behave import _fixture_requests
    _fixture_requests.append(fixture_request)
    yield
    popped = _fixture_requests.pop()
    assert popped is fixture_request


# pytest.behave.getfixture
def getfixture(name):
    from pytest.behave import _fixture_requests
    fixture_request = _fixture_requests[-1]
    return fixture_request.getfuncargvalue(name)


def pytest_configure(config):
    config.addinivalue_line("markers", "behave: denotes a behave BDD test.")


def pytest_namespace():
    """ Behave currently relies on a single global step registry
    """
    # from behave.matchers import step_matcher
    from behave.step_registry import registry
    hooks = {}

    def _make_hook(hook_name):
        def decorator(wrapped):
            hooks.setdefault(hook_name, []).append(wrapped)
            return wrapped

        decorator.__name__ = hook_name
        return decorator

    _make_hook.__hooks__ = hooks

    ns = {
        # 'step_matcher': step_matcher,
        '_registry': registry,
        '_make_hook': _make_hook,  # Can't simply be a dict
        '_fixture_requests': [],  # Set later
        'getfixture': getfixture,
    }

    for step_type in ('given', 'when', 'then', 'step'):
        decorator = registry.make_decorator(step_type)
        ns[step_type] = decorator
        ns[step_type.title()] = decorator

    # Make before_step, etc. decorators
    for timing in ['before', 'after']:
        for place in ['step', 'scenario', 'feature', 'tag', 'all']:
            name = '%s_%s' % (timing, place)
            ns[name] = _make_hook(name)

    return {'behave': ns}


def pytest_collect_file(parent, path):
    if path.ext == '.feature':
        return FeatureFile(path, parent)
    dirpath = path.dirpath()
    if path.ext == '.py' and dirpath.basename == 'steps':
        path.pyimport()
        return
    if dirpath.basename == 'features' and \
            path.basename == 'environment.py':
        path.pyimport()
        return


class FeatureFile(pytest.File):
    def __init__(self, path, parent):
        super(FeatureFile, self).__init__(path, parent)
        # Set a keyword for all behave tests
        self.keywords['behave'] = pytest.mark.behave

    # Must be a separate object for the child fixture request to work.
    def collect(self):
        from behave.parser import parse_file
        feature = parse_file(self.fspath.strpath, language=None)
        yield Feature(feature, self)


class FixtureRequestMixin(object):
    funcargs = None
    _fixture_request = None
    _fixtureinfo = None

    @property
    def fixture_request(self):
        if self._fixture_request is None:
            # satisfy `FixtureRequest` constructor...
            self.funcargs = {}
            #fm = self.session._fixturemanager
            #fm.getfixtureinfo(self, self.setup, self.__class__, funcargs=False)
            self._fixtureinfo = FuncFixtureInfo((), [], {})
            self._fixture_request = FixtureRequest(self)
            #self.fixture_request.scope = 'module'
            self.obj = self.__class__
        return self._fixture_request


class Feature(FixtureRequestMixin, pytest.Collector):
    def __init__(self, feature, parent):
        super(Feature, self).__init__(feature.name, parent)
        self.feature = feature
        for tag in self.feature.tags:
            marker = getattr(pytest.mark, tag)
            self.keywords[marker.markname] = marker

    def collect(self):
        from behave import model
        for scenario in self.feature:
            if isinstance(scenario, model.ScenarioOutline):
                yield ScenarioOutline(scenario, self)
            else:
                yield Scenario(scenario, self)

    @property
    def runner(self):
        with fixture_context(self.fixture_request):
            return getfixture('behave_runner')

    def setup(self):
        runner = self.runner
        feature = self.feature
        from behave.formatter import formatters
        runner.feature = feature
        stream = runner.config.output
        runner.formatter = formatters.get_formatter(runner.config, stream)
        runner.formatter.uri(feature.filename)

        runner.context._push()
        runner.context.feature = feature

        # current tags as a set
        runner.context.tags = set(feature.tags)

        runner.formatter.feature(feature)

        with fixture_context(self.fixture_request):
            for tag in feature.tags:
                runner.run_hook('before_tag', runner.context, tag)
            runner.run_hook('before_feature', runner.context, feature)

        if feature.background:
            runner.formatter.background(feature.background)

    def teardown(self):
        runner = self.runner
        feature = self.feature

        with fixture_context(self.fixture_request):
            runner.run_hook('after_feature', runner.context, feature)
            for tag in feature.tags:
                runner.run_hook('after_tag', runner.context, tag)

        runner.context._pop()

        runner.formatter.eof()
        runner.formatter.stream.write('\n')

        stream = runner.config.output
        runner.formatter.close()
        stream.write('\n')

        for reporter in runner.config.reporters:
            reporter.feature(feature)

    def reportinfo(self):
        return self.fspath, 0, "Feature: %s" % self.name


class ScenarioOutline(FixtureRequestMixin, pytest.Collector):
    def __init__(self, outline, parent):
        super(ScenarioOutline, self).__init__(outline.name, parent)
        self.outline = outline

    @property
    def runner(self):
        return self.parent.runner

    @property
    def feature(self):
        return self.parent.feature

    def collect(self):
        for scenario in self.outline:
            yield Scenario(scenario, self)


class Scenario(FixtureRequestMixin, pytest.Collector):
    def __init__(self, scenario, parent):
        super(Scenario, self).__init__(scenario.name, parent)
        self.scenario = scenario
        for tag in self.scenario.tags:
            marker = getattr(pytest.mark, tag)
            self.keywords[marker.markname] = marker
        self.undefined = []
        self.run_steps = True

    @property
    def runner(self):
        return self.parent.runner

    @property
    def feature(self):
        return self.parent.feature

    def collect(self):
        for step in self.scenario:
            yield Step(step, self)

    def setup(self):
        from behave.step_registry import registry
        runner = self.runner
        feature = self.feature
        scenario = self.scenario

        tags = feature.tags + scenario.tags

        runner.formatter.scenario(scenario)

        row = getattr(scenario, '_row', None)
        if row is not None:
            runner.context._set_root_attribute('active_outline', row)

        runner.context._push()
        runner.context.scenario = scenario

        # current tags as a set
        runner.context.tags = set(tags)

        with fixture_context(self.fixture_request):
            for tag in scenario.tags:
                runner.run_hook('before_tag', runner.context, tag)
            runner.run_hook('before_scenario', runner.context, scenario)

        for step in scenario:
            runner.formatter.step(step)
            step.match = registry.find_match(step)
            if step.match is None:
                self.undefined.append(step)
                step.status = 'undefined'

    def teardown(self):
        runner = self.runner
        scenario = self.scenario

        for step in self.undefined:
            runner.undefined.append(step)

        with fixture_context(self.fixture_request):
            runner.run_hook('after_scenario', runner.context, scenario)
            for tag in scenario.tags:
                runner.run_hook('after_tag', runner.context, tag)

        runner.context._pop()
        runner.context._set_root_attribute('active_outline', None)


class Step(FixtureRequestMixin, pytest.Item):
    def __init__(self, step, parent):
        super(Step, self).__init__(step.name, parent)
        self.step = step

    @property
    def runner(self):
        return self.parent.runner

    @property
    def feature(self):
        return self.parent.feature

    @property
    def scenario(self):
        return self.parent.scenario

    def setup(self):
        from behave.model import NoMatch
        runner = self.runner
        step = self.step
        match = step.match

        if match is None:
            self.parent.run_steps = False
            runner.formatter.match(NoMatch())
            runner.formatter.result(self)
            pytest.skip('No match')
            return

        if not self.parent.run_steps:
            pytest.skip('Skipped')
            return

        runner.formatter.match(match)

        with fixture_context(self.fixture_request):
            runner.run_hook('before_step', runner.context, self)

    def runtest(self):
        import time
        runner = self.runner
        step = self.step
        match = step.match
        try:
            start = time.time()
            try:
                if step.text:
                    runner.context.text = step.text
                if step.table:
                    runner.context.table = step.table
                match.run(runner.context)
                step.status = 'passed'
            except Exception:
                step.status = 'failed'
                self.parent.run_steps = False
                runner.context._set_root_attribute('failed', True)
                raise
        finally:
            step.duration = time.time() - start

    def teardown(self):
        runner = self.runner
        step = self.step

        runner.formatter.result(step)
        with fixture_context(self.fixture_request):
            runner.run_hook('after_step', runner.context, step)


@pytest.fixture(scope='session')
def behave_config():
    # FIXME: read values from pytestconfig
    import sys
    from behave.reporter.junit import JUnitReporter
    from behave.reporter.summary import SummaryReporter
    from behave.tag_expression import TagExpression

    class Configuration(object):
        color = sys.platform != 'win32'
        stdout_capture = False
        stderr_capture = False
        show_snippets = True
        show_skipped = True
        log_capture = False
        dry_run = False
        show_source = True
        show_timings = True
        logging_format = '%(levelname)s:%(name)s:%(message)s'
        summary = False
        junit = False
        junit_directory = 'reports'
        format = ['plain']  # ['pretty']
        output = sys.stdout
        wip = False
        quiet = False
        show_multiline = False
        stop = False
        verbose = False
        expand = False

        def __init__(self, **kw):
            self.formatters = []
            self.reporters = []
            self.tags = []

            self.__dict__.update(kw)

            if self.wip:
                # Only run scenarios tagged with "wip". Additionally: use the
                # "plain" formatter, do not capture stdout or logging output and
                # stop at the first failure.
                self.format = ['plain']
                self.tags = ['wip']
                self.stop = True
                self.log_capture = False
                self.stdout_capture = False

            self.tags = TagExpression(self.tags or [])

            if self.quiet:
                self.show_source = False
                self.show_snippets = False

            if self.junit:
                # Buffer the output (it will be put into Junit report)
                self.stdout_capture = True
                self.stderr_capture = True
                self.log_capture = True
                self.reporters.append(JUnitReporter(self))
            if self.summary:
                self.reporters.append(SummaryReporter(self))

    config = Configuration()
    return config


@pytest.fixture(scope='session')
def behave_runner(request, behave_config):
    import behave.runner
    import pytest.behave

    class Runner(behave.runner.Runner):
        def __init__(self, config):
            super(Runner, self).__init__(config)
            self.context = behave.runner.Context(self)
            self.hooks = pytest.behave._make_hook.__hooks__
            self.context._set_root_attribute('getfixture',
                                             pytest.behave.getfixture)

        def run_hook(self, name, context, *args):
            with fixture_context(request):
                # Allow multiple hooks
                if name in self.hooks:
                    with context.user_mode():
                        for hook in self.hooks[name]:
                            hook(context, *args)

    runner = Runner(behave_config)

    @request.addfinalizer
    def after_all():
        with fixture_context(request):
            runner.run_hook('after_all', runner.context)
        for reporter in runner.config.reporters:
            reporter.end()

    with fixture_context(request):
        runner.run_hook('before_all', runner.context)

    return runner
