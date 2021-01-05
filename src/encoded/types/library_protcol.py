from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
)


@collection(
    name='library-protocols',
    unique_key='library_protocol:name',
    properties={
        'title': 'Library protocols',
        'description': 'Listing of Library protocols',
    })
class LibraryProtocol(Item):
    item_type = 'library_protocol'
    schema = load_schema('encoded:schemas/library_protocol.json')
    name_key = 'name'


    @calculated_property(define=True,
                         schema={"title": "Required files",
                                 "description": "The sequence file types required for a SequencingRun of a Library from this protocol.",
                                 "comment": "Do not submit. This is a calculated property",
                                 "type": "array",
                                 "items": {
                                    "type": "string"
                                    }
                                })
    def required_files(self, request, sequence_file_standards=None):
        req_fs = []
        if sequence_file_standards:
            for f in sequence_file_standards:
                if f.get('required') == True:
                    req_fs.append(f.get('read_type'))
            return req_fs
