Dependency tracking and invalidation
====================================

Keeping elasticsearch in sync.

The /_indexer wsgi app (es_index_listener.py) drives the incremental indexing process. When a new transaction is notified by postgres (or after 60 seconds) it calls the /index view (indexer.py) which works out what needs to be reindexed. The actual reindexing happens in parallel in multiprocessing subprocesses (mpindexer.py.)

When rendering a response, we record the set of embedded_uuids and linked_uuids used.

* ``embedded_uuids`` are those objects embedded into the response or whose properties have been consulted in rendering of the response. Any change to one of these objects should cause an invalidation. (See ``Item.__json__``.)

* ``linked_uuids`` are the objects linked to in the response. Only changes to their url need trigger an invalidation. (See ``Item.__resource_url__``.)

When modifying objects, event subscribers keep track of which objects where updated and their resource paths before and after the modification. This is used to record the set of ``updated_uuids`` and ``renamed_uuids`` in the transaction log. (See indexing.py.)

The indexer process listens for notifications of new transactions. With the union of updated_uuids and union of renamed_uuids across each transaction in the log since its last indexing run, it performs a search for all objects where embedded_uuids intersect with the updated_uuids or linked_uuids intersect with the renamed_uuids. The result is the set of invalidated objects which must be reindexed in addition to those that were modified (recorded in updated_uuids.)

Where an object's url depends on other objects – ``Page`` whose url includes its ancestors in its path, or ``Target`` whose url includes a property from its referenced organism – we must ensure that linked_uuid dependencies to those other objects are recorded in addition the object itself when linked. (See ``Page.__resource_url__`` and ``Target.__resource_url__``.)


Back references
---------------

In a parent-child relationship, it is the child object that references the parent object. A parent response often renders a list of child objects, and that list my be filtered to remove deleted or unpublished child objects.

We want to ensure that parent responses are invalidated when a child object's state changes, so that it would now be included in its parent's list of child objects when it was not before. A parent response must therefore include all *potentially* included child objects in its ``embedded_uuids``, which is done by accessing the child status property through the ``Item.__json__`` method.

We must also invalidate a parent response when a new child is added (either a new object of changing the parent referenced.) This is done adding the parent uuid to the list of updated_uuids recorded on the transaction adding/modifying the child. (See indexing.py ``invalidate_new_back_revs``.)


Isolation level considerations
------------------------------

Postgres defaults to its lowest isolation level, READ COMMITTED: http://www.postgresql.org/docs/9.3/static/transaction-iso.html

For invalidation of back references of new child objects only READ COMMITTED isolation is necessary as invalidated back references are calculated from the updated objects properties.

However, writes must be at least REPEATABLE READ in order for overalapping PATCHes to apply safely.

During recovery indexing uses READ COMMITTED isolation. Indexed objects may be internally inconsistent if there are concurrent updates to embedded objects. But indexing is still eventually consistent as any concurrent update will invalidate the object and it will be reindexed later.

To avoid internal possible internal inconsistancies of indexed objects, SERIALIZABLE isolation is required. It is used once it becomes available when recovery is complete.
