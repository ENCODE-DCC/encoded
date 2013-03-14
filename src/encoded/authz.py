from sqlalchemy.orm.exc import NoResultFound
from .storage import (
    DBSession,
    UserMap,
    )


def groupfinder(login, request):
    session = DBSession()
    query = session.query(UserMap).filter(UserMap.login == login)
    try:
        query.one()
        return ['g:admin']  # return ['g:%s' % g for g in user.groups]
    except NoResultFound:
        return None
