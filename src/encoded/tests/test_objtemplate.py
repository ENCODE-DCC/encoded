# -*- coding: utf-8 -*-
import pytest
import pyramid.settings


def check_keywords(**ns):
    assert ns == NAMESPACE
    return True


def check_arg(foo, default=None):
    assert foo == 'foo'
    return True


NAMESPACE = {
    'foo': 'foo',
    'bar_list': ['bar1', 'bar2'],
    'false_condition': False,
    'true_condition': True,
    'asbool': pyramid.settings.asbool,
    'check_keywords': check_keywords,
    'check_arg': check_arg,
    'unicode': u'1μM',
}

NO_CHANGE = [
    None,
    1,
    'one',
    'one{foo}',
    [1, 2, 3],
    {'a': [1, 2, 3]},
    {'b': [{'a': 'A'}]},
    [{'a': 1}],
]

TEMPLATE_VALUE = [
    ({'$templated': True, 'foo': '$value {foo}'}, {'foo': '$value foo'}),
    ({'$templated': 'foo bar', 'foo': '$value {foo}'}, {'foo': '$value foo'}),
    ({'$templated': 'bar', 'foo': '$value {foo}'}, {'foo': '$value {foo}'}),
    ({'a': [{'$templated': True, '$repeat': 'bar bar_list',
             'bar': '$value {bar}', 'b': 1}]},
     {'a': [{'bar': '$value bar1', 'b': 1},
            {'bar': '$value bar2', 'b': 1},
            ]}),
    ({'a': [{'$templated': 'foo bar', '$repeat': 'bar bar_list',
             'bar': '$value {bar}', 'b': 1}]},
     {'a': [{'bar': '$value bar1', 'b': 1},
            {'bar': '$value bar2', 'b': 1},
            ]}),
    ({'a': [{'$templated': 'foo', '$repeat': 'bar bar_list',
             'bar': '$value {bar}', 'b': 1}]},
     {'a': [{'bar': '$value {bar}', 'b': 1},
            {'bar': '$value {bar}', 'b': 1},
            ]}),
    ([{'a': 1}, {'b': 2, '$condition': 'false_condition'}],
     [{'a': 1}]),
    ([{'a': 1}, {'b': 2, '$condition': 'true_condition'}],
     [{'a': 1}, {'b': 2}]),
    ([{'$condition': 'asbool:false'}], []),
    ([{'$condition': 'asbool:true'}], [{}]),
    ([{'$condition': 'check_arg'}], [{}]),
    ([{'$condition': 'check_keywords'}], [{}]),
    ({'unicode': '{unicode}', '$templated': True}, {'unicode': u'1μM'}),
    ({'$value': '$value {foo}', '$templated': True}, '$value foo'),
    ([{'$templated': True, '$repeat': 'bar bar_list', '$value': '$value {bar}'}],
     ['$value bar1', '$value bar2']),
]


@pytest.mark.objtemplate
@pytest.mark.parametrize('value', NO_CHANGE)
def test_no_change(value):
    from encoded.objtemplate import ObjectTemplate
    compiled = ObjectTemplate(value)
    result = compiled(NAMESPACE)
    assert result == value


@pytest.mark.objtemplate
@pytest.mark.parametrize(('template', 'value'), TEMPLATE_VALUE)
def test_expected(template, value):
    from encoded.objtemplate import ObjectTemplate
    compiled = ObjectTemplate(template)
    result = compiled(NAMESPACE)
    assert result == value
