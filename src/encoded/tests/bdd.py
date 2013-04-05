""" Behave testing with pytest

This module combines behave testing with pytest
"""
from contextlib import contextmanager
import pytest
from _pytest.python import FixtureRequest
import re

parse_param_tag = re.compile(r'(\w+)\(([\s\w,]+)\)').match


def marker_from_tag(tag):
    args = None
    match = parse_param_tag(tag)
    if match is not None:
        tag = match.group(1)
        args = [arg.strip() for arg in match.group(2).split(',') if arg.strip()]
    marker = getattr(pytest.mark, tag)
    if args is not None:
        marker = marker(*args)
    return marker


@contextmanager
def fixture_context(fixture_request):
    """ Manages the fixture_request context
    """
    from pytest.bdd import _fixture_requests
    _fixture_requests.append(fixture_request)
    yield
    popped = _fixture_requests.pop()
    assert popped is fixture_request


# pytest.bdd.getfixture
def getfixture(name):
    from pytest.bdd import _fixture_requests
    fixture_request = _fixture_requests[-1]
    return fixture_request.getfuncargvalue(name)


def pytest_configure(config):
    config.addinivalue_line("markers", "bdd: denotes a BDD test.")
    bdd = BDDPlugin(config)
    config.pluginmanager.register(bdd, 'bdd')


class BDDPlugin(object):
    def __init__(self, config):
        self.config = config

    @property
    def reporter(self):
        return self.config.pluginmanager.getplugin('terminalreporter')

    @pytest.mark.tryfirst
    def pytest_runtest_logstart(self, nodeid, location):
        # ensure that the path is printed before the
        # 1st test of a module starts running
        reporter = self.reporter
        if not reporter.showlongtestinfo:
            return
        #fspath = nodeid.split("::")[0]

    def pytest_runtest_setup(self, item):
        pass

    def pytest_collect_file(self, parent, path):
        if path.ext == '.feature':
            return FeatureFile(path, parent, self)
        dirpath = path.dirpath()
        if path.ext == '.py' and dirpath.basename == 'steps':
            path.pyimport()
            return
        if dirpath.basename == 'features' and \
                path.basename == 'environment.py':
            path.pyimport()
            return

    def pytest_namespace(self):
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

        return {'bdd': ns}


class FeatureFile(pytest.File):
    def __init__(self, path, parent, bdd_plugin):
        super(FeatureFile, self).__init__(path, parent)
        # Set a keyword for all behave tests
        self.keywords['bdd'] = pytest.mark.bdd
        self.bdd_plugin = bdd_plugin
        self.obj = lambda: None

    # Must be a separate object for the child fixture request to work.
    def collect(self):
        from behave.parser import parse_file
        feature = parse_file(self.fspath.strpath, language=None)
        yield Feature(feature, self)


class FixtureRequestMixin(object):
    funcargs = {}
    nofuncargs = True

    def _init_fixtures(self, markers=()):
        self.obj = lambda: None
        if hasattr(self.parent.obj, 'usefixtures'):
            info = self.parent.obj.usefixtures
            pytest.mark.usefixtures(*info.args, **info.kwargs)(self.obj)
        for marker in markers:
            marker(self.obj)
        fm = self.session._fixturemanager
        self._fixtureinfo = fi = fm.getfixtureinfo(self.parent, self.obj,
                                                   None,
                                                   funcargs=False)
        self.fixturenames = fi.names_closure
        self._request = FixtureRequest(self)


class Feature(FixtureRequestMixin, pytest.Collector):
    outline = None

    def __init__(self, model, parent):
        name = '%s: %s' % (model.keyword, model.name)
        super(Feature, self).__init__(name, parent)
        self.feature = self.model = model
        markers = []
        for tag in self.model.tags:
            marker = marker_from_tag(tag)
            self.keywords[marker.markname] = marker
            markers.append(marker)
        self._init_fixtures(markers)

    def reportinfo(self):
        return self.fspath, self.model.line, self.name

    def collect(self):
        from behave import model
        for scenario in self.feature:
            if isinstance(scenario, model.ScenarioOutline):
                yield ScenarioOutline(scenario, self)
            else:
                yield Scenario(scenario, self)

    @property
    def runner(self):
        with fixture_context(self._request):
            return getfixture('behave_runner')

    def setup(self):
        for fixturename in self.fixturenames:
            self._request.getfuncargvalue(fixturename)
        runner = self.runner
        feature = self.feature
        runner.feature = feature

        runner.context._push()
        runner.context.feature = feature

        # current tags as a set
        runner.context.tags = set(feature.tags)

        with fixture_context(self._request):
            for tag in feature.tags:
                runner.run_hook('before_tag', runner.context, tag)
            runner.run_hook('before_feature', runner.context, feature)

    def teardown(self):
        runner = self.runner
        feature = self.feature

        with fixture_context(self._request):
            runner.run_hook('after_feature', runner.context, feature)
            for tag in feature.tags:
                runner.run_hook('after_tag', runner.context, tag)

        runner.context._pop()


class ScenarioOutline(FixtureRequestMixin, pytest.Collector):
    def __init__(self, model, parent):
        name = '%s: %s' % (model.keyword, model.name)
        super(ScenarioOutline, self).__init__(name, parent)
        self.outline = self.model = model
        self._init_fixtures()

    def reportinfo(self):
        return self.fspath, self.model.line, self.name

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
    def __init__(self, model, parent):
        name = '%s: %s' % (model.keyword, model.name)
        row = getattr(model, '_row', None)
        if row is not None:
            name += '[%s]' % '-'.join(row.cells)

        super(Scenario, self).__init__(name, parent)
        self.scenario = self.model = model
        markers = []
        for tag in self.model.tags:
            marker = marker_from_tag(tag)
            self.keywords[marker.markname] = marker
            markers.append(marker)
        self.undefined = []
        self.run_steps = True
        self._init_fixtures(markers)

    def reportinfo(self):
        return self.fspath, self.model.line, self.name

    @property
    def runner(self):
        return self.parent.runner

    @property
    def feature(self):
        return self.parent.feature

    @property
    def outline(self):
        return self.parent.outline

    def collect(self):
        for step in self.scenario:
            yield Step(step, self)

    def setup(self):
        for fixturename in self.fixturenames:
            self._request.getfuncargvalue(fixturename)
        from behave.step_registry import registry
        runner = self.runner
        feature = self.feature
        scenario = self.scenario

        tags = feature.tags + scenario.tags

        row = getattr(scenario, '_row', None)
        if row is not None:
            runner.context._set_root_attribute('active_outline', row)

        runner.context._push()
        runner.context.scenario = scenario

        # current tags as a set
        runner.context.tags = set(tags)

        with fixture_context(self._request):
            for tag in scenario.tags:
                runner.run_hook('before_tag', runner.context, tag)
            runner.run_hook('before_scenario', runner.context, scenario)

        for step in scenario:
            step.match = registry.find_match(step)
            if step.match is None:
                self.undefined.append(step)
                step.status = 'undefined'

    def teardown(self):
        runner = self.runner
        scenario = self.scenario

        #for step in self.undefined:
        #    runner.undefined.append(step)

        with fixture_context(self._request):
            runner.run_hook('after_scenario', runner.context, scenario)
            for tag in scenario.tags:
                runner.run_hook('after_tag', runner.context, tag)

        runner.context._pop()
        runner.context._set_root_attribute('active_outline', None)


class Step(FixtureRequestMixin, pytest.Item):
    def __init__(self, model, parent):
        name = '%s %s' % (model.keyword, model.name)
        super(Step, self).__init__(name, parent)
        self.step = self.model = model
        self._init_fixtures()

    def reportinfo(self):
        return self.fspath, self.model.line, self.name

    @property
    def runner(self):
        return self.parent.runner

    @property
    def feature(self):
        return self.parent.feature

    @property
    def outline(self):
        return self.parent.outline

    @property
    def scenario(self):
        return self.parent.scenario

    def setup(self):
        runner = self.runner
        step = self.step
        match = step.match

        if match is None:
            self.parent.run_steps = False
            pytest.skip('No match')
            return

        if not self.parent.run_steps:
            pytest.skip('Skipped')
            return

        with fixture_context(self._request):
            runner.run_hook('before_step', runner.context, self)

    def runtest(self):
        for fixturename in self.fixturenames:
            self._request.getfuncargvalue(fixturename)
        runner = self.runner
        step = self.step
        match = step.match
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

    def teardown(self):
        runner = self.runner
        step = self.step

        with fixture_context(self._request):
            runner.run_hook('after_step', runner.context, step)


@pytest.fixture(scope='session')
def behave_runner(request):
    import behave.runner
    import pytest.bdd

    class Context(behave.runner.Context):
        @property
        def _request(self):
            from pytest.bdd import _fixture_requests
            return _fixture_requests[-1]

    class Runner(object):
        config = None

        def __init__(self):
            self.context = Context(self)
            self.hooks = pytest.bdd._make_hook.__hooks__
            self.context._set_root_attribute('getfixture',
                                             pytest.bdd.getfixture)

        def run_hook(self, name, context, *args):
            with fixture_context(request):
                # Allow multiple hooks
                if name in self.hooks:
                    with context.user_mode():
                        for hook in self.hooks[name]:
                            hook(context, *args)

    runner = Runner()

    @request.addfinalizer
    def after_all():
        with fixture_context(request):
            runner.run_hook('after_all', runner.context)

    with fixture_context(request):
        runner.run_hook('before_all', runner.context)

    return runner
