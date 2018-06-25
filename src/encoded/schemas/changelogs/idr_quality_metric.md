## Changelog for idr_quality_metric.json

### Minor change

* *size*, *width*, and *height* in *IDR_plot_true* were set to have a minimum of 0.
* *size*, *width*, and *height* in *IDR_plot_rep1_pr* were set to have a minimum of 0.
* *size*, *width*, and *height* in *IDR_plot_rep2_pr* were set to have a minimum of 0.
* *size*, *width*, and *height* in *IDR_plot_pool_pr* were set to have a minimum of 0.
* *size* in *IDR_parameters_true*, *IDR_parameters_rep1_pr*, *IDR_parameters_rep2_pr*, *IDR_parameters_pool_pr* were set to have a minimum of 0.


### Schema version 6

* *status* property was restricted to one of  
    "enum" : [
        "in progress",
        "deleted",
        "released"
    ]

### Schema version 5

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 4

* *assay_term_id* is no longer allowed to be submitted, it will be automatically calculated based on the term_name
* *notes* field is no longer allowed to have leading or trailing whitespace or contain just an empty string.

### Schema version 2

* *award* and *lab* were added as required fields
