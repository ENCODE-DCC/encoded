from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
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

    def unique_keys(self, properties):
        keys = super(Publication, self).unique_keys(properties)
        if properties.get('identifiers'):
            keys.setdefault('alias', []).extend(properties['identifiers'])
        return keys


    @calculated_property(condition='authors', schema={
        "title": "Citation",
        "type": "string"
    })
    def citation(self, registry, authors, publication_year):
        first_author = authors.split(',')[0]
        firstauth_lastname = first_author.split(' ')[-1]
        if publication_year:
            return firstauth_lastname + ' et al. ' + str(publication_year)
        else:
            return firstauth_lastname + ' et al.'
