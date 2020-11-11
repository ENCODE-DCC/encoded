from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)


@collection(
    name='publications',
    unique_key='publication:identifier',
    properties={
        'title': 'Publications',
        'description': 'Publication pages',
    })
class Publication(Item):
    item_type = 'publication'
    schema = load_schema('encoded:schemas/publication.json')
    embedded = [
        'award'
    ]
    rev = {
        'datasets': ('Dataset','references')
    }

    def unique_keys(self, properties):
        keys = super(Publication, self).unique_keys(properties)
        if properties.get('identifiers'):
            keys.setdefault('alias', []).extend(properties['identifiers'])
        return keys


    @calculated_property(condition='authors', schema={
        "title": "Citation",
        "description": "The short citation used to reference this paper.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string"
    })
    def citation(self, registry, authors, publication_year):
        first_author = authors.split(',')[0]
        firstauth_lastname = first_author.split(' ')[-1]
        if publication_year:
            return firstauth_lastname + ' et al. ' + str(publication_year)
        else:
            return firstauth_lastname + ' et al.'


    @calculated_property(schema={
        "title": "Datasets",
        "description": "The Datasets that are used in this Publication.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Dataset.references",
        },
        "notSubmittable": True,
    })
    def datasets(self, request, datasets):
        return paths_filtered_by_status(request, datasets)
