## Changelog for annotation.json

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
