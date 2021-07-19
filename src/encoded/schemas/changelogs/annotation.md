## Changelog for annotation.json

### Minor changes since schema version 33
* Added *simple_biosample_summary* truncated version of biosample_summary as calculated property
* Added *calf*, *child*, *mixed stage*, and *newborn* to *relevant_life_stage* enums list
* Added *RushAD* and *YaleImmuneCells* to the *internal_tags* enum
* Added *LC/MS label-free quantitative proteomics*, *LC-MS/MS isobaric label quantitative proteomics*, and *Ribo-seq* to *assay_term_name* enum. *assay_term_name* enum *Capture Hi-C* was changed to *capture Hi-C*
* Added *DHS* to the *annotation_subtype* enum, and restricted submission of the property to admin only
* Added ** enum to *annotation_type* property

### Schema version 33
* Updated the *internal_tags* enum from *RegulomeDB* to *RegulomeDB_1_0*
* Added *RegulomeDB_2_0* and *RegulomeDB_2_1* to the *internal_tags* enum list.

### Minor changes since schema version 32
* Added *ENCYCLOPEDIAv6* to *internal_tags* enums list

### Schema version 32
* Changed the *analysis_objects* property to be *analyses*

### Schema version 31
* Changed *blacklist* to *exclusion list* in enum for *annotation_type*

### Minor changes since schema version 30
* Added *curated SNVs*, *dsQTLs*, *eQTLs*, *footprints* and *PWMs* enum to *annotation_type* property.
* Added *doi* property
* Added *analysis_objects* property.
* Added *GRO-cap*, *GRO-seq*, and *long read single-cell RNA-seq* to *assay_term_name* enum;  *single-nucleus RNA-seq* and *genotyping by high throughput sequencing assay* were removed and remapped to *single-cell RNA sequencing assay* and *whole genome sequencing assay* respectively
* Removed *single-cell ATAC-seq* from *assay_term_name* enum and remapped to *single-nucleus ATAC-seq*
* Added *fine-mapped variants* enum to *annotation_type* property.
* Added a new property, *annotation_subtype*, to specify the elements in a *candidate Cis-Regulatory Elements* annotation object

### Minor changes since schema version 30
* Added *LRGASP* to the *internal_tags* enum

### Schema version 30
* Updated *representative DNase hypersensitivity sites (rDHSs)*  to *representative DNase hypersensitivity sites* in enum for *annotation_type*

### Minor changes since schema version 29
* The *biochemical_inputs* calculated property now lists the biochemical signal inputs used to generate a candidate Cis-Regulatory Elements (cCRE) annotation.

### Schema version 29
* Remove enum *stage* from *relevant_timepoint* property.

### Schema version 28
* Updated *representative DNase hypersensitivity sites* to *representative DNase hypersensitivity sites (rDHSs)* in enum for *annotation_type*.

### Minor changes since schema version 27
* Added ENCODE v6 to the list of enums within *encyclopedia_version* property.

### Schema version 27

* Update IHEC dbxref regex to remove version number

### Minor changes since schema version 26
* Added *functional characterization elements* and *transcription start sites* enum to *annotation_type* property.
* Added *assay_term_name* property.

### Schema version 26
* Altered *encyclopedia_version* from free text to an enum list of terms, including a new specification for ENCODE v5.

### Minor changes since schema version 25
* Added *MouseDevSeries* enum to *internal_tags*
* Added *consensus DNase hypersensitivity sites* enum to *annotation_type*
* Removed *month_released* calculated property.

### Schema version 25

* Changed enum value *candidate regulatory elements* in *annotation_type* to *candidate Cis-Regulatory Elements*

### Schema version 24

* Adds *annotation_type* imputation and makes *annotation_type* required.

### Schema version 23

* Remove *biosample_type*, *biosample_term_id* and *biosample_term_name*.

### Schema version 22

* *internal_tags* removes *cre_inputv10* and *cre_inputv11*, and adds *ENCYCLOPEDIAv5*, *ccre_inputv1*, and *ccre_inputv2*.

### Schema version 21

* Link to BiosampleType object.

### Schema version 20

* Removed *induced pluripotent stem cell line* and *stem cell* from *biosample_type* enums.

### Schema version 19

* Added *organoid* to *biosample_type* enums.

### Schema version 18

* Replace *started* enum in *status* with *in progress*.

### Minor changes since schema version 17

* Added *single cell* to *biosample_type* enums

### Schema version 17

* Replace *immortalized cell line* with *cell line* in *biosample_type* enum

### Schema version 16

* Remove *enhancer-* and *promoter-like regions* from *annotation_type* (now *candidate regulatory elements*)
* Remove *DNase master peaks* from *annotation_type* (now *representative DNase hypersensitivity sites*)

### Schema version 15

* Remove *proposed* from *status* enum (*dataset* mixin)

### Schema version 14

* *biosample_type* and *biosample_term_id* consistency added to the list of schema dependencies

### Schema version 13

* *annotation_type* *candidate regulatory regions* was changed into *candidate regulatory elements*

### Schema version 12

* *alternate_accessions* now must match accession format, "ENCSR..." or "TSTSR..."

### Schema version 11

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 10

* *description*, *notes*, and *submitter_comment* are now not allowed to have any leading or trailing whitespace

### Schema version 9

* *annotation_type* was changed to be the following list
 
        "enum": [
                "binding sites",
                "blacklist",
                "chromatin state",
                "enhancer-like regions",
                "promoter-like regions",
                "enhancer predictions",
                "DNase master peaks",
                "transcription factor motifs",
                "validated enhancers",
                "overlap",
                "other"
        ]
