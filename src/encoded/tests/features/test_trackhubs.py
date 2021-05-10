import pytest


pytestmark = [
    pytest.mark.bdd,
    pytest.mark.usefixtures('index_workbook'),
]


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


@pytest.mark.parametrize(
    ('at_id', 'expected'),
    [
        (
            '/experiments/ENCSR000AEN/',
            {
                'GRCh38': [
                    "Ensembl",
                    "UCSC",
                ],
                'hg19': [
                    "UCSC"
                ]
            }
        ),
        (
            '/experiments/ENCSR000AJK/',
            {
                'GRCh38': [
                    'Ensembl',
                    'UCSC',
                    'hic'
                ],
                'hg19': [
                    'UCSC',
                    'hic'
                ]
            }
        )
    ]
)
def test_visualize(submitter_testapp, index_workbook, at_id, expected):
    res = submitter_testapp.get(at_id)
    assert len(expected) == len(res.json['visualize'])
    assert all(
        set(expected[assembly]) == set(res.json['visualize'][assembly])
        for assembly in expected
    )


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
    "    interactUp True",
    "    spectrum on",
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


@pytest.mark.parametrize('expected', [
    "track ENCSR928SVL",
    "compositeTrack on",
    "type bed 3",
    "longLabel STARR-seq of Homo sapiens WTC-11 cell line genetically modified (knockout) using CRISPR - ENCSR928SVL",
    "shortLabel STARR-seq of WTC-11 ENCSR928SVL",
    "visibility dense",
    "subGroup1 view Views aPKS=Peaks bSIG=Signal_of_unique_reads cSPV=Signal_p-value dCNS=Control_normalized_signal",
    "subGroup2 BS Biosample WTC4511=WTC-11",
    "subGroup3 EXP Experiment ENCSR928SVL=ENCSR928SVL",
    "subGroup4 REP Replicates rep01=Replicate_1",
    "sortOrder BS=+ REP=+ view=+",
    "dimensions dimA=REP",
    "dimensionAchecked rep01",
    "    track ENCSR928SVL_aPKS_view",
    "    parent ENCSR928SVL on",
    "    view aPKS",
    "    type bigBed",
    "    visibility dense",
    "        track ENCFF105SVF",
    "        parent ENCSR928SVL_aPKS_view on",
    "        bigDataUrl /files/ENCFF105SVF/@@download/ENCFF105SVF.bigBed?proxy=true",
    "        longLabel STARR-seq of WTC-11 peaks rep1 ENCSR928SVL - ENCFF105SVF",
    "        shortLabel rep1 peaks",
    "        type bigBed",
    "        subGroups BS=WTC4511 EXP=ENCSR928SVL REP=rep01 view=aPKS",
])
def test_STARR_bigBed_trackDb(testapp, index_workbook, expected):
    res = testapp.get("/functional-characterization-experiments/ENCSR928SVL/@@hub/hg19/trackDb.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    "track ENCSR127PCE",
    "compositeTrack on",
    "type bed 3",
    "longLabel pooled clone sequencing of DNA cloning sample - ENCSR127PCE",
    "shortLabel pooled clone sequencing of DNA cloning sample ENCSR127PCE",
    "visibility full",
    "subGroup1 view Views aSIG=Signal_of_unique_reads",
    "subGroup2 EXP Experiment ENCSR127PCE=ENCSR127PCE",
    "subGroup3 REP Replicates rep01=Replicate_1",
    "sortOrder REP=+ view=+",
    "dimensions dimA=REP",
    "dimensionAchecked rep01",
    "    track ENCSR127PCE_aSIG_view",
    "    parent ENCSR127PCE on",
    "    view aSIG",
    "    type bigWig",
    "    visibility full",
    "        track ENCFF210SUR",
    "        parent ENCSR127PCE_aSIG_view on",
    "        bigDataUrl /files/ENCFF210SUR/@@download/ENCFF210SUR.bigWig?proxy=true",
    "        longLabel pooled clone sequencing of DNA cloning sample signal of unique reads rep1 ENCSR127PCE - ENCFF210SUR",
    "        shortLabel rep1 unq sig",
    "        type bigWig",
    "        subGroups EXP=ENCSR127PCE REP=rep01 view=aSIG",
])
def test_PCS_bigWig_trackDb(testapp, index_workbook, expected):
    res = testapp.get("/functional-characterization-experiments/ENCSR127PCE/@@hub/hg19/trackDb.txt")
    assert expected in res.text
