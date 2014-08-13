from ..migrator import upgrade_step
from pyramid.traversal import find_root


@upgrade_step('file', '', '2')
def file_0_2(value, system):
    # http://redmine.encodedcc.org/issues/1295
    # http://redmine.encodedcc.org/issues/1307
    if 'status' in value:
        value['status'] = value['status'].lower()


@upgrade_step('file', '2', '3')
def file_2_3(value, system):
    #  http://redmine.encodedcc.org/issues/1572
    file_format = value.get('file_format')
    file_name = value['download_path'].rsplit('/', 1)[-1]
    file_ext = file_name[file_name.find('.'):]

    # REJECTIONS
    if file_ext in ['.gtf.bigBed', '.pdf', '.pdf.gz', '.gff.bigBed', '.spikeins']:
        value['status'] = 'deleted'

    # Find the miscatorgorized bedMethyls
    if file_ext == '.bed.bigBed' and 'MethylRrbs' in value.get('submitted_file_name'):
        value['file_format'] = 'bedMethyl'
    if file_ext == '.bed.gz' and 'MethylRrbs' in value.get('submitted_file_name'):
        value['file_format'] = 'bed_bedMethyl'

    unknownDict = {'.CEL.gz': 'CEL',
                    '.bb': 'bedMethyl',
                    '.bed': 'bed',
                    '.bed.gz': 'bed',
                    '.bed.bigBed': 'bigBed',
                    '.bigBed': 'bigBed',
                    '.bed9': 'bedMethyl',
                    '.bed9.gz': 'bed_bedMethyl',
                    '.bedCluster.bigBed': 'bigBed',
                    '.bedLogR.bigBed': 'bedLogR',
                    '.bedRnaElements.bigBed': 'bedRnaElements',
                    '.bedRrbs.bigBed': 'bedMethyl',
                    '.broadPeak.gz': 'bed_broadPeak',
                    '.bigBed': 'bigBed',
                    '.csfasta.gz': 'csfasta',
                    '.csqual.gz': 'csqual',
                    '.fasta.gz': 'fasta',
                    '.gff.bigBed': 'bigBed',
                    '.gff.gz': 'gtf',
                    '.gp.bigBed': 'bigBed',
                    '.matrix.gz': 'tsv',
                    '.matrix.tgz': 'tar',
                    '.narrowPeak': 'bed_narrowPeak',
                    '.narrowPeak.gz': 'bed_narrowPeak',
                    '.pdf': 'tsv',  # These are going to be obsolete
                    '.pdf.gz': 'tsv',  # These are going to be obsolete
                    '.peaks.gz': 'tsv',
                    '.peptideMapping.bigBed': 'bigBed',
                    '.shortFrags.bigBed': 'bigBed',
                    '.sorted.bigBed': 'bigBed',
                    '.tab.gz': 'tsv',
                    '.tgz': 'tar',
                    '.txt': 'tsv',
                    '.xlsx': 'tsv',  # These need to be converted to tsv
                   }
    if file_format in ['unknown', 'customTrack']:
        value['file_format'] = unknownDict[file_ext]

    # http://redmine.encodedcc.org/issues/1429

    context = system['context']
    root = find_root(context)
    dataset = root.get_by_uuid(value['dataset']).upgrade_properties(finalize=False)

    dataset_status = dataset.get('status')
    status = value.get('status')

    if status == 'current':
        if dataset_status == 'released':
            value['status'] = 'released'
        else:
            value['status'] = 'in progress'

    if status == 'obsolete':
        if dataset_status in ['released', 'revoked']:
            value['status'] = 'revoked'
        else:
            value['status'] = 'deleted'

    # http://redmine.encodedcc.org/issues/568
    output_type_dict = {
                        "": "raw data",
                        "Alignments": "alignments",
                        "bigBed": "sites",
                        "bigWig": "sites",
                        "Clusters": "clusters",
                        "Contigs": "contigs",
                        "FastqRd1": "reads",
                        "FastqRd2": "reads",
                        "forebrain_enhancers": "enhancers_forebrain",
                        "heart_enhancers": "enhancers_heart",
                        "GreenIdat": "idat green file",
                        "hotspot_broad_peaks": "hotspots",
                        "hotspot_narrow_peaks": "hotspots",
                        "hotspot_signal": "hotspots",
                        "Hotspots": "hotspots",
                        "Interactions": "interactions",
                        "MinusRawSignal": "raw minus signal",
                        "PlusRawSignal": "raw plus signal",
                        "macs2_dnase_peaks": "peaks",
                        "macs2_dnase_signal": "signal",
                        "MinusSignal": "minus signal",
                        "minusSignal": "minus signal",
                        "MultiMinus": "multi-read minus signal",
                        "MultiPlus": "multi-read plus signal",
                        "MultiSignal": "multi-read signal",
                        "MultiUnstranded": "multi-read signal",
                        "RawData2": "reads",
                        "RedIdat": "idat red file",
                        "peak": "peaks",
                        "PeakCalls": "peaks",
                        "Peaks": "peaks",
                        "PlusSignal": "plus signal",
                        "plusSignal": "plus signal",
                        "predicted_enhancers_heart": "enhancers_heart",
                        "RawSignal": "raw signal",
                        "RawData": "raw data",
                        "rcc": "raw data",
                        "Read": "reads",
                        "read": "reads",
                        "read1": "reads",
                        "rejected_reads": "rejected reads",
                        "RepPeaks": "peaks",
                        "RepSignal": "signal",
                        "Signal": "signal",
                        "SimpleSignal": "signal",
                        "Sites": "sites",
                        "Spikeins": "spike-ins",
                        "Spikes": "spike-ins",
                        "Splices": "splice junctions",
                        "uniqueReads": "unique signal",
                        "UniqueSignal": "unique signal",
                        "uniqueSignal": "unique signal",
                        "UniqueMinus": "unique minus signal",
                        "uniqueMinusSignal": "unique minus signal",
                        "UniquePlus": "unique plus signal",
                        "uniquePlusSignal": "unique plus signal",
                        "UniqueUnstranded": "unique signal",
                        "UnstrandedSignal": "signal",
                        "dataset_used": "enhancers",
                        "TRAINING_DATA_MOUSE_VISTA": "enhancers",
                        "method_description": "enhancers",
                        "unknown": "enhancers",
                        "Protocol": "raw data",
                        }

    current_output_type = value['output_type']
    if current_output_type in output_type_dict:
        value['output_type'] = output_type_dict[current_output_type]

    # Help the raw data problem
    if value['output_type'] == 'raw data' and value['file_format'] == "fastq":
        value['output_type'] = 'reads' 


@upgrade_step('file', '3', '4')
def file_3_4(value, system):
    #  http://redmine.encodedcc.org/issues/1714
        
    context = system['context']
    root = find_root(context)
    dataset = root.get_by_uuid(value['dataset']).upgrade_properties(finalize=False)    

    value['lab'] = dataset['lab']
    value['award'] = dataset['award']

    # EDW User
    if value['submitted_by'] == '/users/0e04cd39-006b-4b4a-afb3-b6d76c4182ff/':
        value['lab'] = 'w-james-kent'
        value['award'] = 'U41HG006992'
      

    if value['paired_end'] in ['1','2']:
        possible_pairs = []
        for fileob in dataset['original_files']:
            if paired_end in fileob and fileob['paired_end'] != value['paired_end']:
                possible_pairs.append(fileob['accession'])
        if len(possible_pairs) == 1:
            value['paired_with'] = possible_pairs[0]
