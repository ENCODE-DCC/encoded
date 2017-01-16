=========================
Change log for dataset.json
=========================

Schema version 10
-----------------

* *description*, *notes*, and *submitter_comment* are now not allowed to have any leading or trailing whitespace

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