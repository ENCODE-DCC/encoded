import pytest

'''
    Used to generate schema diagrams. The code is in snovault/src/snovault/schema_graph.py. 
'''
def test_graph_dot(testapp):
    res = testapp.get('/profiles/graph.dot', status=200)
    assert res.content_type == 'text/vnd.graphviz'
    assert res.text


'''
    Used to generate schema diagrams. The code is in snovault/src/snovault/schema_graph.py. 
'''
def test_graph_svg(testapp):
    res = testapp.get('/profiles/graph.svg', status=200)
    assert res.content_type == 'image/svg+xml'
    assert res.text
