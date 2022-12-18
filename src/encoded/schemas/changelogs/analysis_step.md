## Changelog for analysis_step.json

### Schema version 16
* *input_file_types* and *output_file_types* enums *topologically associated domains*, *chromatin interactions*, *DNA accessibility raw signal*, *long range chromatin interactions*, *nested topologically associated domains*, *allele-specific chromatin interactions*, *variants chromatin interactions*, *haplotype-specific chromatin interactions*, *haplotype-specific DNA accessibility raw signal*, and *haplotype-specific DNA accessibility corrected signal* were replaced by *contact domains*, *contact matrix*, *nuclease cleavage frequency*, *loops*, *nested contact domains*, *allele-specific contact matrix*, *variants contact matrix*, *haplotype-specific contact matrix*, *haplotype-specific nuclease cleavage frequency* and *haplotype-specific nuclease cleavage corrected frequency* respectively.
* Added *mapping quality thresholded contact matrix*, *variant effect quantifications* to the enum list for *input_file_types* and *output_file_types*.
* *analysis_step_types* enum *topologically associated domain identification* was replaced with *contact domain identification*

### Minor changes since schema version 15
* Added *merging* to the enum list for *analysis_step_types*
* Added *curated binding sites*, *curated SNVs*, *dsQTLs*, *eQTLs* and *PWMs* to the enum list for *input_file_types* and *output_file_types*
* Added *sparse transcript count matrix* and *read annotations* to the enum list for *input_file_types* and *output_file_types*
* Added *sparse gRNA count matrix*, *element barcode mapping*, and *fine-mapped variants* to the enum list for *input_file_types* and *output_file_types*
* Added *repeat elements annotation* to the enum list for *input_file_types* and *output_file_types*
* Added *R2C2 subreads* to the enum list for *input_file_types* and *output_file_types*
* Added *guide locations* to the enum list for *input_file_types* and *output_file_types*
* Added *pairs* to the enum list for *input_file_types* and *output_file_types*
* Added several entries to the enum lists for *input_file_types* and *output_file_types*: *allele-specific chromatin interactions, allele-specific variants, bidirectional peaks, diploid personal genome alignments, haplotype-specific alignments, novel peptides, peptide quantifications, protein expression quantifications, unidirectional peaks*
* Added *polyA sites* to the enum list for *input_file_types* and *output_file_types*
* Added *redacted alignments* and *redacted transcriptome alingments* to the enum list for *input_file_types* and *output_file_types*
* Added *fragments* to the enum list for *input_file_types* and *output_file_types*
* Added *genome compartment identification* to the enum list for *analysis_step_types*
* Added *sparse peak count matrix* to the enum lists for *input_file_types* and *output_file_types*
* Added *functional conservation quantifications* to the enum lists for *input_file_types* and *output_file_types*
* Added *regulatory elements prediction model* to the enum lists for *input_file_types* and *output_file_types*
* Added *genome subcompartments* and *chromatin stripes* to the enum lists for *input_file_types* and *output_file_types*
* Added *TF binding prediction model*, *enhancer prediction model* and *promoter prediction model* to the enum lists for *input_file_types* and *output_file_types*
* Added *filtered reads* and *archr project* to the enum lists for *input_file_types* and *output_file_types*
* Added *inclusion list*, *sparse gene count matrix of all reads*, *sparse gene count matrix of unique reads*, *unfiltered sparse gene count matrix of all reads*, *unfiltered sparse gene count matrix of unique reads*, and *unfiltered sparse splice junction count matrix of unique reads* to the enum lists for *input_file_types* and *output_file_types*
* Added *kmer weights* and *training set* to the enum lists for *input_file_types* and *output_file_types*
* Added *functional conservation mapping* to the enum lists for *input_file_types* and *output_file_types*
* Added *3D structure* and *DNA accessibility raw signal* to the enum lists for *input_file_types* and *output_file_types*
* Added *variants chromatin interactions*, *haplotype-specific chromatin interactions*, *haplotype-specific DNA accessibility raw signal*, *haplotype-specific DNA accessibility corrected signal* to enum list for *input_file_types* and *output_file_types*.
* Added *cell coordinates*, *cell type annotations*, and *raw imaging signal* to enum list for *input_file_types* and *output_file_types*.
* Added *plus strand end position signal*, *minus strand end position signal*, *plus strand normalized end position signal*, and *minus strand normalized end position signal* to enum list for *input_file_types* and *output_file_types*.
* Added *cell type annotation* to the enum list for *analysis_step_types*.
* Added *DNN-MPRA contribution scores*, *DNN-MPRA predicted signal*, *element gene links*, and *thresholded element gene links* to enum list for *input_file_types* and *output_file_types*.
* Added *element gene link prediction* and *selection* to the enum list for *analysis_step_types*.
* Added *contribution score calculation*, *model generation*, and *sequence motif prediction* to the enum list for *analysis_step_types*
* Added the following enums to enum list for *input_file_types* and *output_file_types*:
  * *bias-corrected predicted signal profile*
  * *counts sequence contribution scores*
  * *model performance metrics*
  * *models*
  * *observed bias profile*
  * *observed control profile (minus strand)*
  * *observed control profile (plus strand)*
  * *observed signal profile*
  * *observed signal profile (minus strand)*
  * *observed signal profile (plus strand)*
  * *predicted bias profile*
  * *predicted profile*
  * *predicted signal profile (minus strand)*
  * *predicted signal profile (plus strand)*
  * *profile sequence contribution scores*
  * *selected regions for bias-corrected predicted signal profile*
  * *selected regions for count sequence contribution scores*
  * *selected regions for predicted signal profile*
  * *selected regions for predicted bias profile*
  * *selected regions for predicted signal profile (minus strand)*
  * *selected regions for predicted signal profile (plus strand)*
  * *selected regions for profile sequence contribution scores*
  * *sequence motifs*
  * *sequence motifs report*
  * *sequence motifs instances*
  * *training and test regions*
* Added *cell type data* to the enum lists for *input_file_types* and *output_file_types*.
* Added *enhancer-gene links* and *thresholded links* to the enum lists for *input_file_types* and *output_file_types*.
* Added *depth normalized signals matrix*, *z scores matrix*, and *TF peaks matrix* to the enum lists for *input_file_types* and *output_file_types*.

### Schema version 15
* *input_file_types*, *output_file_types* enums *blacklisted regions* and *mitochondria blacklisted regions* were replaced by *exclusion list regions* and *mitochondrial exclusion list regions* respectively 
* Added *nanopore signal* to the enum list for *input_file_types*
* Added *index reads* to the enum list for *input_file_types*
* Added *guide quantifications*, *perturbation signal*, *element gene interactions signal*, and *element gene interactions p-value* to the enum list for *input_file_types* and *output_file_types*

### Schema version 14
* *input_file_types: pseudo-replicated peaks* was updated to *input_file_types: pseudoreplicated peaks*
* *output_file_types: pseudo-replicated peaks* was updated to *output_file_types: pseudoreplicated peaks*
* Added *capture targets* to the enum list for *input_file_types* and *output_file_types*

### Schema version 13
* *input_file_types*, *output_file_types* enums *consensus DNase hypersensitivity sites (cDHSs)* and *representative DNase hypersensitivity sites (rDHSs)* was updated to *consensus DNase hypersensitivity sites* and *representative DNase hypersensitivity sites* respectively.

### Minor changes since schema version 12
* Added *gene stabilities* and *preprocessed alignments* to the enum list for *input_file_types* and *output_file_types*

### Schema version 12
* *input_file_types* and *output_file_types* *smoothed methylation stage at CpG* was updated to *smoothed methylation state at CpG*

### Minor changes since schema version 11
* Added *genotyping*, *methylation estimation* and *smoothing* to the enum list for *analysis_step_types*
* Added *UV enriched segment quantifications*, *plus strand methylation state at CpG*, *minus strand methylation state at CpG*, *CpG sites coverage*, and *sparse gene count matrix* to the enum list for *input_file_types* and *output_file_types*

### Schema version 11
* *input_file_types: stable peaks* was updated to *input_file_types: pseudo-replicated peaks*
* *output_file_types: stable peaks* was updated to *output_file_types: pseudo-replicated peaks*

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
