from snovault import (
    abstract_collection,
    collection,
    load_schema,
)
from .base import (
    Item,
)


@abstract_collection(
    name='validation-techniques',
    properties={
        'title': "Validation techniques",
        'description': 'Listing of all types of element validation techniques.'
    })
class ValidationTechnique(Item):
    base_types = ['ValidationTechnique'] + Item.base_types


@collection(
    name='mpras',
    properties={
        'title': "Massively parallel reporter assays for element validation",
        'description': 'Listing of all element validations using MPRA techniques.'
    })
class Mpra(ValidationTechnique):
    item_type = 'mpra'
    schema = load_schema('encoded:schemas/mpra.json')


@collection(
    name='transgenic-organisms',
    properties={
        'title': "Transgenic organisms for element validation",
        'description': 'Listing of all element validations using transgenic organisms.'
    })
class TransgenicOrganism(ValidationTechnique):
    item_type = 'transgenic_organism'
    schema = load_schema('encoded:schemas/transgenic_organism.json')
    embedded = [
        'biosample',
        'biosample.model_organism_donor_modifications',
        'biosample.model_organism_donor_modifications.award',
        'biosample.model_organism_donor_modifications.lab',
        'biosample.model_organism_donor_modifications.modification_techniques',
        'biosample.model_organism_donor_modifications.treatments',
        'biosample.model_organism_donor_modifications.target',
        'biosample.donor',
        'biosample.donor.mutated_gene',
        'biosample.donor.organism',
        'biosample.donor.characterizations',
        'biosample.donor.characterizations.award',
        'biosample.donor.characterizations.lab',
        'biosample.donor.characterizations.submitted_by',
        'biosample.donor.documents',
        'biosample.donor.documents.award',
        'biosample.donor.documents.lab',
        'biosample.donor.documents.submitted_by',
        'biosample.donor.references'
    ]
