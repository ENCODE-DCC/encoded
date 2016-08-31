===============================
Change log for matched_set.json
===============================

Schema version 9
----------------

* *status* enum was restricted to:
    "enum" : [
        "proposed",
        "started",
        "submitted",
        "ready for review",
        "deleted",
        "released",
        "revoked",
        "archived",
        "replaced"
    ]

Schema version 8
----------------

* Array properties *aliases*, *dbxrefs*, *documents*, and *references* were updated to allow for only unique elements within them.
