## Changelog for analysis_step.json

### Schema version 7

* *input_file_types* and *output_file_types* were updated to have the following three more enum terms to match File schema: "differential expression quantifications", "differential splicing quantifications", "peaks and background as input for IDR".

* *major_version* was set to have a minimum of 1.

### Schema version 6

* *status* property was restricted to one of  
    "enum" : [
        "in progress",
        "deleted",
        "released"
    ]
* *name* has been renamed to *step_label*. The *name* property will now be a calculated name with the major_version number.
* *major_version* number property has been added and made required so all steps must be versioned, starting from 1.
* all new analysis steps should be accompanied by a new step version object as well.


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
* *pipeline* is calcualted from the listing in pipeline of *analysis_steps*
