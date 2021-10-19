## Changelog for cart.json

### Schema version 3

* Added *description* and *doi* properties.
* Added *unlisted*, *listed*, *released*, and *revoked* to the enum list for *status*, and removed *disabled* and *current*. Existing carts of status *disabled* or *current* are upgraded to *unlisted*.

### Schema version 2

* Added *file_views* array property.

### Minor changes since schema version 1

* Added optional *identifier* property.

### Schema version 1

* New schema for cart added
