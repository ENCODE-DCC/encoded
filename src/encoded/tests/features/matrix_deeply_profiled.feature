@matrix
Feature: Matrix
    Background:
        When I visit "/deeply-profiled-matrix/?type=Experiment&control_type!=*&status=released&replicates.library.biosample.biosample_ontology.term_id=EFO:0002106&replicates.library.biosample.biosample_ontology.term_id=EFO:0001203&replicates.library.biosample.biosample_ontology.term_id=EFO:0006711&replicates.library.biosample.biosample_ontology.term_id=EFO:0002713&replicates.library.biosample.biosample_ontology.term_id=EFO:0002847&replicates.library.biosample.biosample_ontology.term_id=EFO:0002074&replicates.library.biosample.biosample_ontology.term_id=EFO:0001200&replicates.library.biosample.biosample_ontology.term_id=EFO:0009747&replicates.library.biosample.biosample_ontology.term_id=EFO:0002824&replicates.library.biosample.biosample_ontology.term_id=CL:0002327&replicates.library.biosample.biosample_ontology.term_id=CL:0002618&replicates.library.biosample.biosample_ontology.term_id=EFO:0002784&replicates.library.biosample.biosample_ontology.term_id=EFO:0001196&replicates.library.biosample.biosample_ontology.term_id=EFO:0001187&replicates.library.biosample.biosample_ontology.term_id=EFO:0002067&replicates.library.biosample.biosample_ontology.term_id=EFO:0001099&replicates.library.biosample.biosample_ontology.term_id=EFO:0002819&replicates.library.biosample.biosample_ontology.term_id=EFO:0009318&replicates.library.biosample.biosample_ontology.term_id=EFO:0001086&replicates.library.biosample.biosample_ontology.term_id=EFO:0007950&replicates.library.biosample.biosample_ontology.term_id=EFO:0003045&replicates.library.biosample.biosample_ontology.term_id=EFO:0003042"
        And I wait for the content to load


    Scenario: Matrix
        Then the title should contain the text "Deeply Profiled Cell Lines"
        And I should see at least 17 elements with the css selector "tbody > tr"
        And I should see at least 23 elements with the css selector "tr > th"
