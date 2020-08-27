from functools import wraps
from pyramid.exceptions import HTTPBadRequest
from snovault.elasticsearch.searches.parsers import QueryString


def allowed_types(types):
    def decorator(func):
        @wraps(func)
        def wrapper(context, request):
            qs = QueryString(request)
            type_filters = qs.get_type_filters()
            if len(type_filters) != 1:
                raise HTTPBadRequest(
                    explanation='URL requires one type parameter.'
                )
            if type_filters[0][1] not in types:
                raise HTTPBadRequest(
                    explanation=f'{type_filters[0][1]} not a valid type for endpoint.'
                )
            return func(context, request)
        return wrapper
    return decorator
