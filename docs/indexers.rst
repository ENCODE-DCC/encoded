Indexers Documentation:
======================

---------------
Primary Indexer
---------------

The (encoded/snovault) system organizes simple objects stored in Postgres into 'documents' that incude, among other things, object relationships in the form of embedded objects, and audits.  These documents are then indexed by elasticsearch.  The work of *indexing*, which includes constructing the documents from Postgres objects is accomplished by a separate *master indexer process* that may then use multiple *worker processes* (via mpindexer.py) to accomplish the tasks.  Upon initialization, the master indexer process will index all documents from all uuids (object ids) in the Postgres database.  After initial indexing, the process wakes every 60 seconds and checks to see if there have been any Postgres transactions since the previous indexing.  If so, a list of uuids for all changed database objects and all related objects is generated and a new indexing cycle begins on just those uuids.  If the list of uuids is large enough (currently 100K or more), the entire set of objects is reindexed.  If there are any **followup indexers**, then the primary indexer will stage the list of uuids just indexed so those indexers may begin work.  A complete reindexing by the primary indexer currently takes ~4 hours on ~875K of documents (2017-10-26).

-----------------
Followup Indexers
-----------------

Followup indexers act on uuids staged by the primary indexer at the end if its cycle.  Like the primary indexer, each followup indexer runs in a separate process and wakes up every 60 seconds to see if there is anything to do.  *Unlike* the primary indexer, followup indexers do not currently employ additional worker processes.

The **vis indexer** is a followup indexer used to generate and store metadata reformatted for browser visualization of files.  The vis indexer acts on uuids staged by the primary indexer and retrieves embedded objects from elasticsearch.  The list of uuids will usually be filtered down to only those for visualizable objects (datasets) with files.  These objects (sometimes referred to as 'vis_blobs') are stored in elasticsearch (as a 'vis_cache') and retrieved primarily for visualization in UCSC trackhubs.  A complete reindexing by the vis indexer currently takes ~10 minutes on ~19K of vis_blobs (2017-10-26).

The **region indexer** is a followup indexer used to load genomic regions from files into an elasticsearch index.  This indexer receives a list of uuids staged by the primary indexer and will usually filter that down to "regionable datasets" which may contain files of interest to be added to the index.  The embedded dataset objects are retrieved from elasticsearch and each dataset's files are reduced to those that are candidates for the region index.  Since the content of files will not change, once a file is in the region index it will not be reindexed.  Therefore, after the initial index, it is quite common for a complete primary reindex to result in 0 files reindexed by the region indexer.  It should be noted that the region index is in most cases a separate instance of elasticsearch and may be located on a separate machine.  Additionally, the region index may contain regions from other systems, not just encoded.  The regions in the index are retrieved by region search queries.  A complete reindexing of all files currently takes ~2.5 hours on ~5K of files (2017-10-26).

---------------------------
_indexer values (listeners)
---------------------------

The *indexer listener* reports certain current and historical values from an *in-memory* JSON object seen via the ``/_indexer`` path.  The followup indexers also have listener reports at ``/_visindexer`` and ``/_regionindexer``. Key values are described here:

  :status: The indexer is either 'waiting' between cycles or 'indexing' during a cycle.
  :started: The time the indexer process started.  This will reflect the most recent startup, which is not necessarily the time the server was first initialized.
  :timestamp: Time of the latest cycle.
  :timeout: Number of seconds the process sleeps between cycles.
  :listening: True when Postgres is reachable and not in recovery.
  :recovery: False unless the database in recovery.
  :errors: If an error occurred while trying to run the indexer, it should appear here.  This is distinct from result errors described below.
  :max_xid: This is a Postgres transaction id which should rise with each database change.  It is used to ensure a consistent view of data during an indexing cycle.
  :snapshot: Most recent postgres snapshot identifier.  As with xid, this is used by the indexer to ensure a consistent view of data.
  :last_result: Result values from the latest cycles **whether anything was indexed or not**.
  :results: An array of up to 10 results from the most recent cycles that *actually indexed* something.

    :title: Which indexer ran. This will be 'primary_indexer' for path /_indexer.  Other idexers exist in encoded.
    :timestamp: Time of this cycle.
    :xmin: Postgres transaction id of this cycle.
    :pass1_took: If 2-pass indexing is enabled, this is the time it took to index objects without audits.
    :pass2_took: If 2-pass indexing is enabled, this is the time it took to audit objects and update that information in elasticsearch.
    :indexed: Number of objects indexed in this cycle.
    :last_xmin: Postgres transaction id of last cycle.  Indexing should have covered all objects changed between last_xmin and xmin.
    :status: This should say 'done' as the results are displayed after a cycle has completed.  See the next section on querying the state of a current cycle.
    :cycles: Count of indexer cycles that actually indexed something. This number should reflect all cycles since the system was initialized or since a full reindexing was requested.
    :errors: If there were any errors indexing specific objects, they should appear here.
    :updated: On small indexing cycle, may contain uuids of updated objects in Postgres.
    :renamed: On small indexing cycle, may contain uuids of renamed objects in Postgres.
    :types: On small indexing cycle, may contain '\@type's of changed objects in Postgres.
    :stats: This contains the raw stats from the response header for this indexer call.

The followup indexers may report a slightly different set of values as not all values will be relevant to each of the indexers.

------------------
_indexer_state API
------------------

In addition to using path /_indexer, a more complete image of an indexer can be accessed via the ``/_indexer_state``, ``/_visindexer_state`` or ``/_regionindexer_state`` paths. These require admin login to be accessed as will become clear below.

These views will return the following values with some slight variation between the 3 indexers:

  :title: Either 'primary_indexer', 'vis_indexer' or 'region_indexer'.
  :status: The indexer is either 'waiting' between cycles or 'indexing' during a cycle.  It might also be 'uninitialized' when the system is first coming up.
  :docs in index: (primary only) The count of all documents currently in the elasticsearch index.
  :vis_blobs in index: (vis only) The count of all vis objects currently in the elasticsearch index.
  :files in index: (region only) The count of all regionable file objects currently in the elasticsearch region index.
  :uuids in progress: The count of uuids currently being indexed.
  :uuids last cycle: The number of uuids in the previous cycle.
  :uuids troubled: The number of uuids that failed to index during the last cycle.
  :to be handed off to other indexer(s): (primary only) The count of uuids that will be staged by the primary indexer when its current cycle completes.
  :registered indexers: (primary only) List of indexers that have started.
  :staged by primary: (vis and region) Count of uuids that have been staged specifically for this indexer.
  :staged to process: (vis and region) Count of uuids set up for processing by this indexer.
  :files added: (region only) Count of files added to the region indexer in the most recent cycle.
  :files dropped: (region only) Count of files dropped from the region indexer in the most recent cycle.
  :now: The UTC time this view was displayed.  Useful for comparing to other times found here.
  :listener: The contents of an ``/_indexer`` request.  (Or ``/visindexer``, ``/_regionindexer`` as appropriate.)  *Described above*.
  :REINDEX requested: If reindexing was requested this will contain 'all' or a list of uuids.
  :NOTIFY requested: If notify was requested, this will include who will be notified and in which circumstances.
  :state: The contents of the indexer's state object held in elasticsearch...

    :title: Either 'primary_indexer', 'vis_indexer' or 'region_indexer'
    :status: The indexer is either 'done' with a cycle or 'indexing' during a cycle.
    :cycles: Count of indexer cycles that actually indexed something. This number should reflect all cycles since the system was initialized or since a full reindexing was requested.
    :cycle_count: When indexing, the number of uuids in the current cycle.
    :cycle_took: How long it took to complete the most recent indexer cycle.
    :cycle_started: When the most recent indexing cycle started.
    :indexed: Number of objects indexed in the most recent cycle.
    :indexing_elapsed: When currently indexing, the amount of time since indexing started.
    :vis_updated: (vis indexer only) Number of uuids that actually resulted in a vis_blob added to index.
    :invalidated: (primary only) Number of uuids needing to be indexed.
    :renamed: (primary only) uuids of objects renamed in postgres.
    :updated: (primary only) uuids of objects updated in postgres.
    :referencing: (primary only) Count of uuids referenced by objects updated or renamed in postgres.
    :txn_count: (primary only) Number of postgres transactions this cycle covers.
    :xmin: (primary and vis) Postgres transaction id of this cycle.
    :last_xmin: (primary and vis) Postgres transaction id of last cycle.  Indexing should have covered all objects changed between last_xmin and xmin.
    :max_xid: (primary and vis) This is a Postgres transaction id which should rise with each database change.  It is used to ensure a consistent view of data during an indexing cycle.
    :first_txn_timestamp: (primary only) Timestamp of when the postgres tranaction occurred which led to this indexing cycle.

Several requests can be made of the state paths with use of ?request=value appended to the url:

  :reindex: Use 'all' for complete reindexing or comma separated uuids for specific reindexing.  This powerful method necessitates being logged on with admin permissions.
  :notify: One or more comma separated slack ids to be notified when the specific indexer is done.

    :bot_token: For the time being this is required for slack notification to work.
    :which: Use 'all' when combined with notify to be notified when all indexers have completed.

A note about reindexing the region indexer.  Since files are not expected to change contents they are not generally *re-added* to the index, it is useful to be able to force one or more files into the regions index.  By requesting reindex=all or reindex={uuids} directly to ``/_regionindexer_state`` the qualified files *will be* (re)added.  It should be understood that the uuid expected is *for the dataset* that contains the file, not the file itself.  It should also be noted that a primary indexer reindex request will trigger the (followup) region indexer to reindex, but this will not force re-add files.
