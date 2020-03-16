import pytest

@pytest.mark.skip(reason='will be addressed in a PYTEST-REFACTOR')
def test_graph_dot(testapp):
    res = testapp.get('/profiles/graph.dot', status=200)
    assert res.content_type == 'text/vnd.graphviz'
    assert res.text


@pytest.mark.skip(reason='will be addressed in a PYTEST-REFACTOR')
def test_graph_svg(testapp):
    res = testapp.get('/profiles/graph.svg', status=200)
    assert res.content_type == 'image/svg+xml'
    assert res.text
