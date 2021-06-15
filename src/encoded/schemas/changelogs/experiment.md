## Changelog for experiment.json

### Schema version 36
* Added *LC/MS label-free quantitative proteomics*, *LC-MS/MS isobaric label quantitative proteomics*, and *Ribo-seq* to *assay_term_name* enum. *assay_term_name* enum *Capture Hi-C* was changed to *capture Hi-C*

### Schema version 35
* Updated the *internal_tags* enum from *RegulomeDB* to *RegulomeDB_1_0*
* Added *RegulomeDB_2_0* and *RegulomeDB_2_1* to the *internal_tags* enum list.

### Minor changes since schema version 34
* Added *ENCYCLOPEDIAv6* to *internal_tags* enums list
* Added *RushAD* and *YaleImmuneCells* to the *internal_tags* enum

### Schema version 34
* Changed the *analysis_objects* property to be *analyses*

### Schema version 33
* Removed *single-cell ATAC-seq* from *assay_term_name* enum and remapped to *single-nucleus ATAC-seq*

### Schema version 32

* Added *GRO-cap*, *GRO-seq*, and *long read single-cell RNA-seq* to *assay_term_name* enum;  *single-nucleus RNA-seq* and *genotyping by high throughput sequencing assay* were removed and remapped to *single-cell RNA sequencing assay* and *whole genome sequencing assay* respectively

### Minor changes since schema version 31
* Added *Capture Hi-C* and *single-nucleus RNA-seq* to *assay_term_name* enum
* Added *LRGASP* to the *internal_tags* enum
* Added *doi* property

### Schema version 31

* Removed the *analyses* property.

### Minor changes since schema version 30
* Added *analysis_objects* property.
* Added *SPRITE-IP* to *assay_term_name* enum
* Added *life_stage_age* calculated property that summarizes the life stage and age of the biosamples used in the experiment.
* Small RNA-seq experiments (with libraries of fragments <200 nucleotides long) may be submitted with *assay_term_name* enum: *small RNA-seq*.
* Added *CUT&Tag* to *assay_term_name* enum
* *SCREEN-GRCh38* and *SCREEN-mm10* can now be linked to an experiment under external resources (dbxrefs).

### Schema version 30

* *assay_term_name* enum *single cell isolation followed by RNA-seq* was changed to *single-cell RNA sequencing assay*

### Minor changes since schema version 29
* Added *wild type* enum to *control_type*

### Schema version 29

* The *internal_status* enum was adjusted to remove *requires lab review* and *unrunnable*; *pre-pipeline review* and *post-pipeline review* were added.

### Minor changes since schema version 28

* Removed FCC *assay_term_name* enums *STARR-seq*, *MPRA*, *CRISPR screen*, and *pooled clone sequencing* from Experiment schema. They are to be used only in FunctionalCharacterizationExperiment objects
* Removed *month_released* calculated property.
* Added *analyses* property.
* Added *protein_tags* calculated property that specifies the protein tags introduced through genetic modification of the biosamples investigated in the experiment.
* *FactorBook* can now be linked to an experiment under external resources (dbxrefs).
* Added *analyses.assemblies*, *analyses.genome_annotations* and *analyses.pipelines* calculated property.

### Schema version 28

* Removed required property *experiment_classification*.

### Schema version 27

* *assay_term_name* enum *single-nuclei ATAC-seq* was changed to *single-nucleus ATAC-seq*

### Minor changes since schema version 26

* Added *MouseDevSeries* enum to *internal_tags*
* *assay_term_name* enums *STARR-seq*, *MPRA*, *CRISPR screen* and *pooled clone sequencing* is restricted for submission by admins only.
* *experiment_classification* *functional characterization assay* is restricted for specification and submission by admins only.
* Added *control_type*

### Schema version 26

* Replace *ISO-seq* with *long read RNA-seq* in *assay_term_name*.

### Schema version 25

* Remove *biosample_type*, *biosample_term_id* and *biosample_term_name*.

### Schema version 24

* *internal_tags* removes *cre_inputv10* and *cre_inputv11*, and adds *ENCYCLOPEDIAv5*, *ccre_inputv1*, and *ccre_inputv2*.

### Schema version 23

* Link to BiosampleType object.

### Schema version 22

* Removed *induced pluripotent stem cell line* and *stem cell* from *biosample_type* enums.

### Schema version 21

* Added required property *experiment_classification* with enums *functional genomics assay* and *functional characterization assay*

### Minor changes since schema version 20

* *possible_controls* property allows specification of any type of Dataset as possible control

### Schema version 20

* Added *organoid* to *biosample_type* enums.

### Schema version 19

* Make *date_submitted* value a required property for objects in status *submitted*

### Schema version 18

* Replace enum *started* in *status* with *in progress*.

### Schema version 17

* Replace the *status* field value *ready for review* by *submitted*. Make the *status* field editable by DCC personnel only.
* Added *single cell* to *biosample_type* enums

### Schema version 16

* Replace *immortalized cell line* with *cell line* in *biosample_type* enum

### Schema version 15

* The *biosample_type* enum *in vitro sample* has been renamed to *cell-free sample* and requires an accompanying *biosample_term_id* (of type NTR)

### Schema version 14

* Remove *proposed* from *status* enum (*dataset* mixin).

### Schema version 13

* *biosample_type* property is required
* *biosample_term_id* is required for all experiments except experiment with *biosample_type* *in vitro sample*, consistency between the biosample type and ontology *term_id* is validated by schema dependency


### Schema version 12

* *alternate_accessions* now must match accession format, "ENCSR..." or "TSTSR..."
* *date_submitted* property was added to indicate when submission requirements were met. This value is assigned by the DCC.

### Schema version 11
    
* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias


### Schema version 10

* *assay_term_name* is now a required property
* *assay_term_id* is no longer allowed to be submitted, it will be automatically calculated based on the *term_name*

### Schema version 9

* *status* enum was restricted to:
    "enum" : [
        "proposed",
        "started",
        "submitted",
        "ready for review",
        "deleted",
        "released",
        "revoked",
        "archived",
        "replaced"
    ]

### Schema version 8

* Array properties *possible_controls*, *dbxrefs*, *aliases*, *references*, and *documents* were updated to allow for only unique elements within them.


### Schema version 5

* *biosample_type* enum value changed from *primary cell line* to *primary cell*.
