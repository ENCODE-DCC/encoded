## Changelog for annotation.json

### Minor changes since schema version 25
* Added MouseDevSeries to *internal_tags*

### Schema version 25

* Changed enum value *candidate regulatory elements* in *annotation_type* to *candidate Cis-Regulatory Elements*

### Schema version 24

* Adds *annotation_type* imputation and makes *annotation_type* required.

### Schema version 23

* Remove biosample_type, biosample_term_id and biosample_term_name.

### Schema version 22

* *internal_tags* removes cre_inputv10 and cre_inputv11, and adds ENCYCLOPEDIAv5, ccre_inputv1, and ccre_inputv2.

### Schema version 21

* Link to BiosampleType object.

### Schema version 20

* Removed *induced pluripotent stem cell line* and *stem cell* from biosample_type enums.

### Schema version 19

* Added *organoid* to biosample_type enums.

### Schema version 18

* Replace started status with in progress.

### Minor changes since schema version 17

* Added *single cell* to biosample_type enums

### Schema version 17

* Replace *immortalized cell line* with *cell line* in biosample_type enum

### Schema version 16

* Remove enhancer- and promoter-like regions from annotation_type (now candidate regulatory elements)
* Remove DNase master peaks from annotation_type (now representative DNase hypersensitivity sites)

### Schema version 15

* Remove *proposed* from status enum (dataset mixin)

### Schema version 14

* *biosample_type* and *biosample_term_id* consistency added to the list of schema dependencies

### Schema version 13

* *annotation_type* 'candidate regulatory regions' was changed into 'candidate regulatory elements'

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
