Making changes to encoded schemas
=========================

This document describes how to make changes to the JSON schemas ([JSONSchema], [JSON-LD]) and source code that describes the encoded metadata model. For overview of code organization see [overview.rst].

Guide to where to edit Source Code
----------------

* **src** directory - contains all the python and javascript code for front and backends
    * **audit** - contains python scripts that check json objects' metadata stored in the schema
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


2. Add appropriate properties in the "properties" block. Example of different property types:

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


3. Identify all required properties to make an object and add to the "required" array, for treatment we have.


            "required": ["treatment_term_name", "treatment_type"]


4. In the **types** directory add a collection class for the object to define the rendering of the object. 
Refer to [object-lifecycle.rst] to understand object rendering. Example of basic collection definition for treatments:

    
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

6. In ``loadxl.py`` add the new metadata object into the ```Order``` array, for example to add new object ```train.json```.

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
This new object is an array of example objects that can successfully POST against the schema defined, for example:

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

**When not to update a version**

* Do not update the schema version if the updated schema allows all existing objects in the database to continue to validate. For example, a new enum value in an existing list of enums would not cause existing objects of that type to fail validation. 

**NOTE:** 
Exception: When making substantial changes to an existing schema, even if these changes do not cause the existing objects using this schema to fail validation, an update is recommended (please see below).

**When to update a version**

* Schema version has to be updated (bumped up by 1) if the change that is being introduced will lead to a potential invalidation of existing objects in the database. 

* Examples include:
    1) Changing the name of a property in the existing schema.
    2) Removing a property from the existing schema.
    3) A property that previously allowed free text is now changed to a possible list of allowed enums.
    4) Removing an enum from an existing property.

* Most of the cases described above are examples where existing objects could potentially fail the validation under the new schema version. Hence, an additional step of adding an upgrade script is required. This will ensure that all the existing objects will be upgraded (changed) such that they will be valid under the new schema version.

* **NOTE:** You should update the schema version when making substantial changes to an existing schema even if these changes do not cause existing objects using this schema to fail validation.
The new schema version number in such cases helps submitters and users realize that a substantial change has been made to the schema and they may need to update their scripts accordingly.

* **NOTE:** Whenever in doubt (whether to update or not), it would be a good idea to discuss with other members of the group as there can be grey areas as mentioned in the note above. When multiple new properties are being added to the new schema (potentially leading to no conflict with the schema validation), technically the upgrade step would just be bumping the schema version.

**Some detailed steps to follow in each of the above cases are outlined below**

### No update of the schema version

1. In the **schemas** directory, edit the existing properties in the corresponding JSON file named after the object.

2. In the **types** directory, make appropriate updates to object class by adding *embedding*, *reverse links*, and *calculated properties* as necessary.

3. Update the inserts within the **data/inserts** directory.

4. Add test in the **tests** directory to make sure your schema change functions as expected. 

**Specific example from the treatment object schema change:**
For example, if we included a minor change in treatment object such that *μg/kg* could be specified as treatment units, the following test should allow one to test whether the update has been successfully implemented or not:

        def test_treatment_patch_amount_units(testapp, treatment):
            testapp.patch_json(
            treatment['@id'],
            {
                'treatment_type': 'injection',
                'amount': 20,
                'amount_units': 'μg/kg'
            },
            status=200, 
            ## Status 200 means the object was successfully patched and the schema update works as expected.
        )

5. Document the changes to the corresponding log file within the **schemas/changelogs** directory. 

**Specific example from the treatment object schema change:**
For example, a minor change in the treatment object after version 11 that allowed one to use *μg/kg* as treatment amount units is shown below:

        ### Minor changes since schema version 11

        * *μg/kg* can now be specified as amount units.

### Update schema version

1. In the **schemas** directory, edit the existing properties in the corresponding JSON file named after the object and increment the schema version. 

**Specific example from the genetic modifications object schema change:**

Up until schema version 6 for the genetic modifications object, "validation" was an enum for the "purpose" property. As a part of schema version update to 7, "validation" was removed and instead the term "characterization" was added.


        "purpose":{
            "title": "Purpose",
            "description": "The purpose of the genetic modification.",
            "type": "string",
            "enum": [
                "activation",
                "validation",
                "expression"
            ]
        },

Replacing the enum "validation" by the enum "characterization" in the list of enums of the "purpose" property:

        "purpose":{
            "title": "Purpose",
            "description": "The purpose of the genetic modification.",
            "type": "string",
            "enum": [
                "activation",
                "characterization",
                "expression"
            ]
        },

2. In the **schemas** directory, edit the properties in the corresponding JSON file named after the object and increment the schema version..

**Specific example from the genetic modifications object upgrade:**

For example if the original schema version for the genetic modification object being modified was "6", change it to "7" (6->7): 
        
        "schema_version": {
            "default": "7"
        }

3. In the **upgrade** directory add an ```upgrade_step``` to a python file named after the object (create new if there is no such a file in the upgrade directory). For some objects the upgrade is defined in the parent class - like dataset.py for the experiment object.

**Specific example from the genetic modifications object upgrade:**

An example to the upgrade step is shown below. Continuing with our example on genetic modifications, all the existing objects with that had "purpose" specified to be "validation" must now be changed to "characterization". 

        @upgrade_step('genetic_modification', '6', '7')
        def genetic_modification_6_7(value, system):
            if value['purpose'] == 'validation':
                value['purpose'] = 'characterization'

4. In the **tests/data/inserts** directory, we will need to change all the corresponding objects to follow the new schema. 

**Specific example from the genetic modifications object upgrade:**

Continuing with our example, all the ```"purpose": "validation"``` must now be converted to ```"purpose": "characterization"```. Change all the corresponding inserts within the genetic modifications object. For example:

#genetic_modification insert **before** the change from schema version 6 to 7:

        "purpose": "validation",


#genetic_modification insert **after** the change from schema version 6 to 7:

        "purpose": "characterization",


5. Next, add an upgrade test to an existing python file named ```test_upgrade_{metadata_object}.py```. If a corresponding test file doesn't exist, create a new file. 

**Specific example from the genetic modifications object upgrade:**

Below, is an example of an upgrade step that must be added to the ```test_upgrade_genetic_modification.py``` script.

        def test_genetic_modification_upgrade_6_7(upgrader, genetic_modification_6):
            value = upgrader.upgrade('genetic_modification', genetic_modification_6,
                             current_version='6', target_version='7')
            assert value['schema_version'] == '7'
            assert value.get('purpose') == 'characterization'

6. You must check the results of your upgrade on the current database:
   
   **Note** it is possible to write a "bad" upgrade that does not prevent your objects from loading or being shown.
   
   You can check using the following methods:
   * Checking for errors in the /var/log/cloud-init-output.log (search for "batchupgrade" a few times) in any demo with your upgrade, this can be done about 30min after launch (after machine reboots post-install), no need to wait for the indexing to complete.
   * Looking at the JSON for an object that should be upgraded by checking it's schema_version property.
   * Updating and object and looking in the /var/log/apache2/error.log for stack traces.
   
   A good upgrade would ensure that all objects POSTed before and after release would not fail validation. Nevertheless, it will be a good idea to check that again during the release.

**Specific example from a successful batch upgrade on a demo:**

You can find upgrade results on a demo at `/var/log/cloud-init-output.log`. Batchupgrade is almost the last step of demo initiation. So you would expect upgrade results at the end of that log. Batchupgrade log starts with the following progress log which is about 1300 lines:
```
INFO [snovault.batchupgrade][MainThread] Start Upgrade with 1272190 items: 1000, 1, 16, 1
INFO [snovault.batchupgrade][MainThread] 1 of ~1272 Batch: Updated 0 of 1000 (errors 0)
INFO [snovault.batchupgrade][MainThread] 2 of ~1272 Batch: Updated 0 of 1000 (errors 0)
INFO [snovault.batchupgrade][MainThread] 3 of ~1272 Batch: Updated 0 of 1000 (errors 0)
...
INFO [snovault.batchupgrade][MainThread] 1271 of ~1272 Batch: Updated 0 of 1000 (errors 0)
INFO [snovault.batchupgrade][MainThread] 1272 of ~1272 Batch: Updated 0 of 1000 (errors 0)
INFO [snovault.batchupgrade][MainThread] 1273 of ~1272 Batch: Updated 0 of 1000 (errors 0)
INFO [snovault.batchupgrade][MainThread] End Upgrade
```

After that you will find a summary of the upgrade which should indicate any potential errors. Since, in the example below, the line ```Sum errors: 0```, everything looks good for this upgrade:

```
INFO [snovault.batchupgrade][MainThread] Upgrade Summary
INFO [snovault.batchupgrade][MainThread] Sum updated: 2
INFO [snovault.batchupgrade][MainThread] Collection cart: Updated 2 of 142 (errors 0)
INFO [snovault.batchupgrade][MainThread] Collection user: Updated 616 of 616 (errors 0)
INFO [snovault.batchupgrade][MainThread] Sum errors: 0
INFO [snovault.batchupgrade][MainThread] Run Time: 11.91 minutes
```
If you do see any errors in the summary above, you must to look at log above and find out what objects failed the upgrade and why.

7. If applicable you may need to update audits on the metadata. Please refer to [making_audits]

8. To document all the schema changes that occurred between increments of the ```schema_version``` update the object changelogs the **schemas/changelogs** directory. 

**Specific example from the genetic modifications object upgrade:**

Continuing with our example of upgrading genetic modifications object, the changelog for this upgrade would look like the following:

        ### Schema version 7

        * *purpose* property enum value *validation* was renamed to *characterization*

     

[JSONSchema]: http://json-schema.org/
[JSON-LD]:  http://json-ld.org/
[overview.rst]: ../../../docs/overview.rst
[object-lifecycle.rst]: ../../../docs/object-lifecycle.rst
[making_audits]: making_audits.md
