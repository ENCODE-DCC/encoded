## Changelog for annotation.json

### Schema version 12
    
* *biosample_type* and *biosample_term_id* consistency added to the list of schema dependencies

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