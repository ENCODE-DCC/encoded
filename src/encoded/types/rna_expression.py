from pyramid.security import DENY_ALL
from snovault import collection
from snovault import load_schema

from .base import Item


@collection(
    name='rna-expressions',
    acl=[
        DENY_ALL,
    ]
)
class RNAExpression(Item):
    item_type = 'rna-expression'
    schema = load_schema('encoded:schemas/rna_expression.json')
