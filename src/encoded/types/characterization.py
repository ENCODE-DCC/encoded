from snovault import (
    abstract_collection,
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    SharedItem,
    ALLOW_LAB_SUBMITTER_EDIT,
    ALLOW_CURRENT,
    DELETED,
)
from snovault.attachment import ItemWithAttachment
from pyramid.security import (
    Allow,
)
from pyramid.traversal import (
    find_root,
)
ALLOW_REVIEWER_EDIT = [
    (Allow, 'role.lab_reviewer', 'edit'),
    (Allow, 'role.lab_reviewer', 'review')
] + ALLOW_LAB_SUBMITTER_EDIT


@abstract_collection(
    name='characterizations',
    properties={
        'title': "Characterizations",
        'description': 'Listing of all types of characterization.',
    })
class Characterization(ItemWithAttachment, Item):
    base_types = ['Characterization'] + Item.base_types
    embedded = ['lab', 'award', 'submitted_by']
    set_status_up = [
        'documents',
    ]
    set_status_down = []
    

    def __ac_local_roles__(self):
        roles = {}
        properties = self.upgrade_properties().copy()
        if 'lab' in properties:
            lab_submitters = 'submits_for.%s' % properties['lab']
            roles[lab_submitters] = 'role.lab_submitter'
        if 'review' in properties:
            reviewing_lab = properties['review'].get('lab')
            if reviewing_lab is not None:
                lab_reviewers = 'submits_for.%s' % reviewing_lab
                roles[lab_reviewers] = 'role.lab_reviewer'
        if 'award' in properties:
            root = find_root(self)
            award = root.get_by_uuid(properties['award'])
            viewing_group = award.upgrade_properties().get('viewing_group')
            if viewing_group is not None:
                viewing_group_members = 'viewing_group.%s' % viewing_group
                roles[viewing_group_members] = 'role.viewing_group_member'
        return roles


@collection(
    name='donor-characterizations',
    properties={
        'title': 'Donor characterizations',
        'description': 'Listing of model organism donor (strain) construct characterizations',
    })
class DonorCharacterization(Characterization):
    item_type = 'donor_characterization'
    schema = load_schema('encoded:schemas/donor_characterization.json')


@collection(
    name='biosample-characterizations',
    properties={
        'title': 'Biosample characterizations',
        'description': 'Listing of biosample characterizations',
    })
class BiosampleCharacterization(Characterization):
    item_type = 'biosample_characterization'
    schema = load_schema('encoded:schemas/biosample_characterization.json')
    STATUS_ACL = {
        'released': ALLOW_CURRENT,
        'in progress': ALLOW_REVIEWER_EDIT,
        'deleted': DELETED,
    }

@collection(
    name='antibody-characterizations',
    properties={
        'title': 'Antibody characterizations',
        'description': 'Listing of antibody characterization documents',
    })
class AntibodyCharacterization(Characterization, SharedItem):
    item_type = 'antibody_characterization'
    schema = load_schema('encoded:schemas/antibody_characterization.json')
    embedded = [
        'characterization_reviews.biosample_ontology',
        'submitted_by',
        'lab',
        'award',
        'target',
        'target.organism',
        'documents',
        'characterizes.targets',
    ]
    audit_inherit = [
        'characterization_reviews.biosample_ontology',
    ]

    @calculated_property(schema={
        "title": "Characterization method",
        "type": "string",
    })
    def characterization_method(self, primary_characterization_method=None,
                                secondary_characterization_method=None):
        return primary_characterization_method or secondary_characterization_method


@collection(
    name='genetic-modification-characterizations',
    properties={
        'title': 'Genetic modification characterizations',
        'description': 'Listing of genetic modifications characterizations',
    })
class GeneticModificationCharacterization(Characterization):
    item_type = 'genetic_modification_characterization'
    schema = load_schema('encoded:schemas/genetic_modification_characterization.json')
    STATUS_ACL = {
        'released': ALLOW_CURRENT,
        'in progress': ALLOW_REVIEWER_EDIT,
        'deleted': DELETED,
    }