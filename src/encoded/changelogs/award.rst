=========================
Change log for award.json
=========================


Schema version 2
----------------

* Default values of '' were removed. You can no longer submit a blank url (url='')

* "status" was brought into line with other objects that are shared. Disabled grants with rfa in ['ENCODE2', 'ENCODE2-Mouse']

    "enum" : [
        "current",
        "deleted",
        "replaced",
        "disabled"
    ]