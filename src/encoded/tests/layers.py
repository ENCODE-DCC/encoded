''' Layers

Make pytest fixtures work more like zope.testrunner layers:

https://pypi.python.org/pypi/zope.testrunner#layers
'''
from _pytest.python import (
    scopes,
    scopenum_function,
)
import operator
import pytest


def pytest_configure(config):
    layer_manager = LayerManager(config)
    config.pluginmanager.register(layer_manager, 'layers')
    config.addinivalue_line("markers", "fixture_cost(N): denotes a BDD test.")


def layer_key(fixturedefs):
    return tuple(sorted(fixturedefs, key=lambda fd: fd[-1].argname))


class LayerManager(object):
    def __init__(self, config):
        self.config = config
        self.layers = {}

    def layer_for_item(self, item):
        fi = item._fixtureinfo
        argnames = tuple(self.relevant_argnames(fi))
        layer = Layer(self, item, *argnames)
        return layer

    def relevant_argnames(self, fi):
        for name in fi.names_closure:
            fd = fi.name2fixturedefs.get(name)
            if fd is None:
                continue
            if fd[-1].scopenum < scopenum_function:
                yield name

    def sorted_layers(self):
        ''' Sort layers so that those with the largest fixture_cost are least
            likely to to be split up.
        '''
        seen = set()
        layers = sorted(self.layers.values(), reverse=True, key=operator.attrgetter('weight'))
        order = [] # [d  for layer in layers for d in self.gather(seen, layer)]
        for layer in layers:
            for d in self.gather(seen, layer):
                order.append(d)
        order.reverse()
        assert len(order) == len(self.layers)
        return order

    def gather(self, seen, layer, required=()):
        if layer.key in seen:
            return
        skip = required and not (required <= layer.fixturedefs_closure)
        if not skip:
            seen.add(layer.key)
        deps = (self.layers[layer_key(dep)] for dep in layer.deps)
        deps = sorted(deps, reverse=True, key=operator.attrgetter('weight'))
        deps_required = set(required)
        deps_required.update(layer.fixturedefs_closure)
        for dep in deps:
            for d in self.gather(seen, dep, deps_required):
                yield d
        if not skip:
            yield layer
        if required:
            return
        for base in sorted(layer.bases, reverse=True, key=operator.attrgetter('weight')):
            for d in self.gather(seen, base, required):
                yield d

    @pytest.mark.trylast
    def pytest_collection_modifyitems(self, session, config, items):
        ''' Reorder tests to minimize fixture setups/teardowns
        '''
        for item in items:
            layer = self.layer_for_item(item)
            layer.items.append(item)

        reordered = []
        for layer in self.sorted_layers():
            reordered.extend(layer.items)
        assert len(items) == len(reordered)
        items[:] = reordered
        #self._print_layers(items)

    def _print_layers(self, items):
        current = set()
        for item in items:
            next = set()
            fi = item._fixtureinfo
            for name in self.relevant_argnames(fi):
                fd = fi.name2fixturedefs.get(name)
                if fd is None:
                    continue
                next.add(fd)
            for fd in current - next:
                print "TEARDOWN: %s (%s)" % (fd[-1].argname, fd[-1].scope)
            for fd in next - current:
                print "SETUP: %s (%s)" % (fd[-1].argname, fd[-1].scope)
            print item
            current = next
        layers = self.sorted_layers()
        for i, layer in enumerate(layers):
            print layer.weight, layer

    @pytest.mark.tryfirst
    def pytest_runtest_setup(self, item):
        ''' Proactively setup shared fixtures in order
        '''
        fixturenames = getattr(item, "fixturenames", item._request.fixturenames)
        keylist = []
        scopenum = scopes.index(item._request.scope  or "function")
        for argname in fixturenames:
            fixturedef = item._fixtureinfo.name2fixturedefs.get(argname)
            if fixturedef is None:
                continue
            if hasattr(fixturedef[-1], 'cached_result'):
                continue
            if fixturedef[-1].scopenum >= scopenum:
                continue
            layer = self.layers.get(layer_key([fixturedef]), None)
            weight = 1 if layer is None else layer.weight
            key = (fixturedef[-1].scopenum, weight, argname, fixturedef)
            keylist.append(key)

        keylist.sort()
        for scopenum, weight, argname, fd in keylist:
            if argname not in item.funcargs:
                #print "SETUP: %s (%s)" % (fd[-1].argname, fd[-1].scope)
                item.funcargs[argname] = item._request.getfuncargvalue(argname)

    @pytest.mark.trylast
    def pytest_runtest_teardown(self, item, nextitem):
        ''' Teardown unused fixtures
        '''
        if nextitem is None:
            return

        keylist = []
        nextitem_name2fixturedefs = nextitem._fixtureinfo.name2fixturedefs
        for argname, fixturedef in item._fixtureinfo.name2fixturedefs.items():
            if not hasattr(fixturedef[-1], 'cached_result'):
                continue
            nextitem_fixturedef = nextitem_name2fixturedefs.get(argname, None)
            if nextitem_fixturedef == fixturedef:
                continue
            layer = self.layers.get(layer_key([fixturedef]), None)
            weight = 1 if layer is None else layer.weight
            key = (fixturedef[-1].scopenum, weight, argname, fixturedef)
            keylist.append(key)

        fixturemanager = item.session.config.pluginmanager.getplugin("funcmanage")

        keylist.sort(reverse=True)
        for scopenum, weight, argname, fd in keylist:
            #print "TEARDOWN: %s (%s)" % (fd[-1].argname, fd[-1].scope)
            fd[-1].finish()


class Layer(object):
    ''' A Layer is a unique set of fixtures

    Layers fall into two categories:

    * A unique set of fixtures shared by one or more tests.
    * A particular fixture.

    We assume that fixture ordering in argnames is not significant.
    '''

    weight = 0
    def __new__(cls, layer_manager, item, *argnames):
        layers = layer_manager.layers
        fi = item._fixtureinfo
        key = layer_key(fi.name2fixturedefs[name] for name in argnames)
        self = layers.get(key, None)
        if self is not None:
            return self
        self = super(Layer, cls).__new__(cls, layers, fi, argnames)
        layers[key] = self

        self.fixtureinfo = fi
        self.key = key
        self.fixturedefs_closure = set(key)
        self.items = []
        self.deps = set()
        self.scopenum = max(fd[-1].scopenum for fd in key) if key else scopenum_function

        if len(key) == 1:
            fd, = key
            self.argname = fd[-1].argname
            self.baseid = fd[-1].baseid
            base_fixturedefs = sorted(
                (fi.name2fixturedefs[name], name)
                    for name in fd[-1].argnames if name in fi.name2fixturedefs)
            fixture_cost = getattr(fd[-1].func, 'fixture_cost', None)
            if fixture_cost is not None:
                self.weight += fixture_cost.args[0]
            else:
                self.weight = 1
        else:
            self.argname = ','.join(fd[-1].argname for fd in key)
            self.baseid = '<virtual>'
            base_fixturedefs = sorted(
                (fi.name2fixturedefs[name], name)
                    for name in argnames if name in fi.name2fixturedefs)
        self.bases = tuple(
            cls(layer_manager, item, name)
            for fd, name in base_fixturedefs
            if fd is not None  # request
        )
        for base in self.bases:
            self.fixturedefs_closure.update(base.fixturedefs_closure)

        for fd in self.fixturedefs_closure:
            other_key = layer_key([fd])
            if other_key != key:
                layers[other_key].deps.add(key)

        return self

    def __init__(self, layers, fi, *argnames):
        pass

    def __repr__(self):
        return '<%s (%s) %s:%s [%s]>' % (
            type(self).__name__,
            scopes[self.scopenum],
            self.baseid,
            self.argname if len(self.key) == 1 else '',
            ','.join(base.argname for base in self.bases),
        )
