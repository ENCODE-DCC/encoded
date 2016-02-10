import pytest


@pytest.mark.parametrize('expected', [
    "hub ENCODE_DCC_search",
    "shortLabel Hub (search)",
    "longLabel ENCODE Data Coordination Center Data Hub",
    "genomesFile genomes.txt",
    "email encode-help@lists.stanford.edu",
])
def test_hub(testapp, workbook, expected):
    res = testapp.get("/batch_hub/type%3Dexperiment/hub.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    "genome hg19",
    "trackDb hg19/trackDb.txt",
])
def test_genomes(testapp, workbook, expected):
    res = testapp.get("/batch_hub/type%3Dexperiment/genomes.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    "compositeTrack on",
    "visibility full",
    "dragAndDrop subTracks",
    "subGroup1 view Views PK=Peaks SIG=Signals",
    "type bed 3",
    "sortOrder view=+",
])
def test_trackDb(testapp, workbook, expected):
    res = testapp.get("/batch_hub/type%3Dexperiment/hg19/trackDb.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    "shortLabel Unknown Assay of IMR-90 - ENCSR575ZXX",
    "longLabel Unknown Assay of IMR-90 - ENCSR575ZXX",
    "bigDataUrl /files/ENCFF762DWI/@@download/ENCFF762DWI.bigBed?proxy=true",
    "track ENCSR575ZXX",
    "longLabel Unknown Assay of IMR-90 - ENCSR575ZXX - ENCFF762DWI narrowPeak semi-automated genome annotation rep unknown",
])
def test_dataset_trackDb(testapp, workbook, expected):
    res = testapp.get("/annotations/ENCSR575ZXX/@@hub/hg19/trackDb.txt")
    assert expected in res.text


@pytest.mark.parameterize('expected', [
    "bigDataUrl /files/ENCFF003COS/@@download/ENCFF003COS.bigBed?proxy=true"
])
def test_related_files_trackDb(testapp, workbook, expected):
    res = testapp.get("/publication-data/ENCSR727WCB/@@hub/hg19/trackDb.txt")
    assert expected in res.text
