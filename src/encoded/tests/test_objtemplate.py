import pytest

NAMESPACE = {
    'foo': 'foo',
    'bar_list': ['bar1', 'bar2'],
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
    ({'templated': True, 'foo': 'value {foo}'}, {'foo': 'value foo'}),
    ({'templated': 'foo bar', 'foo': 'value {foo}'}, {'foo': 'value foo'}),
    ({'templated': 'bar', 'foo': 'value {foo}'}, {'foo': 'value {foo}'}),
    ({'a': [{'templated': True, 'repeat': 'bar bar_list',
             'bar': 'value {bar}', 'b': 1}]},
     {'a': [{'bar': 'value bar1', 'b': 1},
            {'bar': 'value bar2', 'b': 1},
            ]}),
    ({'a': [{'templated': 'foo bar', 'repeat': 'bar bar_list',
             'bar': 'value {bar}', 'b': 1}]},
     {'a': [{'bar': 'value bar1', 'b': 1},
            {'bar': 'value bar2', 'b': 1},
            ]}),
    ({'a': [{'templated': 'foo', 'repeat': 'bar bar_list',
             'bar': 'value {bar}', 'b': 1}]},
     {'a': [{'bar': 'value {bar}', 'b': 1},
            {'bar': 'value {bar}', 'b': 1},
            ]}),
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
