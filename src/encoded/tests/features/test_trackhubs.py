import pytest

pytestmark = [pytest.mark.indexing]

@pytest.mark.parametrize('expected', [
    "# http://localhost/batch_hub/type=Experiment/hub.txt",
    "hub ENCODE_DCC_search",
    "shortLabel Hub (search:)",
    "longLabel ENCODE Data Coordination Center Data Hub",
    "genomesFile genomes.txt",
    "email encode-help@lists.stanford.edu"
])
def test_hub(testapp, index_workbook, expected):
    res = testapp.get("/batch_hub/type=Experiment/hub.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    "genome mm9",
    "trackDb mm9/trackDb.txt",
    "genome hg38",
    "trackDb hg38/trackDb.txt",
    "genome hg19",
    "trackDb hg19/trackDb.txt",
])
def test_genomes(testapp, index_workbook, expected):
    res = testapp.get("/batch_hub/type=Experiment/genomes.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    "track ENCSR575ZXX",
    "compositeTrack on",
    "type bed 3",
    "longLabel Encyclopedia annotation of chromatin state for IMR-90 - ENCSR575ZXX",
    "shortLabel chromatin state of IMR-90 ENCSR575ZXX",
    "visibility full",
    "pennantIcon https://www.encodeproject.org/static/img/pennant-encode.png https://www.encodeproject.org/ \"This trackhub was automatically generated from the ENCODE files and metadata found at the ENCODE portal\"",
    "subGroup1 view Views aENHAN=Candidate_enhancers bPROMO=Candidate_promoters cSTATE=Chromatin_state hSTATE=HMM_predicted_chromatin_state sPKS=Peaks",
    "subGroup2 BS Biosample IMR4590=IMR-90",
    "subGroup3 EXP Experiment ENCSR575ZXX=ENCSR575ZXX",
    "subGroup4 REP Replicates pool=Pooled",
    "sortOrder BS=+ REP=+ view=+",
    "    track ENCSR575ZXX_cSTATE_view",
    "    parent ENCSR575ZXX on",
    "    view cSTATE",
    "    type bigBed",
    "    visibility dense",
    "        track ENCFF762DWI",
    "        parent ENCSR575ZXX_cSTATE_view on",
    "        bigDataUrl /files/ENCFF762DWI/@@download/ENCFF762DWI.bigBed?proxy=true",
    "        longLabel Encyclopedia annotation of IMR-90 semi-automated genome annotation pool ENCSR575ZXX - ENCFF762DWI",
    "        shortLabel pool saga",
    "        type bigBed",
    "        subGroups BS=IMR4590 EXP=ENCSR575ZXX REP=pool view=cSTATE",
])
def test_dataset_trackDb(testapp, index_workbook, expected):
    res = testapp.get("/annotations/ENCSR575ZXX/@@hub/hg19/trackDb.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    "track chip",
    "compositeTrack on",
    "type bed 3",
    "longLabel Collection of ENCODE ChIP-seq experiments",
    "shortLabel ENCODE ChIP-seq",
    "visibility full",
    "html ChIP",
    "subGroup1 view Views aOIDR=Optimal_IDR_thresholded_peaks bIDRT=IDR_thresholded_peaks cCIDR=Conservative_IDR_thresholded_peaks dRPKS=Pseudoreplicated_IDR_thresholded_peaks ePKS=Peaks gSPV=Signal_p-value fFCOC=Fold_change_over_control hSIG=Signal",
    "subGroup2 BS Biosample GM12878=GM12878",
    "subGroup3 EXP Experiment ENCSR000DZQ=ENCSR000DZQ",
    "subGroup4 REP Replicates pool=Pooled",
    "subGroup5 TARG Targets EBF1=EBF1",
    "sortOrder BS=+ TARG=+ REP=+ view=+ EXP=+",
    "dimensions dimA=REP",
    "dimensionAchecked pool",
    "    track chip_bIDRT_view",
    "    parent chip on",
    "    view bIDRT",
    "    type bigNarrowPeak",
    "    visibility dense",
    "    spectrum on",
    "        track ENCFF003COS",
    "        parent chip_bIDRT_view on",
    "        bigDataUrl /files/ENCFF003COS/@@download/ENCFF003COS.bigBed?proxy=true",
    "        longLabel EBF1 TF ChIP-seq of GM12878 IDR thresholded peaks pool ENCSR000DZQ - ENCFF003COS",
    "        shortLabel pool IDRt pk",
    "        type bigNarrowPeak",
    "        color 153,38,0",
    "        altColor 115,31,0",
    "        subGroups BS=GM12878 EXP=ENCSR000DZQ REP=pool TARG=EBF1 view=bIDRT",
])
def test_genomes(testapp, index_workbook, expected):
    res = testapp.get("/batch_hub/type=Experiment%2C%2caccession%3DENCSR000DZQ%2C%2caccession%3DENCSRENCSR575ZXX/hg19/trackDb.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    ""
])
def test_fileset_files_trackDb(testapp, index_workbook, expected):
    res = testapp.get("/publication-data/ENCSR727WCB/@@hub/hg19/trackDb.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    "# Empty composite for ENCSR000ACY.  It cannot be visualized at this time.",
])
def test_experiment_trackDb(testapp, index_workbook, expected):
    res = testapp.get("/experiments/ENCSR000ACY/@@hub/trackDb.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    "genome hg38",
    "trackDb hg38/trackDb.txt",
])
def test_genome_txt(testapp, index_workbook, expected):
    res = testapp.get("/batch_hub/type=Experiment&assembly=GRCh38/genomes.txt")
    assert expected in res.text

@pytest.mark.parametrize('expected', [
    "GRCh38",
    "hg19"
])
def test_assembly(testapp, index_workbook, expected):
    res = testapp.get("/experiments/ENCSR000AEN/")
    assert expected in res.json['assembly']


@pytest.mark.parametrize('expected', [
    "/experiments/ENCSR000AEN/@@hub/hub.txt",
])
def test_hub_field(testapp, index_workbook, expected):
    res = testapp.get("/experiments/ENCSR000AEN/")
    assert expected in res.json['hub']


def test_visualize(submitter_testapp, index_workbook):
    expected = {
        'GRCh38': [
            "Ensembl",
            "UCSC",
        ],
        'hg19': [
            "UCSC"
        ]
    }
    res = submitter_testapp.get("/experiments/ENCSR000AEN/")
    assert set(expected['GRCh38']) == set(res.json['visualize']['GRCh38']) and set(expected['hg19']) == set(res.json['visualize']['hg19'])


@pytest.mark.parametrize('expected', [
    "track ENCSR270OQH",
    "compositeTrack on",
    "type bed 3",
    "longLabel Unknown Target ChIA-PET of Unknown Biosample - ENCSR270OQH",
    "shortLabel Unknown Target ChIA-PET of cell-free sample ENCSR270OQH",
    "visibility full",
    "subGroup1 view Views CHRINTR=Chromatin_interactions LRCI=Long_range_interactions PEAKS=Peaks SIGBL=Signal_of_unique_reads SIGBM=Signal_of_all_reads",
    "subGroup2 BS Biosample cell45free_sample=cell-free_sample",
    "subGroup3 EXP Experiment ENCSR270OQH=ENCSR270OQH",
    "subGroup4 REP Replicates rep01=Replicate_1",
    "sortOrder BS=+ REP=+ view=+",
    "dimensions dimA=REP",
    "dimensionAchecked rep01",
    "    track ENCSR270OQH_CHRINTR_view",
    "    parent ENCSR270OQH on",
    "    view CHRINTR",
    "    type bigInteract",
    "    visibility full",
    "        track ENCFF727BIF",
    "        parent ENCSR270OQH_CHRINTR_view on",
    "        bigDataUrl /files/ENCFF727BIF/@@download/ENCFF727BIF.bigInteract?proxy=true",
    "        longLabel ChIA-PET of cell-free sample long range chromatin interactions rep1 ENCSR270OQH - ENCFF727BIF",
    "        shortLabel rep1 lrci",
    "        type bigInteract",
    "        subGroups BS=cell45free_sample EXP=ENCSR270OQH REP=rep01 view=CHRINTR",
])
def test_bigInteract_trackDb(testapp, index_workbook, expected):
    res = testapp.get("/experiments/ENCSR270OQH/@@hub/hg19/trackDb.txt")
    assert expected in res.text
