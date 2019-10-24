Making changes to encoded schemas
=========================

This document describes how to make changes to the JSON schemas ([JSONSchema], [JSON-LD]) and source code that describes the encoded metadata model. For overview of code organization see [overview.rst].

Guide to where to edit Source Code
----------------

* **src** directory - contains all the python and javascript code for front and backends
    * **audit** - contains python scripts that check json objects' metadata stored in the schema.
    * **schemas** - JSON schemas ([JSONSchema], [JSON-LD]) describing allowed types and values for all metadata objects
    * **tests** - Unit and integration tests
    * **types** -  business logic for dispatching URLs and producing the correct JSON
    * **upgrade** - python instructions for upgrading old objects to match the new schema
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

There are two situations we need to consider when updating an existing schema: (1) No update of the schema version (2) Update schema version

### No update of the schema version

* Schema version should not to be updated if the change introduced is not going to cause a potential invalidation of the existing objects in the database. For example an addition of a new enum value to a list of existing enums can not cause schema invalidation, but will simply extend the list of potential values to choose from.

**Follow the steps as outlined below**

1. In the **schemas** directory, edit the existing properties in the corresponding JSON file named after the object.

2. In the **types** directory, make appropriate updates to object class by adding *embedding*, *reverse links*, and *calculated properties* as necessary.

3. Update the inserts within the **data/inserts** directory.

4. Add test in the **tests** directory to make sure your schema change functions as expected. For example, if we included a minor change in treatment object such that *μg/kg* could be specified as treatment units, the following test should allow one to test whether the update has been successfully implemented or not:

        def test_treatment_patch_amount_units(testapp, treatment):
            testapp.patch_json(
            treatment['@id'],
            {
                'treatment_type': 'injection',
                'amount': 20,
                'amount_units': 'μg/kg'
            },
            status=200, 
            ## Status 200 means the object was a successfully patched and the schema update works as expected.
        )

5. Document the changes to the corresponding log file within the **schemas/changelogs** directory. For example, a minor change in the treatment object after version 11 that allowed one to use *μg/kg* as treatment units is shown below:

        ### Minor changes since schema version 11

        * *μg/kg* can now be specified as amount units.

### Update schema version
* Schema version has to be updated (bumped up by 1) if the change that is being introduced will lead to a potential invalidation of existing objects in the database. 

* Examples include:
    1) Changing the name of a property in the existing schema.
    2) Removing a property from the existing schema.
    3) A property that previously allowed free text is now changed to a possible list of allowed enums.
    4) If an existing enum is removed from a property.


* Most of the cases described above are examples where there will be a potential conflict for all the existing objects to be validated under the new schema. Hence, an additional step of adding an upgrader script will be required. This will ensure that all the existing objects will be changed such that they can fit into the new schema that is currently being implemented.

* One more case needs a mention here: When adding multiple new schema properties that would lead to substantial changes within an existing schema, one must update the schema version. Even though, the addition of multiple new schema properties is not going to invalidate any existing objects, it would be useful to do so. Particularly, this will be helpful to all the submitters and users who are trying to use these properties either to submit their data or while querying the database using scripts.

**Follow the steps as outlined below**

1. In the **schemas** directory, edit the existing properties in the corresponding JSON file named after the object and increment the schema version. One of the possible enums for for the genetic modifications object was "validation" up until schema version 6. As a part of schema version upate to 7, "validation" was removed and instead the term "characterization" was added.

        "purpose":{
            "title": "Purpose",
            "description": "The purpose of the genetic modification.",
            "type": "string",
            "enum": [
                "activation",
                "analysis",
                "overexpression",
                "repression",
                "tagging",
                "validation",
                "screening",
                "expression"
            ]
        },
        # Changing validation to characterization as a list of enums within the purpose property:
        "purpose":{
            "title": "Purpose",
            "description": "The purpose of the genetic modification.",
            "type": "string",
            "enum": [
                "activation",
                "analysis",
                "overexpression",
                "repression",
                "tagging",
                "characterization",
                "screening",
                "expression"
            ]
        },

2. In the **schemas** directory, edit the existing properties in the corresponding JSON file named after the object and increment the schema version. For example if the original schema version for the genetic modification object being modified was "6", change it to "7" (6->7): 
        
        "schema_version": {
            "default": "7"
        }

2. In the **upgrade** directory add an ```upgrade_step``` to an existing/new python file named after the object. An example to the upgrade step is shown below. Continuing with our example, after the upgrade all the existing objects with that had "purpose" specified to be "validation" must now be changed to "characterization". And since the schema is changing from version 6 to 7 the def must specify this (6->7):

        @upgrade_step('genetic_modification', '6', '7')
        def genetic_modification_6_7(value, system):
            if value['purpose'] == 'validation':
                value['purpose'] = 'characterization'

3. In the **tests/data/inserts** directory, we will need to change all the corresponding objects to follow the new schema. Continuing with our example, all the ```"purpose": "validation"``` must now be converted to ```"purpose": "characterization"```. So, we need to change all the corresponding inserts within the genetic modification object. For example:

        #Schema version 6
        "purpose": "validation",

        #Owing to schema version 7, the above should be changed to (within the genetic modifications object):
        "purpose": "characterization",

4. Next, add an upgrade test to an existing python file named ```test_upgrade_{metadata_object}.py```. For our example, we will need to edit the ```test_upgrade_genetic_modification.py```. If a corresponding test file doesn't exist, we must create a new file. This example shows the basic structure of setting up ```pytest.fixture``` and upgrade to  ```property_1```:

**General structure to follow**

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
            value = upgrader.upgrade('{metadata_object}', {metadata_object}_2, target_version='3')
            assert value['schema_version'] == '3'
            assert value['property_1'] == 'value 1'

**Specific example from the genetic modifications object upgrade**

        def test_genetic_modification_upgrade_6_7(upgrader, genetic_modification_6):
            value = upgrader.upgrade('genetic_modification', genetic_modification_6,
                             current_version='6', target_version='7')
            assert value['schema_version'] == '7'
            assert value.get('purpose') == 'characterization'

5. You must check the results of your upgrade on the current database:
   
   **note** it is possible to write a "bad" upgrade that does not prevent your objects from loading or being shown.
   
   You can check using the following methods:
   * Checking for errors in the /var/log/cloud-init-output.log (search for "batchupgrade" a few times) in any demo with your upgrade, this can be done about 30min after launch (after machine reboots post-install), no need to wait for the indexing to complete.
   * Looking at the JSON for an object that should be upgraded by checking it's schema_version property.
   * Updating and object and looking in the /var/log/apache2/error.log for stack traces.
   
   It is also possible that an upgrade can be clean under a current database but new objects POSTed before release are broken, so it will be checked again during release.

6. If applicable you may need to update audits on the metadata. Please refer to [making_audits]

7. To document all the schema changes that occurred between increments of the ```schema_version``` update the object changelogs the **schemas/changelogs** directory. Continuing with our example of upgrading genetic modifications object, the changelog for this upgrade would look like the following:

        ### Schema version 7

        * *purpose* property *validation* was renamed to *characterization*

     

[JSONSchema]: http://json-schema.org/
[JSON-LD]:  http://json-ld.org/
[overview.rst]: ../../../docs/overview.rst
[object-lifecycle.rst]: ../../../docs/object-lifecycle.rst
[making_audits]: making_audits.md
