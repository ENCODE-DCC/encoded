## Changelog for ataqseq_quality_metric.json

### Schema version 6

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % $ ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 5

Introduction of a new schema for quality metrics calculated by the ENCODE ATAC-seq pipeline.