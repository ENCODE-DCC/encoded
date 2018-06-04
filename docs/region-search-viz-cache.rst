===============================
Region Search and Viz Cache
===============================

Region-Search
------------

encodeD has a feature to search through a sub-set of result files "tracks" by genomic coordinate.
This is accessble from the URL region-search/ (in production: https://www.encodeproject.org/region-search).

Region search takes a variety of inputs, all of which must be tranformed into genome assembly (e.g., hg19, mm10, GRCh38..) + a range of coordinates (usually a SNP or varient, or a gene).

This region is intersected with the region-search index in elasticsearch (ES) to return a list of:
a) peaks that intersect
b) files that created those peaks (bed)
c) experments with facets ("aggegrations" in ES lingo) that those files belong to (via a secondary query on list of files).

This search functionality is in src/encode/region_search.py and is relatively compact and straightforward.
The process by which the BED files get into Elasticsearch is handled by the "region indexer" system.


Automatic Region Indexing
-----------------------

The "peaks" which are essentially intervals in a BED file are kept in a separate index per chromosome (including scaffolds).   In the apache config there is a seperate indexing listener:

.. code::
    # regionindexer. Configure first to avoid catchall '/'
    WSGIDaemonProcess encoded-regionindexer user=encoded group=encoded processes=1 threads=1 display-name=encoded-regionindexer
    WSGIScriptAlias /_regionindexer /srv/encoded/parts/production-regionindexer/wsgi process-group=encoded-indexer application-group=%{GLOBAL}

Which is an instance of snovault.elasticsearch.indexer with path=index_region.   As a "follow up" indexer (see indexer.rst) the region_indexer never queries postgres and relies entirely on encodeD objects in elasticsearch.  The listener wakes every 60 seconds when idle and queries es for uuids staged by the primary encodeD indexer (/snovault/meta/staged_for_region_indexer) as having just been indexed. These uuids are filtered down to datasets that are likely to contain bed files to be added to the region indexer.  Each dataset is then verified to be of interest and its list of files is filtered down to candidate files to be added.  If a candidate file is NOT already resident in the regions index it is then added. The file are accessed via io.BytesIO() on the file download URL, and each peak (line of BED file) is indexed as {file-uuid, start, stop}.  The region indexes consist of one index per chromosome (e.g. 'chrx') (or scaffold), document type is the assembly (e.g. 'hg19') and key is the file's uuid.  A small amount of file specific information is then added to the "resident_regionsets" index.

Analogous to the primary (encodeD metadata) indexer, the indexing state is stored in the Elasticsearch object snovault/meta/region_indexer.  Unlike the primary indexer, work of the region indexer is not multi-threaded, using only 1 process.

Full indexing takes ~4 hours on ~5000 files.  Currently region indexes are only used for "region search" functionality described above.  However "Regulome DB" files are going to be added to the region indexes.


TrackHub generation
-----------------------

UCSC trackhubs are large blocks of ASCII text that we provide a URL for.  The UCSC genome browser URL uses @@hub and /batch_hub/ endpoints as callbacks to generate 3 "files": hub.txt, genomes.txt and trackDb.txt.  The code for these views/endpoints is in visualization.py and vis_defines.py.

The big output is the trackDb.txt which contains all the information to display each file (with metadata) at a browser that consumes it.
The hub.txt lists the genomes available (genomes.txt) and genomes.txt are just "pointers" to the correct trackDb.txt per assembly (genome).

Ensembl should support the UCSC hub formatting and our hubs have worked in the past.  However, recently our hubs were failing at Ensembl, possibly due to a bug at their site.

Each visualizable ENCSR (Experiment or Dataset that contains one or more output files that are browser compliant, i.e., bigBed or bigWig) has the information for it's trackDb cached in Elasticsearch independent of the encodeD application.  While this would not be necessary if trackhubs only contained one or two experiments, batch_hubs can contain as many a 100 experiments and can only be efficiently generated if much of the reformatting for visualization is already cached.

The "vis_datasets" aka "vis_blobs" are stored in a separate ES index called vis_cache as JSON, keyed on ENCSRxxx_assembly.
When a trackHub or other visualization query comes it, it's looked for by accession in the cache, otherwise it is created.  For batch_hubs, if at least one vis_blob is found in the cache then any missing ones will not be regenerated. It is possible to force the (re)creation of vis_blobs for any hub request by adding 'regen' to the trackDb request (e.g. ../trackDb.regen.txt).

You can see the raw JSON used to generate the trackDb.txt by requesting json instead of text (e.g. ../trackDb.json).  Further, since batch_hubs are reorganized from a list of vis_blobs to a set of assay based composites, the json for the vis_blobs themselves can be seen by requesting 'vis_blob.json'. (For single experiment hubs, trackDb.json and vis_blob.json are identical requests.)  Finally any trackDb.txt request can be transfomed to the IHEC JSON equivalent by requesting ihec.json.  (Note that IHEC JSON is an unreleased feature so far and the contents need to be verified by IHEC).


Viz Caching and Priming
-----------------------

The caching of visualization JSON is handled by a "follow up" indexer (see indexer.rst), just as region indexing described above.  In the apache config there is a seperate indexing listener:

.. code::
    # visindexer. Configure first to avoid catchall '/'
    WSGIDaemonProcess encoded-visindexer user=encoded group=encoded processes=1 threads=1 display-name=encoded-visindexer
    WSGIScriptAlias /_visindexer /srv/encoded/parts/production-visindexer/wsgi process-group=encoded-indexer application-group=%{GLOBAL}

The listener wakes every 60 seconds when idle and queries es for uuids staged by the primary encodeD indexer (/snovault/meta/staged_for_vis_indexer) as having just been indexed. These uuids are filtered down to datasets that are likely to be visualizable.  The embedded object is retrieved for each likely dataset and reformatted to one or more vis_blobs (one for each relevant assembly) which is then added to the on index named "vis_cache".  To support IHEC JSON, each dataset may require one or more additional queries of encodeD metadata from elasticsearch.

Analogous to the primary (encodeD metadata) indexer, the indexing state is stored in the Elasticsearch object snovault/meta/vis_indexer.  Unlike the primary indexer, work of the vis indexer uses only 1 process.

The whole indexing of all visualizable datasets takes ~30 minutes for ~25K of vis_blobs.


Differences between clustered and non-clustered deployments
-----------------------------------------------------------

Currently the region indexes are contained in the same elasticsearch instance as encodeD metadata, for all flavors of the encodeD application including local.  In the future it is expected that unclustered demo's will not have region indexes, and under some circumstances the region indexes will be migrated to their own instance of elasticsearch.  It is not anticipated that the vis_cache index will ever be separated from the encodeD elasticsearch instance, nor will it be turned off in unclustered demos.


