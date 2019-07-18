Adding audits
=========================

This document describes how to add and update audits that check metadata consistency and integrity.

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

Adding a new aduit
----------------

1. To add a new audit, navigate to the *audit** directory. Determine what metadata is needed to implement the consistency and integrity check. This helps to determine which object has the appropriate metadata available and where to place the new audit. In the directory make a new python file or edit an exisiting python file named after the determined object.

2. Make a new audit definition, using the metadata needed as a guide to fall into one these 2 categories:
    
    * *Contained in an object* - all metadata need for audit are properties of the object where embedded 
objects referred to by an identifier:
  
        @audit_checker('{metadata_object}', frame='object')
        def audit_new_audit_name(value, system):
            '''
            Description of audit
            '''
            pass

    * *Requires metadata in other objects* - metadata need for audit are properties of the object as well as properoties within embedded objects:
   
        @audit_checker('{metadata_object}', frame=['{linked_object_1}'])
        def audit_new_audit_name(value, system):
            '''
            Description of audit
            '''
            pass

3. Write the logic for the metadata check and determine what the ```AuditFailure``` human readable name when displayed on faceted search and the details of the audit to be displayed. Also determine which of the following 4 categories this audit should fall into:
    
    * *ERROR* - This is wrong no matter what.  Example: term mismatch
    * *NOT COMPLIANT* - This should not be released this way. Example: in progress ChIP experiment with no control
    * *WARNING* - Informational warning.  Example: This library is paired end but the replicate is single end.  
    * *DCC ACTION* - DCC needs to update metadata or code to fix. Example NTRs. 
    
    Example of ```library``` where RNA library should have a size_range specified :
        
        RNAs = ['SO:0000356', 'SO:0000871']
    
        if (value['nucleic_acid_term_id'] in RNAs) and ('size_range' not in value):
            detail = 'RNA library {} requires a value for size_range'.format(audit_link(value['accession'], value['@id']))
            raise AuditFailure('missing size_range', detail, level='ERROR')

    Use ```audit_link``` to format links so that the front end can find and present them. The first parameter is the text to display for the link, while the second is the link path. You must import ```audit_link``` from the .formatter library.

    The .formatter library also includes a ```path_to_text``` utility to help generate link text if all you have is the ```@id```. Pass this ```@id``` to ```path_to_text``` and it returns just the accession portion as text that you can use as link text.

4. In the **tests** directory add audit test to an existing/new python file named ```test_audit_{metadata_object}.py```. This example shows the basic structure of setting up ```pytest.fixture``` and test that ```property_1``` is present if ```property_2``` is RNA:

        @pytest.fixture
        def {metadata_object}_1:
            item = {
                'property_2': 'RNA',
            }
            return testapp.post_json('/{metadata_object}', item, status=201).json['@graph'][0]


        def test_{metadata_object}_property_1(testapp, {metadata_object}_1):
            res = testapp.get({metadata_object}_1['@id'] + '@@index-data')
                errors = res.json['audit']
                errors_list = []
                for error_type in errors:
                    errors_list.extend(errors[error_type])
                assert any(error['category'] == 'missing prperty 1' for error in errors_list)

