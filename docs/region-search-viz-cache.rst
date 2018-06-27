===============================
Region Search and Viz Cache
===============================

Region-Search
-------------

encodeD has a feature to search through a sub-set of result files "tracks" by genomic coordinate.
This is accessble from the URL region-search/ (in production: https://www.encodeproject.org/region-search).

Region search takes a variety of inputs, all of which must be tranformed into genome assembly (e.g., hg19, mm10, GRCh38..) + a range of coordinates (usually a SNP or varient, or a gene).

This region is intersected with the region-search index in elasticsearch (ES) to return a list of:
a) peaks that intersect
b) file uuids that define those peaks and a small object containing minimal file details including dataset uuid
c) experments with facets ("aggegrations" in ES lingo) that those files belong to (via a secondary query on list of files).

This region_search API is in src/encode/region_search.py, which calls into region_atlas.py which encapsulates access to the region_index.
The process by which the BED files get into Elasticsearch is handled by the "region indexer" system.


Regulome-Search
---------------

Access to the RegulomeDB feature is through the URL regulome-search/ (in production: https://www.encodeproject.org/regulome-search).
This is near identical to region-search and is served by the same function defined in region_search.py.
The set of files that are indexed for regulome and region_search are not identical but are overlapping.
Regulome is primarily focuses on SNPs and calculates a 'regulome score' for each single-base position, based on the types of regions the SNP intersects.
Most of the subtle differences between region and regulome are defined in the two classes RegionAtlas and RegulomeAtlas found in region_atlas.py.

Automatic Region Indexing
-----------------------

The "peaks" which are essentially intervals in a BED file, are kept in a separate index per chromosome (including scaffolds).
In the apache config there is a seperate indexing listener:

.. code::
    # regionindexer. Configure first to avoid catchall '/'
    WSGIDaemonProcess encoded-regionindexer user=encoded group=encoded processes=1 threads=1 display-name=encoded-regionindexer
    WSGIScriptAlias /_regionindexer /srv/encoded/parts/production-regionindexer/wsgi process-group=encoded-indexer application-group=%{GLOBAL}

Which is an instance of snovault.elasticsearch.indexer with path=index_region.
As a "follow up" indexer (see indexer.rst) the region_indexer never queries postgres and relies entirely on encodeD objects in elasticsearch.
The listener wakes every 60 seconds when idle and queries es for uuids staged by the primary encodeD indexer (/snovault/meta/staged_for_region_indexer) as having just been indexed.
These uuids are filtered down to datasets that are likely to contain bed files to be added to the region indexes.
Each dataset is then verified to be of interest and its list of files is filtered down to candidate files to be added.
If a candidate file is NOT already resident in the regions index it is then added.
While examining a candidate dataset, if a member file is no longer a candidate but is found in the index, it will be removed.
Most files are accessed via io.BytesIO() on the file download URL, and each peak (line of BED file) is indexed as {file-uuid, start, stop}.
Very large files may cause memory allocations errors if read as a byte-stream, so they are downloaded to the server as a temporary file and then read line by line to accomplish the same thing as the in-memory byte-stream does.
The region indexes consist of one index per chromosome (e.g. 'chrx') (or scaffold), document type is the assembly (e.g. 'hg19') and key is the file's uuid.
A single document contains all the positions for that assembly/chromosome found in the file.  Positions are a "nested" array (in ES terminology).
A small amount of file specific information is then added to the "resident_regionsets" index, including whether the file was indexed for region search, regulome, or both.

In addition to the peak positions, the region_indexer also holds dbSNP variants in a slightly different arrangement.
There is a need to look up SNPs not only by position but also by rsid.  To do this requires a separate document per SNP, keyed on rsid.
Unlike peaks, which have chromosome based indexes, SNPs have assembly based indexes, to avoid duplicate rsid keys in an index holding more than one assembly.
To aid queries by position, the document type is the chromosome.
A small amount of information for the entire SNP file is added to the "resident_regionsets" index, just as for peak files.
A primary purpose for the resident_regionsets index is to quickly determine if a file has already been indexed, as its contents will not change.
This is especially important for SNP files which contain more than 60 million SNPs each and take a *very long time* to index.

Analogous to the primary (encodeD metadata) indexer, the indexing state is stored in the Elasticsearch object snovault/meta/region_indexer.
Unlike the primary indexer, work of the region indexer is not multi-threaded, using only 1 process at this time.

Full indexing takes ~4 hours on ~6000 region search files.
This expands to ~8 hours with regulome and dbSNP files.


TrackHub generation
-----------------------

UCSC trackhubs are large blocks of ASCII text that we provide a URL for.
The UCSC genome browser URL uses @@hub and /batch_hub/ endpoints as callbacks to generate 3 "files": hub.txt, genomes.txt and trackDb.txt.
The code for these views/endpoints is in visualization.py and vis_defines.py.

The big output is the trackDb.txt which contains all the information to display each file (with metadata) at a browser that consumes it.
The hub.txt lists the genomes available and genomes.txt are just "pointers" to the correct trackDb.txt per assembly (genome).

Ensembl should support the UCSC hub formatting and our hubs have worked in the past.
However, recently our hubs were failing at Ensembl, possibly due to a bug at their site.

Each visualizable ENCSR (Experiment or Dataset that contains one or more output files that are browser compliant, i.e., bigBed or bigWig) has the information for it's trackDb cached in Elasticsearch independent of the encodeD application.
While this would not be necessary if trackhubs only contained one or two experiments, batch_hubs can contain as many a 100 experiments and can only be efficiently generated if much of the reformatting for visualization is already cached.

The "vis_datasets" aka "vis_blobs" are stored in a separate ES index called vis_cache as JSON, keyed on ENCSRxxx_assembly.
When a trackHub or other visualization query comes in, it's looked for by accession in the cache, otherwise it is created (and added to the vis_cache index).
For batch_hubs, if at least one vis_blob is found in the cache then any missing ones will not be regenerated.
It is possible to force the (re)creation of vis_blobs for any hub request by adding 'regen' to the trackDb request (e.g. ../trackDb.regen.txt).

You can see the raw JSON used to generate the trackDb.txt by requesting json instead of text (e.g. ../trackDb.json).
Further, since batch_hubs are reorganized from a list of vis_blobs to a set of assay based composites, the json for the vis_blobs themselves can be seen by requesting 'vis_blob.json'.
(For single experiment hubs, trackDb.json and vis_blob.json are identical requests.)
Finally any trackDb.txt request can be transfomed to the IHEC JSON equivalent by requesting ihec.json.
(Note that IHEC JSON is an unreleased feature so far and the contents need to be verified by IHEC).


Viz Caching and Priming
-----------------------

The caching of visualization JSON is handled by a "follow up" indexer (see indexer.rst), just as region indexing, described above.
In the apache config there is a seperate indexing listener:

.. code::
    # visindexer. Configure first to avoid catchall '/'
    WSGIDaemonProcess encoded-visindexer user=encoded group=encoded processes=1 threads=1 display-name=encoded-visindexer
    WSGIScriptAlias /_visindexer /srv/encoded/parts/production-visindexer/wsgi process-group=encoded-indexer application-group=%{GLOBAL}

The listener wakes every 60 seconds when idle and queries es for uuids staged by the primary encodeD indexer (/snovault/meta/staged_for_vis_indexer) as having just been indexed.
As a follow up indexer, the vis caching does not query postgres and gets all information from the primary indexes in elasticsearch.
These uuids are filtered down to datasets that are likely to be visualizable.
The embedded object is retrieved for each likely dataset and reformatted to one or more vis_blobs (one for each relevant assembly) which is then added to the one index named "vis_cache".
To support IHEC JSON, each dataset may require one or more additional queries of encodeD metadata from elasticsearch.

Analogous to the primary (encodeD metadata) indexer, the indexing state is stored in the Elasticsearch object snovault/meta/vis_indexer.
Unlike the primary indexer, work of the vis indexer uses only 1 process at this time.

The whole indexing of all visualizable datasets takes ~30 minutes for ~25K of vis_blobs.


Differences between clustered and non-clustered deployments
-----------------------------------------------------------

Currently the region indexes are contained in the same elasticsearch instance as encodeD metadata, for all flavors of the encodeD application including local.
By default, unclustered demo's will not have region indexes, while clustered deployments will.
(This arrangement can be overridden using deploy.py option: --set-region-index-to 'True' or 'False'.)
It is possible in the future (as in the past) that the region indexes will be separated from the primary indexes into their own elasticsearch instance.
This might be desirable because the region indexes could grow to be massive, take a very long time to index and have very low turnover.
The region indexes may not change at all between releases of the encodeD portal, so recreating them each release would be of little value.
It is not anticipated that the vis_cache index will ever be separated from the encodeD elasticsearch instance, nor will it be turned off in unclustered demos.
