Making changes to encoded schemas
=========================

This document describes how to make changes to the JSON schemas ([JSONSchema], [JSON-LD]) and source code that describes the encoded metadata model.  For overview of code organization see [overview.rst].

Guide to where to edit Source Code
----------------

* **src** directory - contains all the python and javascript code for front and backends
    * **audit** - python instructions for checking metadata stored in the schema
    * **schemas** - JSON schemas ([JSONSchema], [JSON-LD]) describing allowed types and values for all metadata objects
    * **tests** - Unit and integration tests
    * **types** -  business logic for dispatching URLs and producing the correct JSON
    * **upgrade** - python instructions for upgrading old objects stored to the latest 
    * **loadxl.py** - python script that defines the schema objects to load


-----

Adding a new schema
----------------

1. To add a new schema navigate to the **schemas** directory and make a new JSON file named after the object. Populate the file with basic schema definition:


            {
                "title": {Metadata Object},
                "description": "Description of the metadata that this object aims to capture.",
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
Refer to [object-lifecycle.rst] to understand object rendering. Example of basic collection definition for treatments::

    
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

    * *Embedding* - specifying the properties embeded in the object when specifying ```frame=object```, for construct we have:

                embedded = ['target']

    * *Reverse links* - specifying the links that are back calculated from an object that ```linkTo``` this object, for file we have:

                rev = {
                    'paired_with': ('File', 'paired_with'),
                    'quality_metrics': ('QualityMetric', 'quality_metric_of'),
                    'superseded_by': ('File', 'supersedes'),
                }

    * *Calculated properties* - dynamically calculated before rendering of an object, for platforms we calculate the title:

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

7. Add in sample data to test the new schema in **tests** directory. Create a new JSON file in the **data/inserts** directory named after the new metadata object. 
This new object is an array of example objects that can successfully POST against the schema defined, for example ::

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

8. If applicable you may want to add audits on the metadata. Please refer to [making_audits]

-----

Updating an existing schema
----------------

There are 2 categories when we talk about updating an existing schema:

* No affect on schema version
* Update schema version


**The schema version is updated, requiring an upgrade of the schema, when the objects stored in the database will not validate and POST to the updated schema.**


### No affect on schema version

1. In the **schemas** directory, make edits  to properties in the JSON file named after the object.

2. In the **types** directory, make appropriate updates to object class by adding *embedding*, *reverse links*, and *calculated properties* as necessary.

3. Update sample data, **data/inserts** directory, to test the changes made to the schema in **tests** directory. 


### Update schema version

1. In the **schemas** directory, increment the schema version (1->2), if it meets the above rule: 
        
        "schema_version": {
            "default": "2"
        }

2. In the **upgrade** directory add an ```upgrade_step``` to an existing/new python file named after the object. An example upgrades the object from schema version (2->3):

        @upgrade_step('{metadata_object}', '2, '3')
        def {metadata_object}_2_3(value, system):
            # {Redmine Issue}

            # lowercase all values in property 1
            if 'property_1' in value:
                value['property_1'] = value['property_1'].lower()

3.  In the **tests** directory add upgrade test to an existing/new python file named ```test_upgrade_{metadata_object}.py```. This example shows the basic structure of setting up ```pytest.fixture``` and upgrade to  ```property_1```:


        @pytest.fixture
        def {metadata_object}():
            return{
                "property_1": "Value 1",
                "property_2": 10,         
            }


        @pytest.fixture
        def {metadata_object}_2({metadata_object}):
            item = {metadata_object}.copy()
            item.update({
                'schema_version': '2',
            })
            return item


        def test_{metadata_object}_lowercase_property_1(app, {metadata_object}_2):
            migrator = app.registry['migrator']
            value = migrator.upgrade('{metadata_object}', {metadata_object}_2, target_version='3')
            assert value['schema_version'] == '3'
            assert value['property_1'] == 'value 1'
            
5. You must check the results of your upgrade on the current database:
   
   **note** it is possible to write a "bad" upgrade that does not prevent your objects from loading or being shown.
   
   You can check using the following methods:
   * Checking for errors in the /var/log/cloud-init-output.log (search for "batchupgrade" a few times) in any demo with your upgrade, this can be done about 30min after launch (after machine reboots post-install), no need to wait for the indexing to complete.
   * Looking at the JSON for an object that should be upgraded by checking it's schema_version property.
   * Updating and object and looking in the /var/log/apache2/error.log for stack traces.
   
   It is also possible that an upgrade can be clean under a current database but new objects POSTed before release are broken, so it will be checked again during release.

6. If applicable you may need to update audits on the metadata. Please refer to [making_audits]

7. To document all the schema changes that occurred between increments of the ```schema_version``` update the object changelogs the **schemas/changelogs** directory. Below is an example of the changelog for above upgrade:

    Schema version 2
    ----------------

    * *property_1* values were changed to all lower case
     

[JSONSchema]: http://json-schema.org/
[JSON-LD]:  http://json-ld.org/
[overview.rst]: ../../../docs/overview.rst
[object-lifecycle.rst]: ../../../docs/object-lifecycle.rst
[making_audits]: making_audits.md
