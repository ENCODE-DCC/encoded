from pyramid.view import view_config


def includeme(config):
    config.scan('.')


@view_config(name='testing-user', request_method='GET')
def user(request):
    from pyramid.security import (
        authenticated_userid,
        effective_principals,
    )
    return {
        'authenticated_userid': authenticated_userid(request),
        'effective_principals': effective_principals(request),
    }
