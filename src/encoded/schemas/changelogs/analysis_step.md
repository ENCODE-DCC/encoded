## Changelog for analysis_step.json

### Minor changes since schema version 10
* Added *bigInteract* to the enum list for *input_file_types* and *output_file_types*
* Added *bias model* to the enum list for *input_file_types* and *output_file_types*

### Schema version 10
* Updated *spike-in sequence* to *spike-ins* in enums for *output_file_types* and *input_file_types*.

### Minor changes since schema version 9
* Added *representative peak selection* and *candidate cis-regulatory element identification* to the enum list for *analysis_step_types*
* Added *consensus DNase hypersensitivity sites (cDHSs)* to the enum list for *input_file_types* and *output_file_types*
* Added *pseudoalignment based quantification* to the enum list for *analysis_step_types*
* Added *chromosomes reference*, *FDR cut rate*, *footprints*, *hotspots1 reference*, *hotspots2 reference*, *mitochondrial genome index*, and *mitochondrial genome reference* to the enum list for *input_file_types* and *output_file_types*
* Added *fastq demultiplexing* and *gRNA generation* to the enum list for *analysis_step_types*
* Added *chromosome sizes*, *ranked gRNAs*, *enhancers reference*, *promoters reference*, *DHS regions reference*, *merged transcription segment quantifications*, *transcription segment quantifications*, *transcribed region quantifications*, and *smoothed methylation stage at CpG* to the enum list for *input_file_types* and *output_file_types*
* Added *pseudo-replicated peaks* to the enum list for *input_file_types* and *output_file_types*

### Schema version 9
* Updated *representative dnase hypersensitivity sites* to *representative DNase hypersensitivity sites (rDHSs)* in enums for *output_file_types* and *input_file_types*.

### Minor changes since schema version 8
* *input_file_types* and *output_file_types* were updated to have the following enum term(s) to match File schema: *miRNA annotations*, *personalized genome assembly*.
* *personalized genome assembly* was also added to the enum list for *analysis_step_types*.
* The following enums were added to the list for *input_file_types* and *output_file_types*:
        [
            "regulatory elements",
            "negative control regions",
            "non-targeting gRNAs",
            "positive control regions",
            "safe-targeting gRNAs",
            "subreads"
        ]
* *gRNAs* was added to the enum list of *input_file_types* and *output_file_types*.
* *element quantifications* was added to the enum list of *input_file_types* and *output_file_types*.
* *elements reference* was added to the enum list of *input_file_types* and *output_file_types*.

### Schema version 8

* Add enum value *pseudoreplicated IDR* to *analysis_step_types*
* Add enum values *IDR ranked peaks* and *IDR thresholded peaks* for *input_file_types* and *output_file_types*
* Change enum value *conservative idr thresholded peaks* in *input_file_types* and *output_file_types* to *conservative IDR thresholded peaks*
* Change enum value *optimal idr thresholded peaks* in *input_file_types* and *output_file_types* to *optimal IDR thresholded peaks*
* Change enum value *pseudoreplicated idr thresholded peaks* in *input_file_types* and *output_file_types* to *pseudoreplicated IDR thresholded peaks*

### Minor changes since schema version 7

* *input_file_types* and *output_file_types* were updated to have the following enum terms to match File schema: *transcriptome annotations*, *sequence barcodes* and *sequence adapters*
* *analysis_step_type* were updated to have the following enum terms *transcriptome annotation* and *barcodes mapping generation*

### Schema version 7

* Changed enum value *candidate regulatory elements* in *input_file_types* and *output_file_types* to *candidate Cis-Regulatory Elements*

### Minor changes since schema version 6

* *input_file_types* and *output_file_types* were updated to have the following enum terms to match File schema: *differential expression quantifications*, *differential splicing quantifications*, *peaks and background as input for IDR*, and *gene alignments*.

* *major_version* was set to have a minimum of 1.

* Added *enrichment* to *analysis_step_types* enums.

* Added *long-read sequencing error correction* to *analysis_step_types* enums.

* Added *splice junction extraction* to *analysis_step_types* enums.

### Schema version 6

* *status* property was restricted to one of  
    "enum" : [
        "in progress",
        "deleted",
        "released"
    ]
* *name* has been renamed to *step_label*. The *name* property will now be a calculated name with the *major_version* number.
* *major_version* number property has been added and made required so all steps must be versioned, starting from 1.
* All new analysis steps should be accompanied by a new step version object as well.


### Schema version 5

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 4

* *analysis_step_types*, *input_file_types*, *output_file_types*, *qa_stats_generated*, *parents*, *aliases*, *documents* arrays must contain unique elements.

### Schema version 3

* *output_file_types* and *input_file_types* were updated to have more accurate terms:

        "mapping": {
            'minus strand signal of multi-mapped reads': 'minus strand signal of all reads',
            'plus strand signal of multi-mapped reads': 'plus strand signal of all reads',
            'signal of multi-mapped reads': 'signal of all reads',
            'normalized signal of multi-mapped reads': 'normalized signal of all reads'
        }
* *software_versions* was migrated to *analysis_step_versions.software_versions*
* *parents* is now assumed to be a unique path to pipeline
* *name* and *title* needs to include the major version of the analysis_step
* *analysis_step_versions* point to *analysis_step* but are not a calcuated list
* *current_version* is a calculated property pointing to an *analysis_step_version* based on the the highest value of *analysis_step_version.version*
* *pipeline* is calculated from the listing in pipeline of *analysis_steps*
