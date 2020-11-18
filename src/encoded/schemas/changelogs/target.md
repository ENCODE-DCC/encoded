## Changelog for target.json

### Minor changes since schema version 14

* Removed dependency restricting *dbxrefs* to non-gene targets. *dbxrefs* value formatting is now enforced with regex for UniProtKB and FactorBook.

### Schema version 14

* Property *dbxref* was renamed to *dbxrefs* and restricted to non-gene targets.

### Schema version 13

* *investigated_as* enum list was modified. The following terms were removed:
  - *recombinant protein*

### Schema version 12
* *investigated_as* enum list was modified. The following terms were removed:
  - *control*
* *TagRFP* was added to the type of modifications enum list in *modifications* property.

### Schema version 11

* *investigated_as* enum list was modified. The following terms were removed:
  - *nucleotide modification*
  - *other post-translational modification*

  and the following terms were added:
  - *Co-factor*
  - *Cohesin*
  - *DNA replication*
  - *DNA repair*
  - *RNA polymerase complex*

### Schema version 10

* Property modifications depends on genes and the default for modifications is removed. In other words, only gene targets can have modifications.
* Added *synthetic tag* and oneOf keyword to address synthetic targets (FLAG) properly.
* Added *Ubiquitination* to target.modifications.modification enum.

### Schema version 9

* Added *genes* property for the list of genes targeted by assay or antibody associated with the target.
* Removed the *gene_name* property.
* The *organism* property is now a calculated property. The organism of a target is either specified directly through the new *target_organism* property or defined indirectly by its target genes. The *target_organism* property and the *genes* property are mutually exclusive.
* Added *modification* property to represent modification(s) made to the corresponding wild-type gene product.

### Schema version 8

* Move *status* property to *standard_status* mixin.

### Schema version 7

* Remove *histone modification* from *investigated_as* enum.

### Schema version 6

* Remove *proposed* from *status* enum.

### Schema version 5

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as * # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 4

* Array properties *aliases*, *dbxref*, and *investigated* were updated to allow for only unique elements within them.

### Schema version 3

* *investigated_as* property was backfilled to assign existing targets the appropriate enums according to what the target was being investigated as within an assay

### Schema version 2

* *status* values were changed to be lowercase
