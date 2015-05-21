Making changes to encoded schemas
=========================



This document describes how to make changes to the JSON schemas ([JSONSchema], [JSON-LD]) and source code that describes the encoded metadata model.  For overview of code organization see [overview.rst].

Guide to where to edit Source Code
----------------

* *src* directory - contains all the python and javascript code for front and backends
    * *audit* - python instructions for checking metadata stored in the schema
    * *schemas* - JSON schemas ([JSONSchema], [JSON-LD]) describing allowed types and values for all metadata objects
    * *tests* - Unit and integration tests
    * *types* -  business logic for dispatching URLs and producing the correct JSON
    * *upgrade* - python instructions for upgrading old objects stored to the latest 
    * *loadxl.py* - python script that defines the schema objects to load


-----

Adding a new schema
----------------

1. To add a new schema navigate to the **schemas** directory and make a new JSON file named after the object. Populate the file with basic schema definition:


            {
                "title": {Meatadata Object},
                "description": "Description of the metdata that this object aims to capture.",
                "id": "/profiles/{metadata object}.json",
                "$schema": "http://json-schema.org/draft-04/schema#",
                "identifyingProperties": ["uuid"],
                "additionalProperties": false,
                "mixinProperties": [
                    { "$ref": "mixins.json#/schema_version" },
                    { "$ref": "mixins.json#/uuid" }
                ],
                "type": "object",
                "properties": {
                    "schema_version": {
                        "default": "1"
                    }
                }
            }


2. Add appropriate properties in the properties block. Example of different property types:

            {
                "example_string": {
                    "title": "Example string",
                    "description": "An example of a free text property.",
                    "type": "string"
                },
                "example_number": {
                    "title": "Example number",
                    "description": "An example of a free text property.",
                    "type": "integer"
                },
                "example_enum": {
                    "title": "Example enum",
                    "description": "An example of a property with enumerated values.",
                    "type": "string",
                    "enum": [
                        "option 1",
                        "option 2",
                        "option 3"
                    ]
                },
                "example_pattern": {
                    "title": "Example string with pattern",
                    "description": "An example of a property that must match a pattern",
                    "type": "string",
                    "pattern": "^[\\S\\s\\d\\-\\(\\)\\+]+$"
                }
            }


3. Identify all required properties to make an object and add to the "required" array, for treatment we have::


            "required": ["treatment_term_name", "treatment_type"]


4. In the **types** directory add a collection class for the object to define the rendering of the object. 
Refer to object-lifecycle.rst_ to understand object rendering. Example of basic collection definition for treatments::

    
            @collection(
                name='treatments',
                properties={
                    'title': 'Treatments',
                    'description': 'Listing Biosample Treatments',
                }
            )
            class Treatment(Item):
                item_type = 'treatment'
                schema = load_schema('encoded:schemas/treatment.json')


5. Within in a class add in  *embedding*, *reverse links*, and *calculated properties* as necessary.

    * *Embedding* - specificing the properties embeded in the object when specifing ```frame=object```, for construct we have::

                embedded = ['target']

    * *Reverse links* - specifiying the links that are back calculated from an object that ```linkTo``` this object, for construct we have::
    
                rev = {
                    'characterizations': ('construct_characterization', 'characterizes'),
                }

    * *Calculated properties* - dynamically calculated before rendering of an object, for platforms we calculate the title::

                @calculated_property(schema={
                    "title": "Title",
                    "type": "string",
                })
                def title(self, term_name):
                    return term_name

6. In ``loadxl.py`` add the new metadata object into the ```Order``` array, for example to add new object ```train.json```::

            ORDER = [
                'user',
                'award',
                'lab',
                'organism',
                'source',
                ...
                'train',
            ]

7. Add in sample data to test the new schema in *tests* directory. Create a new JSON file in the **data/inserts** directory named after the new metadata object. 
This new object is an array of example objects that can succesfully POST against the schema defined, for example ::

            [
                {
                    "property_1": "value 1",
                    "property_2": 10,
                    "uuid": "1a594ade-218a-4697-9ee1-a3ab50024dfa"
                },
                {
                    "property_1": "value 2",
                    "property_2": 100,
                    "uuid": "0137a084-57af-4f69-b756-d6a920393fde"
                }



[JSONSchema]: http://json-schema.org/
[JSON-LD]:  http://json-ld.org/
[overview.rs]: docs/overview.rst
[object-lifecycle.rst]: docs/object-lifecycle.rst
