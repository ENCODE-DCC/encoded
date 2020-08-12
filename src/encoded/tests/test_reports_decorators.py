import pytest

from encoded.tests.features.conftest import app, app_settings, index_workbook
from pyramid.exceptions import HTTPBadRequest


def test_reports_decorators_allowed_types_decorator_raises_error():
    from encoded.reports.decorators import allowed_types

    @allowed_types(['MyType'])
    def endpoint(context, request):
        return True

    class Request:
        def __init__(self, params):
            self.params = params

    context = {}
    request = Request({})
    with pytest.raises(HTTPBadRequest) as error:
        endpoint(context, request)
    assert str(error.value) == 'URL requires one type parameter.'
    request = Request({'type': 'WrongType'})
    with pytest.raises(HTTPBadRequest) as error:
        endpoint(context, request)
    assert str(error.value) == 'WrongType not a valid type for endpoint.'
    request = Request({'type': 'MyType'})
    assert endpoint(context, request)


def test_reports_metadata_view_unallowed_type(index_workbook, testapp):
    testapp.get('/metadata/?type=File', status=400)


def test_reports_batch_download_view_unallowed_type(index_workbook, testapp):
    testapp.get('/batch_download/?type=File', status=400)
