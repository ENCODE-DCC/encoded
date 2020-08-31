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
    name='sequencing-runs',
    properties={
        'title': 'Sequencing Runs',
        'description': 'Listing Sequuencing runs',
    })
class SequencingRun(Item):
    item_type = 'sequencing_run'
    schema = load_schema('encoded:schemas/sequencing_run.json')
    rev = {
        'files': ('RawSequenceFile', 'derived_from')
    }


    @calculated_property(schema={
        "title": "Files",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "RawSequenceFile",
        },
    })
    def files(self, request, files):
        return paths_filtered_by_status(request, files)


    @calculated_property(schema={
            "title": "Read 1 file",
            "type": "string",
            "linkFrom": "RawSequenceFile.derived_from",
            "notSubmittable": True,
    })
    def read_1_file(self, request, registry, files):
        for file_id in files:
            file_obj = request.embed(file_id, '@@object')
            read_type = file_obj.get('read_type')
            if read_type == 'Read 1':
                return file_obj['accession']


    @calculated_property(schema={
            "title": "Read 2 file",
            "type": "string",
            "linkFrom": "RawSequenceFile.derived_from",
            "notSubmittable": True,
    })
    def read_2_file(self, request, registry, files):
        for file_id in files:
            file_obj = request.embed(file_id, '@@object')
            read_type = file_obj.get('read_type')
            if read_type == 'Read 2':
                return file_obj['accession']


    @calculated_property(schema={
            "title": "Read 1N file",
            "type": "string",
            "linkFrom": "RawSequenceFile.derived_from",
            "notSubmittable": True,
    })
    def read_1N_file(self, request, registry, files):
        for file_id in files:
            file_obj = request.embed(file_id, '@@object')
            read_type = file_obj.get('read_type')
            if read_type == 'Read 1N':
                return file_obj['accession']


    @calculated_property(schema={
            "title": "Read 2N file",
            "type": "string",
            "linkFrom": "RawSequenceFile.derived_from",
            "notSubmittable": True,
    })
    def read_2N_file(self, request, registry, files):
        for file_id in files:
            file_obj = request.embed(file_id, '@@object')
            read_type = file_obj.get('read_type')
            if read_type == 'Read 2N':
                return file_obj['accession']


    @calculated_property(schema={
            "title": "i5 index file",
            "type": "string",
            "linkFrom": "RawSequenceFile.derived_from",
            "notSubmittable": True,
    })
    def i5_index_file(self, request, registry, files):
        for file_id in files:
            file_obj = request.embed(file_id, '@@object')
            read_type = file_obj.get('read_type')
            if read_type == 'i5 index':
                return file_obj['accession']


    @calculated_property(schema={
            "title": "i7 index file",
            "type": "string",
            "linkFrom": "RawSequenceFile.derived_from",
            "notSubmittable": True,
    })
    def i7_index_file(self, request, registry, files):
        for file_id in files:
            file_obj = request.embed(file_id, '@@object')
            read_type = file_obj.get('read_type')
            if read_type == 'i7 index':
                return file_obj['accession']
