Database Documentation:
=====================

The (encodeD) system uses a Postgres implementation of a document store of a JSONLD_ object hierarchy.   Multiple view of each document are indexed in Elasticsearch_ for speed and efficient faceting and filtering.  The JSON-LD object tree can be exported from Elasticsearch with a query, converted to RDF_ and loaded into a SPARQL_ store for arbitrary queries.

**POSTGRES RDB**

When an object is POSTed to a collection, and has passed schema validation, it is inserted into the Postgres object store, defined in storage.py_.   

There are 7 tables in the RDB.  Of these, Resource_ represents a single URI.  Most Resources (otherwise known as Items or simpley "objects" are represented by a single PropSheet_, but the facility exists for multiple PropSheets per Resource (this is used for attachments and files, in which the actual data is stored as BLOBS instead of JSON).  

The Key_ and Link_ tables are indexes used for performance optimziation.  Keys are to find specific unique aliases of Resources (so that all objects have identifiers other than the UUID primary key), while Links are used to track all the JSON-LD relationships between objects (Resources).  Specifically, the Link table is accessed when an Item is updated, to trigger reindexing of all Items that imbed the updated Item.

The CurrentPropSheet_ and TransactionRecord_ tables are used to track all changes made to objects via transactions.

On a standard EC2/Ubuntu install, you will have to su to user encoded to interact with the database on the command line (psql).
The current production database has a useful VIEW created for querying recent objects, called OBJECT:

```
    encoded=> \d+ object
    View "public.object"
    Column   |       Type        | Modifiers | Storage  | Description 
   ------------+-------------------+-----------+----------+-------------
    rid        | uuid              |           | plain    | 
    item_type  | character varying |           | extended | 
    properties | json              |           | extended | 
    tid        | uuid              |           | plain    | 
   View definition:
    SELECT resources.rid,
      resources.item_type,
      propsheets.properties,
      propsheets.tid
     FROM resources
       JOIN current_propsheets USING (rid)
       JOIN propsheets USING (rid, name, sid)
    WHERE current_propsheets.name::text = ''::text;
```

As an example query (show me all the files that link back to dataset with uuid: 27311ca3-dc24-4853-94bc-a80825598621


```
  encoded=> select * from object where item_type='file' and properties ->> 'dataset' = '27311ca3-dc24-4853-94bc-a80825598621';
```
  


** A LOCAL SERVER **
The dev-servers command completely drops and restarts a local copy of postgres db. Posts all the objects in tests/data/inserts (plus /tests/data/documents as attachments). Then indexes them all in local elastic search.
but these dbs are both destroyed when you kill the dev-servers process

** CREATING A SPARQL STORE **

After building out the software, it will create an executable called json_rdf

```
  bin/jsonld-rdf  'https://www.encodeproject.org/search/?type=Item&frame=object&limit=all' -s n3 -o encode-rdf.n3
```

The n3 file can be imported into a SPARQL using, for example, Virtuoso ( http://semanticweb.org/wiki/Virtuoso.html_ ) or YasGUI http://yasgui.org/_

The query may take upwards of 20 minutes.

There are other output options documented in src/commands/json_rdf.py  (XML, Turtle, trix others), you can also curl the URL above directly and write a json file (set accept-headers or use &format=json), and pass the file to bin/jsonld-rdf
