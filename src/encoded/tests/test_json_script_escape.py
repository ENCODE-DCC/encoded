import pytest

BAD_STRINGS = [
    '</script>',
    '&gt;',
    '&#62;',
    '<![CDATA[ data ]]>',  # xml.etree fails on ']]>' so escape '>'
    '<!-- comment -->',
    '<!DOCTYPE html>',
    '<?xml processing instruction ?>',
    '<![ decl ]>',
]

HTML = (
    '<html><body>'
    '<script type="application/json">%s</script>'
    '</body></html>'
)


@pytest.mark.parametrize('string', BAD_STRINGS)
def test_escape_load(string):
    import json
    from ..json_script_escape import json_script_escape
    escaped = json_script_escape(json.dumps(string))

    assert '<' not in escaped
    assert '>' not in escaped
    assert '&' not in escaped
    assert json.loads(escaped) == string


@pytest.mark.parametrize('string', BAD_STRINGS)
def test_xml_parsed(string):
    import json
    from ..json_script_escape import json_script_escape
    escaped = json_script_escape(json.dumps(string))
    html = HTML % escaped

    from xml.etree import ElementTree as etree
    assert etree.fromstring(html)[0][0].text == escaped


@pytest.mark.parametrize('string', BAD_STRINGS)
def test_html_parsed(string):
    import json
    from ..json_script_escape import json_script_escape
    escaped = json_script_escape(json.dumps(string))
    html = HTML % escaped

    from HTMLParser import HTMLParser

    class CheckHTML(HTMLParser):
        data = None
        def handle_data(self, data):
            assert self.data is None
            self.data = data

        def raise_error(self, arg):
            raise AssertionError('Should not be here')
 
        handle_entityref = handle_charref = handle_comment = raise_error
        handle_decl = handle_pi = unknown_decl = raise_error

    parser = CheckHTML()
    parser.feed(html)
    parser.close()

    assert parser.data == escaped
