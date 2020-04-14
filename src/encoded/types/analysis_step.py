from snovault import (
    collection,
    calculated_property,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)
from pyramid.traversal import (
    find_root,
)


@collection(
    name='analysis-steps',
    unique_key='analysis_step:name',
    properties={
        'title': 'Analysis steps',
        'description': 'Listing of Analysis Steps',
    })
class AnalysisStep(Item):
    item_type = 'analysis_step'
    schema = load_schema('encoded:schemas/analysis_step.json')
    rev = {}
    embedded = [
        'parents'
    ]

    def unique_keys(self, properties):
        keys = super(AnalysisStep, self).unique_keys(properties)
        keys.setdefault('analysis_step:name', []).append(self._name(properties))
        return keys

    @calculated_property(schema={
        "title": "Name",
        "type": "string",
        "description": "Full name of the analysis step with major version number.",
        "comment": "Do not submit. Value is automatically assigned by the server.",
        "uniqueKey": "name"
    })
    def name(self):
        return self.__name__

    @property
    def __name__(self):
        properties = self.upgrade_properties()
        return self._name(properties)

    def _name(self, properties):
        return u'{}-v-{}'.format(properties['step_label'], properties['major_version'])

