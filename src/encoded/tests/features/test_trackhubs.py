import pytest


@pytest.mark.parametrize('expected', [
    "# http://localhost/batch_hub/type%3Dexperiment/hub.txt",
    "hub ENCODE_DCC_search",
    "shortLabel Hub (search:)",
    "longLabel ENCODE Data Coordination Center Data Hub",
    "genomesFile genomes.txt",
    "email encode-help@lists.stanford.edu",
])
def test_hub(testapp, workbook, expected):
    res = testapp.get("/batch_hub/type%3Dexperiment/hub.txt")
    assert expected in res.text

@pytest.mark.parametrize('expected', [
    "genome mm9",
    "trackDb mm9/trackDb.txt",
    "genome hg38",
    "trackDb hg38/trackDb.txt",
    "genome hg19",
    "trackDb hg19/trackDb.txt",
])
def test_genomes(testapp, workbook, expected):
    res = testapp.get("/batch_hub/type%3Dexperiment/genomes.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    "track ENCSR575ZXX",
    "compositeTrack on",
    "type bed 3",
    "longLabel Unknown Assay of Unknown Biosample - ENCSR575ZXX",
    "shortLabel Unknown Assay of IMR-90 ENCSR575ZXX",
    "visibility full",
    "pennantIcon https://www.encodeproject.org/static/img/pennant-encode.png https://www.encodeproject.org/ \"This trackhub was automatically generated from the ENCODE files and metadata found at the ENCODE portal\"",
    "subGroup1 view Views PK=Peaks SIG=Signals",
    "subGroup2 BS Biosample IMR4590=IMR-90",
    "subGroup3 REP Replicates pool=Pooled",
    "sortOrder BS=+ REP=+ view=+",
    "dimensionAchecked pool",
    "    track ENCSR575ZXX_PK_view",
    "    parent ENCSR575ZXX on",
    "    view PK",
    "    type bigBed",
    "    visibility dense",
    "    spectrum on",
    "        track ENCFF762DWI",
    "        parent ENCSR575ZXX_PK_view on",
    "        bigDataUrl /files/ENCFF762DWI/@@download/ENCFF762DWI.bigBed?proxy=true",
    "        longLabel Unknown Assay of IMR-90 semi-automated genome annotation pool ENCSR575ZXX - ENCFF762DWI",
    "        shortLabel pool saga",
    "        type bigBed",
    "        subGroups BS=IMR4590 REP=pool view=PK",
    "        metadata biosample=\"IMR-90\" experiment=\"<a href='http://localhost/experiments/ENCSR575ZXX' TARGET='_blank' title='Experiment details from the ENCODE portal'>ENCSR575ZXX</a>\" file&#32;download=\"<a href='http://localhost/files/ENCFF762DWI/@@download/ENCFF762DWI.bigBed' title='Download this file from the ENCODE portal'>ENCFF762DWI</a>\"",
])
def test_dataset_trackDb(testapp, workbook, expected):
    res = testapp.get("/annotations/ENCSR575ZXX/@@hub/hg19/trackDb.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    "track ENCSR727WCB",
    "compositeTrack on",
    "type bed 3",
    "longLabel Unknown Assay of Unknown Biosample - ENCSR727WCB",
    "shortLabel Unknown Assay of Unknown Biosample ENCSR727WCB",
    "visibility full",
    "pennantIcon https://www.encodeproject.org/static/img/pennant-encode.png https://www.encodeproject.org/ \"This trackhub was automatically generated from the ENCODE files and metadata found at the ENCODE portal\"",
    "subGroup1 view Views PK=Peaks SIG=Signals",
    "subGroup2 REP Replicates rep01=Replicate_1",
    "sortOrder REP=+ view=+",
    "dimensionAchecked rep01",
    "    track ENCSR727WCB_PK_view",
    "    parent ENCSR727WCB on",
    "    view PK",
    "    type bigBed",
    "    visibility dense",
    "    spectrum on",
    "        track ENCFF003COS",
    "        parent ENCSR727WCB_PK_view on",
    "        bigDataUrl /files/ENCFF003COS/@@download/ENCFF003COS.bigBed?proxy=true",
    "        longLabel Unknown Assay of Unknown Biosample optimal idr thresholded peaks rep1 ENCSR727WCB - ENCFF003COS",
    "        shortLabel rep1 oIDR pk",
    "        type bigBed",
    "        subGroups REP=rep01 view=PK",
    "        metadata biological&#32;replicate=1 experiment=\"<a href='http://localhost/experiments/ENCSR727WCB' TARGET='_blank' title='Experiment details from the ENCODE portal'>ENCSR727WCB</a>\" file&#32;download=\"<a href='http://localhost/files/ENCFF003COS/@@download/ENCFF003COS.bigBed' title='Download this file from the ENCODE portal'>ENCFF003COS</a>\" technical&#32;replicate=1",
])
def test_fileset_files_trackDb(testapp, workbook, expected):
    res = testapp.get("/publication-data/ENCSR727WCB/@@hub/hg19/trackDb.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    "# Empty composite for ENCSR000ACY.  It cannot be visualized at this time.",
])
def test_experiment_trackDb(testapp, workbook, expected):
    res = testapp.get("/experiments/ENCSR000ACY/@@hub/trackDb.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    "genome hg38",
    "trackDb hg38/trackDb.txt",
])
def test_genome_txt(testapp, workbook, expected):
    res = testapp.get("/batch_hub/type=Experiment&assembly=GRCh38/genomes.txt")
    assert expected in res.text

@pytest.mark.parametrize('expected', [
    "GRCh38",
    "hg19"
])
def test_assembly(testapp, workbook, expected):
    res = testapp.get("/experiments/ENCSR000AEN/")
    assert expected in res.json['assembly']


@pytest.mark.parametrize('expected', [
    "/experiments/ENCSR000AEN/@@hub/hub.txt",
])
def test_hub_field(testapp, workbook, expected):
    res = testapp.get("/experiments/ENCSR000AEN/")
    assert expected in res.json['hub']


def test_visualize_ucsc(testapp, workbook):
    expected = {
        'GRCh38': 'http://genome.ucsc.edu/cgi-bin/hgTracks?hubClear=http://localhost/experiments/ENCSR000AEN/@@hub/hub.txt&db=hg38',
        'hg19': 'http://genome.ucsc.edu/cgi-bin/hgTracks?hubClear=http://localhost/experiments/ENCSR000AEN/@@hub/hub.txt&db=hg19'
    }
    res = testapp.get("/experiments/ENCSR000AEN/")
    assert expected == res.json['visualize_ucsc']
