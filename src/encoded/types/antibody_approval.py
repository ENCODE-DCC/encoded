from snovault import (
    collection,
    load_schema,
)
from snovault.resource_views import (
    item_view,
    item_view_page,
)
from .base import (
    DELETED,
    Item,
)
from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPMovedPermanently,
)
from pyramid.security import (
    NO_PERMISSION_REQUIRED,
)
from pyramid.view import (
    view_config,
)


@collection(
    name='antibody-approvals',
    properties={
        'title': 'Antibody Approvals',
        'description': 'Listing of characterization approvals for ENCODE antibodies',
    })
class AntibodyApproval(Item):
    schema = load_schema('encoded:schemas/antibody_approval.json')
    item_type = 'antibody_approval'
    embedded = [
        'antibody',
        'award',
        'award.pi',
        'award.pi.lab',
        'lab',
        'target',
        'target.organism',
        'submitted_by',
        'characterizations.award',
        'characterizations.lab',
        'characterizations.submitted_by',
        'characterizations.target.organism',
        ]

    __acl__ = DELETED

    def unique_keys(self, properties):
        keys = super(AntibodyApproval, self).unique_keys(properties)
        value = u'{antibody}/{target}'.format(**properties)
        keys.setdefault('antibody_approval:lot_target', []).append(value)
        return keys


@view_config(context=AntibodyApproval, permission=NO_PERMISSION_REQUIRED,
             request_method='GET', name='page')
def antibody_approval_page_view(context, request):
    if 'antibodies' in request.traversed:
        obj = request.embed(request.resource_path(context), '@@object')
        qs = request.query_string
        location = obj['antibody'] + ('?' if qs else '') + qs
        raise HTTPMovedPermanently(location=location)
    if request.has_permission('view'):
        return item_view_page(context, request)
    raise HTTPForbidden()


@view_config(context=AntibodyApproval, permission=NO_PERMISSION_REQUIRED,
             request_method='GET')
def antibody_approval_view(context, request):
    # XXX Should item_view be registered with NO_PERMISSION_REQUIRED?
    return item_view(context, request)
