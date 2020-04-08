## Changelog for file.json

### Minor changes since schema version 18
* *output_type* list was updated to include the enum *regulatory elements*.
* Added *cropped_read_length* property
* Added "gRNAs" to *output_type* enum list.

### Schema version 18
* Added dependency restrictions for files of *output_type* subreads, preventing specification of *assembly* and requiring that *platform* be one of the Pacific Biosciences platforms.

### Schema version 17
* Added Oxford Nanopore platforms, MinION and PromethION to dependency that enforces that *run_type* and *read_length* properties should not be specified for FASTQ files produced on Oxford Nanopore and PacBio platforms.

### Minor changes since schema version 16
* *output_type* list was updated to include the enum *personalized genome assembly* and *index reads*
* *index_of* list property was added to allow specification of FASTQ files that are linked to the index file
* *output_type* list was updated to include the following enums:
        [
            "negative control regions",
            "non-targeting gRNAs",
            "positive control regions",
            "safe-targeting gRNAs",
            "subreads"
        ]

### Schema version 16

* Added new PacBio platform, PacBio Sequel II to dependency that enforces that *run_type* and *read_length* properties should not be specified for FASTQ files produced on PacBio platform.

### Minor changes since schema version 15

* *output_type* list was updated to include the enum *elements reference*
* *output_type* list was updated to include the enum *miRNA annotations*

### Schema version 15

* Add *IDR ranked peaks* and *IDR thresholded peaks* for *output_type*
* Add a new property *preferred_default*
* Change *output_type* *conservative idr thresholded peaks* to *conservative IDR thresholded peaks*
* Change *output_type* *optimal idr thresholded peaks* to *optimal IDR thresholded peaks*
* Change *output_type* *pseudoreplicated idr thresholded peaks* to *pseudoreplicated IDR thresholded peaks*

### Minor changes since schema version 14

* *output_type* list was updated to include the following enums: *transcriptome annotations*, *sequence barcodes* and *sequence adapters*
* Added *read_structure*
* Added *matching_md5sum* property, which tracks a list of other files with identical md5 sums.

### Schema version 14

* Changed *candidate regulatory elements* in *output_type* to *candidate Cis-Regulatory Elements*

### Minor changes since schema version 13

* *output_type* list was updated to include *mapping quality thresholded chromatin interactions*
* *read_count*, *file _size*, *read_length*, *mapped_read_length* were set to have a minimum of 0.
* *barcode_position* in  *flowcell_details* was set to have a minimum of 1.
* *read_name_details* property is added to the schema. This property can be specified for FASTQ files only, and it could be posted by DCC only.
* added *gene alignments* to *output_type* enum.
* added *idx* to *file_format* to support kallisto indexes.
* added *txt* to *file_format* enum, added *restriction enzyme site locations* to *output_type* enum, and created *restriction_enzymes* property to specify the restriction enzymes for which a *restriction enzyme site locations* file is applicable
* added *M21*, *V29*, and *V30* to the list of enums for the *genome_annotation* property.
* *file_format* was updated to include *database*.

### Schema version 13

* *run_type* and *read_length* properties should not be specified for FASTQ files produced on PacBio platform. Dependency that enforces that was added.

### Minor changes since schema version 12

* New enumerations that could be posted only by the DCC were added in output_types: *redacted alignments* and *redacted unfiltered alignments*; both enumerations are categorized as *alignments*.
DNA sequence information was removed from these analyses, since they are based on primary data with restricted public access (such as dbGap).
* New enumerations were added in output_types: *differential expression quantifications* and *differential splicing quantifications*; both enumerations are categorized as *quantification*
* *fastq_signature* list items (colon separated flowcell, lane, read-end and barcode items) now can include 3 as the read-end portion of the signature item.


### Schema version 12

* *run_type* and *mapped_run_type* were limited to only "single-ended" and "paired-ended" types

### Schema version 11

* *alternate_accessions* now must match accession format, "ENCFF..." or "TSTFF..."
* *no_file_available* field was added. The DCC will post this boolean field. Files with no_files_available = true will not be required to specify md5sum and file_size values.
* *revoke_detail* was added.  The DCC will post this field. The goal is to make the reason for file revoke clear:

        "revoke_detail": {
            "title": "Revoke error detail",
            "description": "Explanation of why the file was revoked.",
            "comment": "Do not submit. The field would be posted by DCC.",
            "type": "string",
            "permission": "import_items"
        }
#### Formats and enums are more restrictive for several fields:

* *output_type* values ["predicted forebrain enhancers", "predicted heart enhancers", "predicted whole brain enhancers", "sequence alignability",] added to the list of values that could be submitted only by DCC personnel
* *revoke_detail* is available only for files with status = revoked

### Schema version 10

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 9.a

#### Fields restricted to DCC access only:
* *status*
* *restricted*
* *content_md5sum*
* *mapped_read_length*
* *mapped_run_type*

#### Fields that are now required for certain cases:

* *platform* value is now required for files with *file_format* that is one of ["fastq", "rcc", "csfasta", "csqual", "sra", "CEL", "idat"]
* *assembly* value is required for files with *file_format* that is one of ["bam", "sam", "gtf", "bigWig"]
* *file_size* value is now required for files with *status* that is one of ["in progress", "released", "archived", "revoked"]
* *paired_end* value (1, 2, or 1,2) is required for files with *run_type* = paired-ended and forbidden for *run_type* that is one of ["single-ended", "unknown"]
* *read_length* value is now required for files with *output_type* = reads and *file_format* that is one of ["fastq", "fasta", "csfasta", "csqual", "sra"]

#### Formats and enums are more restrictive for several fields:

* *date_created* format is limited now to only *date-time* and not one of ["date", "date-time"] as it used to be
* *md5sum* value formatting is now enforced with regex, validating it as a 32-character hexadecimal number
* *output_type* values ["tRNA reference", "miRNA reference", "snRNA reference"] added to the ist of values that could be submitted only by DCC personnel
* *file_format* values ["sra", "btr"] could be submitted only by DCC personnel

#### Restrictions for use were also put in place:

* *mapped_read_length* is available only for files with file_format = bam
* *mapped_run_type* is available only for files with file_format = bam
* *statuses* "uploaded" and "format check failed" were removed
* *paired_end* enums list was expanded to include a "1,2" value that is acceptable only for *file_format* = sra files that have *run_type* = paired_ended

### Schema version 9

* property *supercedes* was renamed to *supersedes*
* *assembly* values are no longer accepted for *file_format* = fastq

### Schema version 8

* *technical_replicates* was added as a calculated field.

* *mapped_read_length* was added for alignments when the length of the mapped reads differs from the accessioned fastq.

### Schema version 7

#### The following arrays were restricted to contain unique values

* *derived_from*
* *controlled_by*
* *supersedes*
* *aliases*
* *file_format_specifications*

### Schema version 6

* *output_type* was updated to have more accurate terms:

        "mapping": {
            'minus strand signal of multi-mapped reads': 'minus strand signal of all reads',
            'plus strand signal of multi-mapped reads': 'plus strand signal of all reads',
            'signal of multi-mapped reads': 'signal of all reads',
            'normalized signal of multi-mapped reads': 'normalized signal of all reads'
        }
       
### Schema version 5

* *run_type* was migrated from replicate.paired_ended. It will be required for fastq files.  If *run_type* is paired-ended then *paired_with* will be required as well:

           "run_type": {
            "title": "Run type for sequencing files",
            "description": "Indicates if file is part of a single or paired run",
            "type": "string",
            "enum": [
                "single-ended",
                "paired-ended",
                "unknown"
            ]
        },

* *read_length* was migrated this field from replicate.read_length.  It will be required for fastq files.:

            "read_length": {
                "title": "Read length",
                "description": "For high-throughput sequencing, the number of contiguous nucleotides determined by sequencing.",
                "type": "integer"
            },

* *read_length_units* was added as a calculated field.  It will not need to be submitted.

* *platform* was migrated this field from replicate.read_length.  It will be required for fastq files.:

            "platform": {
                "title": "Platform",
                "description": "The measurement device used to collect data.",
                "comment": "See platform.json for available identifiers.",
                "type": "string",
                "linkTo": "platform"
            },

* *file_format* enum was restricted to general formats for example bed not bed_narrowpeak:
    
            "mapping" = {
                'bed_bedLogR': 'bed',
                'bed_bedMethyl': 'bed',
                'bed_broadPeak': 'bed',
                'bed_gappedPeak': 'bed',
                'bed_narrowPeak': 'bed',
                'bed_bedRnaElements': 'bed',
                'bedLogR': 'bigBed',
                'bedMethyl': 'bigBed',
                'broadPeak': 'bigBed',
                'narrowPeak': 'bigBed',
                'gappedPeak': 'bigBed',
                'bedRnaElements': 'bigBed'
            }

            "current_enum": [
                    "bam",
                    "bed",
                    "bigBed",
                    "bigWig",
                    "fasta",
                    "fastq",
                    "gff",
                    "gtf",
                    "hdf5",
                    "idat",
                    "rcc",
                    "CEL",
                    "tsv",
                    "csv",
                    "sam",
                    "tar",
                    "wig"
            ]


* *file_format_type* was added and will be required when *file_format* is ["bed", "bigBed", "gff"]:

            "enum": [
                "bed6",
                "bed9",
                "bedGraph",
                "bedLogR",
                "bedMethyl",
                "broadPeak",
                "gappedPeak",
                "gff2",
                "gff3",
                "narrowPeak"
            ]

            "comment": "Historical file formats, not valid for new submissions.",
            "enum": [
                "unknown",
                "bedRnaElements"
            ]

* *file_format_specifications* was added as a way to add description or autosql to the file object:

            "file_format_specifications": {
                "title": "File format specifications documents",
                "description": "Text or .as files the further explain the file format",
                "type": "array",
                "items": {
                        "comment": "See document.json for a list of available identifiers.",
                        "type": "string",
                        "linkTo": "document"
                        }
            },
             
* *output_category* added as a calculated field.  The files are now given one of these categories.:

           [
           "raw data",
           "alignment",
           "signal",
           "annotation",
           "quantification",
           "reference",
           "validation"
           ]


* *output_type* enum was changed dramatically to more specifically describe what the file contents are.  The maping here is simplistic.  (For further details in how we re-classified please look at src/encoded/upgrade/file.py.):

            output_mapping = {
                'idat green file': 'idat green channel',
                'idat red file': 'idat red channel',
                'reads': 'reads',
                'rejected reads': 'rejected reads',
                'rcc': 'reporter code counts',
                'CEL': 'intensity values',
                'raw data': 'raw data',
                'alignments': 'alignments',
                'transcriptome alignments': 'transcriptome alignments',
                'spike-ins': 'spike-in alignments',
                'multi-read minus signal': 'minus strand signal of multi-mapped reads',
                'multi-read plus signal': 'plus strand signal of multi-mapped reads',
                'multi-read signal': 'signal of multi-mapped reads',
                'multi-read normalized signal': 'normalized signal of multi-mapped reads',
                'raw minus signal': 'raw minus strand signal',
                'raw plus signal': 'raw plus strand signal',
                'raw signal': 'raw signal',
                'raw normalized signal': 'raw normalized signal',
                'unique minus signal': 'minus strand signal of unique reads',
                'unique plus signal': 'plus strand signal of unique reads',
                'unique signal': 'signal of unique reads',
                'signal': 'signal',
                'minus signal': 'minus strand signal',
                'plus signal': 'plus strand signal',
                'Base_Overlap_Signal': 'base overlap signal',
                'PctSignal': 'percentage normalized signal',
                'SumSignal': 'summed densities signal',
                'WaveSignal': 'wavelet-smoothed signal',
                'signal p-value': 'signal p-value',
                'fold change over control': 'fold change over control',
                'enrichment': 'enrichment',
                'exon quantifications': 'exon quantifications',
                'ExonsDeNovo': 'exon quantifications',
                'ExonsEnsV65IAcuff': 'exon quantifications',
                'ExonsGencV10': 'exon quantifications',
                'ExonsGencV3c': 'exon quantifications',
                'ExonsGencV7': 'exon quantifications',
                'GeneDeNovo': 'gene quantifications',
                'GeneEnsV65IAcuff': 'gene quantifications',
                'GeneGencV10': 'gene quantifications',
                'GeneGencV3c': 'gene quantifications',
                'GeneGencV7': 'gene quantifications',
                'genome quantifications': 'gene quantifications',
                'library_fraction': 'library fraction',
                'transcript quantifications': 'transcript quantifications',
                'TranscriptDeNovo': 'transcript quantifications',
                'TranscriptEnsV65IAcuff': 'transcript quantifications',
                'TranscriptGencV10': 'transcript quantifications',
                'TranscriptGencV3c': 'transcript quantifications',
                'TranscriptGencV7': 'transcript quantifications',
                'mPepMapGcFt': 'filtered modified peptide quantification',
                'mPepMapGcUnFt': 'unfiltered modified peptide quantification',
                'pepMapGcFt': 'filtered peptide quantification',
                'pepMapGcUnFt': 'unfiltered peptide quantification',
                'clusters': 'clusters',
                'CNV': 'copy number variation',
                'contigs': 'contigs',
                'enhancer validation': 'enhancer validation',
                'FiltTransfrags': 'filtered transcribed fragments',
                'hotspots': 'hotspots',
                'Junctions': 'splice junctions',
                'interactions': 'long range chromatin interactions',
                'Matrix': 'long range chromatin interactions',
                'PrimerPeaks': 'long range chromatin interactions',
                'sites': 'methylation state at CpG',
                'methyl CG': 'methylation state at CpG',
                'methyl CHG': 'methylation state at CHG',
                'methyl CHH': 'methylation state at CHH',
                'peaks': 'peaks',
                'replicated peaks': 'replicated peaks',
                'RbpAssocRna': 'RNA-binding protein associated mRNAs',
                'splice junctions': 'splice junctions',
                'Transfrags': 'transcribed fragments',
                'TssGencV3c': 'transcription start sites',
                'TssGencV7': 'transcription start sites',
                'Valleys': 'valleys',
                'Alignability': 'sequence alignability',
                'Excludable': 'blacklisted regions',
                'Uniqueness': 'sequence uniqueness',
                'genome index': 'genome index',
                'genome reference': 'genome reference',
                'Primer': 'primer sequence',
                'spike-in sequence': 'spike-in sequence',
                'reference': 'reference',
                'enhancers': 'predicted enhancers',
                'enhancers_forebrain': 'predicted forebrain enhancers',
                'enhancers_heart': 'predicted heart enhancers',
                'enhancers_wholebrain': 'predicted whole brain enhancers',
                'TssHmm': 'predicted transcription start sites',
                'UniformlyProcessedPeakCalls': 'optimal idr thresholded peaks',
                'Validation': 'validation',
                'HMM': 'HMM predicted chromatin state'
            }


* *md5sum_content* was added.  The DCC will calculate this field. The goal is to make this unique.:

            "content_md5sum": {
                    "title": "Content MD5sum",
                    "description": "The MD5sum of the uncompressed file.",
                    "comment": "This is only relavant for gzipped files.",
                    "type": "string",
                    "format": "hex"
            }


### Schema version 4

* *lab* was added
* *award* was added
* *download_path* was removed as we now have *href*
* *flowcell_details* array was migrated from *replicate.flowcell_details*
