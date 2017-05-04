## Changelog for analysis_step.json

### Schema version 5

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ ! $ ^ & | ~ ; ` and consecutive whitespaces will no longer be allowed in the alias

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
