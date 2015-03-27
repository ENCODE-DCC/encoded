def test_graph_dot(testapp):
    res = testapp.get('/profiles/graph.dot', status=200)
    assert res.content_type == 'text/vnd.graphviz'


def test_graph_svg(testapp):
    res = testapp.get('/profiles/graph.svg', status=200)
    assert res.content_type == 'image/svg+xml'
