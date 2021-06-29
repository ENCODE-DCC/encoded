from pyramid.security import DENY_ALL
from snovault import collection
from snovault import load_schema

from .base import Item


@collection(
    name='expressions',
    acl=[
        DENY_ALL,
    ]
)
class Expression(Item):
    item_type = 'expression'
    schema = load_schema('encoded:schemas/expression.json')
