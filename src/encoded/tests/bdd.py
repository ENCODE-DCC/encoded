""" Behave testing with pytest

This plugin combines behave testing with pytest
"""
import behave.runner
import behave.step_registry
from contextlib import contextmanager
import pytest
from _pytest.python import (
    FixtureRequest,
    NOTSET,
    ScopeMismatchError,
    SubRequest,
    scopemismatch,
    scopeproperty,
    scopes,
)
import re


@pytest.fixture(scope='session')
def context(request):
    runner = request.session.config.pluginmanager.getplugin('bdd')
    context = runner.context

    # Hooks are called here so they only run when bdd tests are selected
    @request.addfinalizer
    def after_all():
        with runner.fixture_context(request):
            runner.run_hook('after_all', context)

    with runner.fixture_context(request):
        runner.run_hook('before_all', context)

    return context


@pytest.fixture(scope='module')
def feature(context):
    return context.feature


@pytest.fixture(scope='function')
def scenario(context):
    return context.scenario


@pytest.fixture(scope='subfunction')
def step(context):
    return context.step


def pytest_configure(config):
    config.addinivalue_line("markers", "bdd: denotes a BDD test.")
    bdd = BDDPlugin(config)
    config.pluginmanager.register(bdd, 'bdd')
    scopes.append('subfunction')  # XXX rethink step -> subfunction mapping


class BehaveConfig(object):
    verbose = False


class BDDPlugin(object):

    def __init__(self, config):
        self._config = config
        self.hooks = {}
        self._fixture_requests = []
        self.config = BehaveConfig()
        self.context = behave.runner.Context(self)
        self.step_registry = behave.step_registry.registry

#    @property
#    def reporter(self):
#        return self._config.pluginmanager.getplugin('terminalreporter')
#
#    @pytest.mark.tryfirst
#    def pytest_runtest_logstart(self, nodeid, location):
#        # ensure that the path is printed before the
#        # 1st test of a module starts running
#        reporter = self.reporter
#        if not reporter.showlongtestinfo:
#            return
#        #fspath = nodeid.split("::")[0]

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
            self.register_hooks(path.pyimport())
            return

    def register_hooks(self, environment):
        for place in ['step', 'scenario', 'feature', 'tag', 'all']:
            for timing in ['before', 'after']:
                name = '%s_%s' % (timing, place)
                hook = getattr(environment, name, None)
                if hook is None:
                    continue
                if not callable(hook):
                    continue
                self.hooks[name] = hook

    def pytest_namespace(self):
        """ Behave currently relies on a single global step registry
        """
        ns = {'getfixture': self.getfixture}

        for step_type in ('given', 'when', 'then', 'step'):
            decorator = self.step_registry.make_decorator(step_type)
            ns[step_type] = decorator
            ns[step_type.title()] = decorator

        return {'bdd': ns}

    def run_hook(self, name, context, *args):
        hook = self.hooks.get(name, None)
        if hook is None:
            return
        with context.user_mode():
            hook(context, *args)

    @contextmanager
    def fixture_context(self, fixture_request):
        """ Manages the fixture_request context
        """
        self._fixture_requests.append(fixture_request)
        yield
        popped = self._fixture_requests.pop()
        assert popped is fixture_request

    # pytest.bdd.getfixture
    def getfixture(self, name):
        fixture_request = self._fixture_requests[-1]
        return fixture_request.getfuncargvalue(name)


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


class BDDFixtureRequest(FixtureRequest):
    @scopeproperty()
    def function(self):
        """ test function object if the request has a per-function scope. """
        node = self._pyfuncitem.getparent(Scenario)
        if node:
            return node.obj
        if isinstance(self._pyfuncitem, Step):
            return self._pyfuncitem.obj

    @scopeproperty("class")
    def cls(self):
        """ class (can be None) where the test function was collected. """
        node = self._pyfuncitem.getparent(ScenarioOutline)
        if node:
            return node.obj

    @property
    def instance(self):
        """ instance (can be None) on which test function was collected. """
        return None

    @scopeproperty()
    def module(self):
        """ python module object where the test function was collected. """
        node = self._pyfuncitem.getparent(Feature)
        if node:
            return node.obj

    def _getscopeitem(self, scope):
        if scope == "session":
            return self.session
        if scope == "subfunction":
            x = self._pyfuncitem.getparent(Step)
            if x is not None:
                return x
            scope = "function"
        if scope == "function":
            x = self._pyfuncitem.getparent(Scenario)
            if x is not None:
                return x
            scope = "class"
        if scope == "class":
            x = self._pyfuncitem.getparent(ScenarioOutline)
            if x is not None:
                return x
            scope = "module"
        if scope == "module":
            return self._pyfuncitem.getparent(Feature)
        raise ValueError("unknown finalization scope %r" % (scope,))

    def _getfuncargvalue(self, fixturedef):
        # prepare a subrequest object before calling fixture function
        # (latter managed by fixturedef)
        argname = fixturedef.argname
        funcitem = self._pyfuncitem
        scope = fixturedef.scope
        try:
            param = funcitem.callspec.getparam(argname)
        except (AttributeError, ValueError):
            param = NOTSET
            param_index = 0
        else:
            # indices might not be set if old-style metafunc.addcall() was used
            param_index = funcitem.callspec.indices.get(argname, 0)
            # if a parametrize invocation set a scope it will override
            # the static scope defined with the fixture function
            paramscopenum = funcitem.callspec._arg2scopenum.get(argname)
            if paramscopenum is not None:
                scope = scopes[paramscopenum]

        subrequest = BDDSubRequest(self, scope, param, param_index, fixturedef)

        # check if a higher-level scoped fixture accesses a lower level one
        if scope is not None:
            __tracebackhide__ = True
            if scopemismatch(self.scope, scope):
                # try to report something helpful
                lines = subrequest._factorytraceback()
                raise ScopeMismatchError("You tried to access the %r scoped "
                    "fixture %r with a %r scoped request object, "
                    "involved factories\n%s" %(
                    (scope, argname, self.scope, "\n".join(lines))))
            __tracebackhide__ = False

        try:
            # call the fixture function
            val = fixturedef.execute(request=subrequest)
        finally:
            # if fixture function failed it might have registered finalizers
            self.session._setupstate.addfinalizer(fixturedef.finish,
                                                  subrequest.node)
        return val


class BDDSubRequest(BDDFixtureRequest, SubRequest):
    def __init__(self, *args, **kw):
        SubRequest.__init__(self, *args, **kw)



class FixtureRequestMixin(object):
    funcargs = {}
    nofuncargs = True
    _parse_param_tag = re.compile(r'(\w+)\(([\s\w,]+)\)').match

    def marker_from_tag(self, tag):
        args = None
        match = self._parse_param_tag(tag)
        if match is not None:
            tag = match.group(1)
            args = [arg.strip() for arg in match.group(2).split(',') if arg.strip()]
        marker = getattr(pytest.mark, tag)
        if args is not None:
            marker = marker(*args)
        return marker

    def _init_fixtures(self, markers=()):
        self.obj = lambda: None
        self.obj.__name__ = self.name.encode('utf-8')
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
        self._request = BDDFixtureRequest(self)
        self._request.scope = self.fixture_scope

    def _setup_fixtures(self, scope=None):
        if scope is None:
            scope = self.fixture_scope
        # Ensure scoped fixtures are run in the correct behave context
        with self.runner.context.user_mode():
            for fixturename in self.fixturenames:
                if fixturename == 'request':
                    continue
                fixture_scope = self._fixtureinfo.name2fixturedefs[fixturename][-1].scope
                if scopemismatch(scope, fixture_scope):
                    continue
                self._request.getfuncargvalue(fixturename)


class Feature(FixtureRequestMixin, pytest.Collector):
    outline = None
    fixture_scope = 'module'

    def __init__(self, model, parent):
        name = '%s: %s' % (model.keyword, model.name)
        super(Feature, self).__init__(name, parent)
        self.feature = self.model = model
        self.runner = self.session.config.pluginmanager.getplugin('bdd')
        markers = []
        for tag in self.model.tags:
            marker = self.marker_from_tag(tag)
            self.keywords[marker.markname] = marker
            markers.append(marker)
        self._init_fixtures(markers)

    def reportinfo(self):
        return self.fspath, self.model.line - 1, self.name

    def collect(self):
        from behave import model
        for scenario in self.feature:
            if isinstance(scenario, model.ScenarioOutline):
                yield ScenarioOutline(scenario, self)
            else:
                yield Scenario(scenario, self)

    def setup(self):
        runner = self.runner
        feature = self.feature
        runner.feature = feature

        with runner.fixture_context(self._request):
            # Ensure that before_all / after_all get called
            runner.getfixture('context')
            self._setup_fixtures('session')

        runner.context._push()
        runner.context.feature = feature

        # current tags as a set
        runner.context.tags = set(feature.tags)

        with runner.fixture_context(self._request):
            # Ensure scoped fixtures are run in the correct behave context
            self._setup_fixtures()

            for tag in feature.tags:
                runner.run_hook('before_tag', runner.context, tag)
            runner.run_hook('before_feature', runner.context, feature)

    def teardown(self):
        runner = self.runner
        feature = self.feature

        with runner.fixture_context(self._request):
            runner.run_hook('after_feature', runner.context, feature)
            for tag in feature.tags:
                runner.run_hook('after_tag', runner.context, tag)

        runner.context._pop()


class ScenarioOutline(FixtureRequestMixin, pytest.Collector):
    fixture_scope = 'cls'

    def __init__(self, model, parent):
        name = '%s: %s' % (model.keyword, model.name)
        super(ScenarioOutline, self).__init__(name, parent)
        self.outline = self.model = model
        self._init_fixtures()

    def reportinfo(self):
        return self.fspath, self.model.line - 1, self.name

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
    fixture_scope = 'function'

    def __init__(self, model, parent):
        name = '%s: %s' % (model.keyword, model.name)
        row = getattr(model, '_row', None)
        if row is not None:
            name += '[%s]' % '-'.join(row.cells)

        super(Scenario, self).__init__(name, parent)
        self.scenario = self.model = model
        markers = []
        for tag in self.model.tags:
            marker = self.marker_from_tag(tag)
            self.keywords[marker.markname] = marker
            markers.append(marker)
        self.undefined = []
        self.run_steps = True
        self._init_fixtures(markers)

    def reportinfo(self):
        return self.fspath, self.model.line - 1, self.name

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

        with runner.fixture_context(self._request):
            # Ensure scoped fixtures are run in the correct behave context
            self._setup_fixtures()

            for tag in scenario.tags:
                runner.run_hook('before_tag', runner.context, tag)
            runner.run_hook('before_scenario', runner.context, scenario)

        for step in scenario:
            step.match = runner.step_registry.find_match(step)
            if step.match is None:
                self.undefined.append(step)
                step.status = 'undefined'

    def teardown(self):
        runner = self.runner
        scenario = self.scenario

        #for step in self.undefined:
        #    runner.undefined.append(step)

        with runner.fixture_context(self._request):
            runner.run_hook('after_scenario', runner.context, scenario)
            for tag in scenario.tags:
                runner.run_hook('after_tag', runner.context, tag)

        runner.context._pop()
        runner.context._set_root_attribute('active_outline', None)


class Step(FixtureRequestMixin, pytest.Item):
    fixture_scope = 'subfunction'

    def __init__(self, model, parent):
        name = u'%s %s' % (model.keyword, model.name)
        name = name.encode('ascii', 'backslashreplace')
        super(Step, self).__init__(name, parent)
        self.step = self.model = model
        self._init_fixtures()
        # Make -k happy on pytest 2.4
        self.function = lambda: None

    def reportinfo(self):
        return self.fspath, self.model.line - 1, self.name

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

        runner.context.step = step

        if match is None:
            self.parent.run_steps = False
            pytest.skip('No match')
            return

        if not self.parent.run_steps:
            pytest.skip('Skipped')
            return

        with runner.fixture_context(self._request):
            self._setup_fixtures()
            runner.run_hook('before_step', runner.context, self)

    def runtest(self):
        runner = self.runner
        step = self.step
        match = step.match
        if step.text:
            runner.context.text = step.text
        if step.table:
            runner.context.table = step.table
        try:
            with runner.fixture_context(self._request):
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

        with runner.fixture_context(self._request):
            runner.run_hook('after_step', runner.context, step)
