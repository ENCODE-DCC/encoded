## Changelog for genetic_modification.json

### Schema version 11
* Added *MOI* (multiplicity of infection) and *guide_type* properties.
* *guide_type* is a required property when *introduced_elements* specifies *gRNAs and CRISPR machinery*

### Minor changes since schema version 10

* A combination of method *CRISPR* with the category of *mutagenesis* and purpose *characterization* may be submitted to describe a genetic modification.
* The *identifier* regular expression in the *reagents* property was updated to include identifiers from the source GenBank:
  * GenBank: '^genbank:[A-Z]{1,2}\\d{5,6}\\.\\d{1}$', e.g., genbank:MK484105.1
* *mAID* was added to the *introduced_tags* enum.
* Added *promoter_details* to the *reagents* property.

### Schema version 10

* Moved the following enum values from *method* to a new property, *nucleic_acid_delivery_method*. Genetic modifications must specify at least one of *method* or *nucleic_acid_delivery_method*.
 - bombardment
 - microinjection
 - stable transfection
 - transduction
 - transient transfection
 - mouse pronuclear microinjection
* The *donor* property was renamed to *introduced_elements_donor*.
* Added new property *introduced_elements_organism*.

### Minor changes since schema version 9

* Added *disruption*, *inhibition*, and *knockout* as enums in *category* for use with CRISPR screen data.
* Added *homologous recombination* as enum in *method*, to be used with the *category* of *knockout* and the *purpose* of *repression*.
* Added *gRNAs and CRISPR machinery* to *introduced_elements* enum, to indicate the first step in a CRISPR screen.
* Added *binding* and *transgene insertion* to *category* enum, *mouse pronuclear microinjection* to *method* enum, and *in vivo enhancer characterization* to *purpose* enum.
* Modified the *identifier* regular expression for Thermo Fisher within *reagents* to accept identifiers with 7 digits.
  * Thermo Fisher: '^thermo-fisher:[a-zA-Z]{1,3}\\d{5,7}$', ex. thermo-fisher:L3000008

### Schema version 9

* Several underused *purpose* enum were combined: *activation* and *overexpression* are remapped to *expression*, and *analysis* and *screening* are remapped to *characterization*.
* A combination of method *CRISPR* with the category of *activation* or *interference* and purpose *characterization* may be submitted to specify a collective set of modifications intended for a CRISPRa or CRISPRi screen.

### Minor changes since schema version 8
* *TagRFP* was added to the *introduced_tags* enum.
* Added calculated property *perturbed* to indicate genetic modifications which cause genetic perturbations.
* *donor* property was added to allow specification of the origin of the sheared genomic DNA elements or genomic DNA regions
* *non-specific target control* was added to the *purpose* enum.
* *genomic DNA regions* was added to the *introduced_elements* enum to describe selected regions derived from donor DNA

### Schema version 8

* A combination of *introduced_elements* and *modified_site_nonspecific* can satisfy the *category* dependency for *insertion*.
* *episome* was added to the *category* enum, and modifications with this *category* require the *introduced_elements* property.
* The *introduced_elements* property was added for characterization of groups of elements.
* A minimum of 0 is set for *start* and *end* in *modified_site_by_coordinates*
* The dependency of *method* on *reagents* specification was changed, *reagents* are no longer required to be specified for the relevant types of modification methods.
* *zygosity* is now required for modifications of *method* TALEN
* The *introduced_gene* property was added, and can satisfy the *category* dependencies for modifications of *category* insertion.
* *expression* was added to the *purpose* enum, and modifications with this *purpose* require *introduced_sequence* or *introduced_gene*.
* Within *reagents*, an *identifier* is no longer allowed to be free text and must conform to the pattern. Listed below are indivdual sources, their corresponding *identifier* regular expressions, and examples of allowed identifiers. Note that the
identifier is prefixed by 'source-name:'.
  * Addgene: '^addgene:\\d{5,6}$', ex. addgene:12345, addgene:123456
  * BACPAC: '^bacpac:([A-Z]{2,3}\\d{2,3}|[A-Z]{3})-\\d{1,4}[A-Z]\\d{1,2}$', ex. bacpac:CH17-232B19, bacpac:RP11-722H2
  * Brenton Graveley: '^brenton-graveley:BGC#\\d{7}$', ex. brenton-graveley:BGC#0000007
  * Dharmacon: '^dharmacon:[DL]-\\d{6}-\\d{2}(-\\d{2,4})?$', ex. dharmacon:D-001810-10-05, dharmacon:L-006690-00
  * Hugo Bellen: '^hugo-bellen:MI\\d{5}$', ex. hugo-bellen:MI06350
  * Human Orfeome: '^human-orfeome:([A-Z]{2})?\\d{1,9}$', ex. human-orfeome:100068273, human-orfeome:867, human-orfeome:BC009921
  * Plasmid Repository: '^plasmid-repository:HsCD\\d{8}$', ex. plasmid-repository:HsCD00040564
  * Sigma: '^sigma:[A-Z]{3}\\d{3}$', ex. sigma:SHC002
  * Source BioScience: '^source-bioscience:[A-Z]{3}\\d{3,4}[a-z][A-Z]\\d{2}(\_[A-Z]\\d{2})?$', ex. source-bioscience:WRM0610bH03, source-bioscience:WRM061aG12
  * Thermo Fisher: '^thermo-fisher:[a-zA-Z]{1,3}\\d{5,6}$', ex. thermo-fisher:P36238, thermo-fisher:V601020
  * TRC: '^trc:TRCN\\d{10}$', ex. trc:TRCN0000001243

### Minor changes since schema version 7

* A minimum of 0 is set for *start* and *end* in *modified_site_by_coordinates*
* The dependency of *method* on *reagents* specification was changed, *reagents* are no longer required to be specified for the relevant types of modification methods.
* The *introduced_gene* property was added, and can satisfy the *category* dependencies for modifications of *category* insertion.
* *expression* was added to the *purpose* enum, and modifications with this *purpose* require *introduced_sequence* or *introduced_gene*.

### Schema version 7

* *purpose* property *validation* was renamed to *characterization*, and *screening* was also added to the list of enums

### Schema version 6

* Genetic modifications are now accessioned objects with accessions starting with "ENCGM"
* *method* and *purpose* are now required properties
* *modification_type* has been renamed to *category*
* *target* has been renamed to *modified_site_by_target_id*
* linkOuts to CRISPR and TALEN objects have been removed, the relevant properties in those objects have been absorbed into this one and techniques are listed as enums within *method*
* *modified_site* has been renamed to *modified_site_by_coordinates*
* *source* and *product id* have been renamed to be an array of subobjects with those equivalent properties (*source* and *identifier*) within a property named *reagents*. Note that these values are meant to capture the reagents used to create the resultant modification.

### Schema version 5

* *status* property was restricted to one of  
    "enum" : [
        "in progress",
        "deleted",
        "released"
    ]

### Schema version 4

* *aliases* now must be properly namespaced according lab.name:alphanumeric characters with no leading or trailing spaces
* unsafe characters such as " # @ % ^ & | ~ ; ` [ ] { } and consecutive whitespaces will no longer be allowed in the alias

### Schema version 3

* *modified_site* was renamed from *modification_genome_coordinates*
* if *modified_site* is used, all subproperties (*assembly*, *chromosome*, *start* and *end*) are required
* *description* was renamed from *modification_description*
* *purpose* was renamed from *modification_purpose*
* *zygosity* was renamed from *modification_zygocity*
* *treatments* was renamed from *modification_treatments*

### Schema version 2

* *modification_description* was renamed from *modifiction_description*
