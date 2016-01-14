Database Documentation:
=====================

The (encodeD) system uses a Postgres implementation of a document store of a JSONLD_ object hierarchy.   Multiple view of each document are indexed in Elasticsearch_ for speed and efficient faceting and filtering.  The JSON-LD object tree can be exported from Elasticsearch with a query, converted to RDF_ and loaded into a SPARQL_ store for arbitrary queries.

**POSTGRES RDB**

When an object is POSTed to a collection, and has passed schema validation, it is inserted into the Postgres object store, defined in storage.py_.   

There are 7 tables in the RDB.  Of these, Resource_ represents a single URI.  Most Resources (otherwise known as Items or simpley "objects" are represented by a single PropSheet_, but the facility exists for multiple PropSheets per Resource (this is used for attachments and files, in which the actual data is stored as BLOBS instead of JSON).  

The Key_ and Link_ tables are indexes used for performance optimziation.  Keys are to find specific unique aliases of Resources (so that all objects have identifiers other than the UUID primary key), while Links are used to track all the JSON-LD relationships between objects (Resources).  Specifically, the Link table is accessed when an Item is updated, to trigger reindexing of all Items that imbed the updated Item.

The CurrentPropSheet_ and TransactionRecord_ tables are used to track all changes made to objects via transactions.