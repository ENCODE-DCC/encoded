from pyramid.security import Allow
from pyramid.security import ALL_PERMISSIONS
from sqlalchemy.orm.exc import NoResultFound
from .storage import (
    DBSession,
    CurrentStatement,
    Resource,
    UserMap
    )


class RootFactory(object):
    __acl__ = [
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request


def groupfinder(userid, request):
    session = DBSession()
    query = session.query(UserMap).filter(UserMap.persona_email == userid)
    try:
        query.one()
        return ['g:admin']  # return ['g:%s' % g for g in user.groups]
    except NoResultFound:
        return None
