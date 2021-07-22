## Changelog for single_cell_rna_series.json

### Minor changes since schema version 3

* Added *LRGASP* to the *internal_tags* enum
* Added *doi* property
* Added *analyses* property
* *related_datasets* now includes SingleCellUnit.json
* Added *assay_slims* calculated property
* Added *RushAD* and *YaleImmuneCells* to the *internal_tags* enum
* Added *biosample_summary* calculated property

### Schema version 3

* Update the dbxref regex to remove IHEC; this is only allowed for Annotation and ReferenceEpigenome objects

### Schema version 2

* Update IHEC dbxref regex to remove version number
