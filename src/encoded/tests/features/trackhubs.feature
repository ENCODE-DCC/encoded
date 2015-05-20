@antibodies @usefixtures(workbook)
Feature: Trackhubs

    Scenario: hub.txt
        When I visit "/batch_hub/type%3Dexperiment/hub.txt"

        And I should see "hub ENCODE_DCC_search"
        And I should see "shortLabel Hub (search)"
        And I should see "longLabel ENCODE Data Coordination Center Data Hub"
        And I should see "genomesFile genomes.txt"
        And I should see "email encode-help@lists.stanford.edu"

    Scenario: genomes.txt
        When I visit "/batch_hub/type%3Dexperiment/genomes.txt"

        And I should see "genome hg19"
        And I should see "trackDb hg19/trackDb.txt"

    Scenario: trackDb.txt
        When I visit "/batch_hub/type%3Dexperiment/hg19/trackDb.txt"

        And I should see "compositeTrack on"
        And I should see "visibility full"
        And I should see "dragAndDrop subTracks"
        And I should see "subGroup1 view Views PK=Peaks SIG=Signals"
        And I should see "type bed 3"
        And I should see "sortOrder view=+"
