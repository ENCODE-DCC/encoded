====================
The object lifecycle
====================

Retrieval (GET)
---------------

Data can be retrieved from the database in one of a few "frames" which specify how much data is in the returned object.
The object and embedded frames are indexed in elasticsearch, the page properties are applied at "GET".  Usually you will specify format=json (or set content-type: application/json) if you wish to return a JSON object directly.

* frame=raw

Objects are stored in the DB "raw" - with only the properties that are submitted with links as uuids.

* frame=object

This is the raw object with additional "@properties" (@id, @type) and calculated properties (defined in python code "types" package).  

* frame=embedded

This is the frame=object object with all the embedded properties (also specified in the "types" package)

* frame=page

This is the default object returned if frame is not specified.  It is the frame=embedded object with several UI and form properties added including @context, audit, and actions.


Submission (POST)
----------

POST /biosample::

    {
        "biosample_type": "DNA",
        "biosample_term_id": "UBERON:349829",
        "aliases": ["my-lab:sample1"],
        "award": "my-award",
        "lab": "my-lab",
        "source": "some-source",
        "organism": "human"
    }


Validation
----------


* Does submission conform to schema?
* Structural conformance
* Link resolution
* Value format validation
* Permission checking


Link resolution
---------------

Links are resolved relative to their configured base url, normally their collection.
Absolute paths and UUIDs are also valid, as are aliases and other uniquely identifying properties::

    {
        "award": "fae1bd8b-0d90-4ada-b51f-0ecc413e904d",
        "lab": "b635b4ed-dba3-4672-ace9-11d76a8d03af",
        "source": "1d5be796-8f80-4fd4-b6c7-6674318657eb",
        "organism": "7745b647-ff15-4ff3-9ced-b897d4e2983c"
    }


Default values
--------------

Static and calculated defaults::

    {
        "uuid": "7c245cea-7d59-45fb-9ebe-f0454c5fe950"
        "accession": "ENCBS000TST",
        "date_created": "2014-01-20T10:30:00-0800",
        "status": "IN PROGRESS",
        "submitted_by": "bb319896-3f78-4e24-b6e1-e4961822bc9b"
    }


Storage
-------

Resource record created for uuid with item_type::

    uuid: "7c245cea-7d59-45fb-9ebe-f0454c5fe950"
    item_type: "biosample"


*Raw* properties::

    {
        "biosample_type": "DNA",
        "biosample_term_id": "UBERON:349829",
        "aliases": ["my-lab:sample1"],

        "award": "fae1bd8b-0d90-4ada-b51f-0ecc413e904d",
        "lab": "b635b4ed-dba3-4672-ace9-11d76a8d03af",
        "source": "1d5be796-8f80-4fd4-b6c7-6674318657eb",
        "organism": "7745b647-ff15-4ff3-9ced-b897d4e2983c",

        "accession": "ENCBS000TST",
        "date_created": "2014-01-20T10:30:00-0800",
        "status": "IN PROGRESS",
        "submitted_by": "bb319896-3f78-4e24-b6e1-e4961822bc9b"
    }

Rows are inserted to enforce unique constraints::

    keys: [
        ("accession", "ENCBS000TST"),
        ("alias", "my-lab:sample1"),
    ]

and to maintain referential integrity::

    links: [
        ("award", "fae1bd8b-0d90-4ada-b51f-0ecc413e904d"),
        ("lab", "b635b4ed-dba3-4672-ace9-11d76a8d03af"),
        ("source", "1d5be796-8f80-4fd4-b6c7-6674318657eb"),
        ("organism", "7745b647-ff15-4ff3-9ced-b897d4e2983c"),
        ("submitted_by", "bb319896-3f78-4e24-b6e1-e4961822bc9b"),
    ]

Also:
    * additional property sheets
    * transaction logging
    * object versioning



Rendering
=========

::

    * raw properties
      -> link canonicalization
        -> calculated properties
          -> embedding
            -> page expansion


Link canonicalization
---------------------

Specified in the schema. UUID's are converted to resource paths.
::
    {
        "award": "/awards/my-award/",
        "lab": "/labs/my-lab",
        "source": "/sources/some-source/",
        "organism": "/organisms/human/",
        "submitted_by": "/users/me/",
    }


Calculated properties
---------------------

These include the JSON-LD boilerplate along with other dynamically calculated properties such as a consistently formatted title and reverse links pulled from the links table.
::
    {
        "@id": "/biosamples/ENCBS000TST/",
        "@type": ["biosample", "item"],
        "uuid": "7c245cea-7d59-45fb-9ebe-f0454c5fe950"
        "name": "ENCBS000TST",
        "title": "Biosample ENCBS000TST (human)",
        "characterizations": [],
    }


JSON result
-----------

Combining gives us::

    {
        "biosample_type": "DNA",
        "biosample_term_id": "UBERON:349829",
        "aliases": ["my-lab:sample1"],
        "accession": "ENCBS000TST",
        "date_created": "2014-01-20T10:30:00-0800",
        "status": "IN PROGRESS",

        "award": "/awards/my-award/",
        "lab": "/labs/my-lab",
        "source": "/sources/some-source/",
        "organism": "/organisms/human/",
        "submitted_by": "/users/me/",

        "@id": "/biosamples/ENCBS000TST/",
        "@type": ["biosample", "item"],
        "uuid": "7c245cea-7d59-45fb-9ebe-f0454c5fe950"
        "name": "ENCBS000TST",
        "title": "Biosample ENCBS000TST (human)",
        "characterizations": [],
    }


This is the representation returned within the POST/PUT/PATCH result and when specifying ``frame=object`` within the query parameters.


Embedding
---------

Each object type specifies its embedded properties, for biosample we have::

    [
        "donor.organism",
        "submitted_by",
        "lab",
        "award",
        "source",
        "treatments.protocols.submitted_by",
        "treatments.protocols.lab",
        "treatments.protocols.award",
        "constructs.documents.submitted_by",
        "constructs.documents.award",
        "constructs.documents.lab",
        "constructs.target",
        "protocol_documents.lab",
        "protocol_documents.award",
        "protocol_documents.submitted_by",
        "derived_from",
        "part_of",
        "pooled_from",
        "characterizations.submitted_by",
        "characterizations.award",
        "characterizations.lab",
        "rnais.target.organism",
        "rnais.source",
        "rnais.documents.submitted_by",
        "rnais.documents.award",
        "rnais.documents.lab",
        "organism"
    ]

The specified links are then replaced with objects::

    {
        "biosample_type": "DNA",
        "biosample_term_id": "UBERON:349829",
        "aliases": ["my-lab:sample1"],
        "accession": "ENCBS000TST",
        "date_created": "2014-01-20T10:30:00-0800",
        "status": "IN PROGRESS",

        "award": {
            "@id": "/awards/my-award/",
            "@type": ["award", "item"],
            "uuid": "fae1bd8b-0d90-4ada-b51f-0ecc413e904d",
            "name": "my-award"
        },

        "lab": {
            "@id": "/labs/my-lab",
            "@type": ["lab", "item"],
            "uuid": "b635b4ed-dba3-4672-ace9-11d76a8d03af",
            "name": "my-lab",
            "title": "My Lab"
        },

        "source": {
            "@id": "/sources/some-source/",
            "@type": ["source", "item"],
            "uuid": "1d5be796-8f80-4fd4-b6c7-6674318657eb",
            "name": "some-source",
            "title": "Some source"
        },

        "organism": {
            "@id": "/organisms/human/",
            "@type": ["organism", "item"],
            "uuid": "7745b647-ff15-4ff3-9ced-b897d4e2983c",
            "name": "human",
            "scientific_name": "Homo sapiens",
            "taxon_id": "9606",
        },

        "submitted_by": {
            "@id": "/users/me/",
            "@type": ["user", "item"],
            "uuid": "bb319896-3f78-4e24-b6e1-e4961822bc9b",
            "title": "My Name",
            "lab": "/labs/my-lab"
        },

        "@id": "/biosamples/ENCBS000TST/",
        "@type": ["biosample", "item"],
        "uuid": "7c245cea-7d59-45fb-9ebe-f0454c5fe950"
        "name": "ENCBS000TST",
        "title": "Biosample ENCBS000TST (human)",
        "characterizations": [],
    }

This embedded object is indexed in elasticsearch to allow searching and faceting across the embedded values.
It is returned when when specifying ``frame=embedded`` within the query parameters.


Page expansion
--------------

The final step in the rendering pipeline is applied only to single items, not to search results.
It provides the opportunity to add properties that are restricted or tailored to certain users, such as the actions and audit results::

    {
        "actions": [
            {
                "profile": "/profiles/biosample.json",
                "href": "/biosamples/ENCBS000TST/#!edit",
                "name": "edit",
                "title": "Edit"
            },
            {
                "profile": "/profiles/biosample.json",
                "href": "/biosamples/ENCBS000TST/#!edit-json",
                "name": "edit-json",
                "title": "Edit JSON"
            }
        ],
        "audit": {
            "ERROR": [
                {
                    "category": "missing donor",
                    "name": "audit_biosample_donor",
                    "level": 60,
                    "detail": "Biosample ENCBS000TST requires a donor",
                    "path": "/biosamples/ENCBS000TST/",
                    "level_name": "ERROR"
                }
            ]
        }
    }
