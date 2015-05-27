from contentbase.upgrader import upgrade_step
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
    dataset = root.get_by_uuid(value['dataset']).upgrade_properties()

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
                        '': 'raw data',
                        'Alignments': 'alignments',
                        'bigBed': 'sites',
                        'bigWig': 'sites',
                        'Clusters': 'clusters',
                        'Contigs': 'contigs',
                        'FastqRd1': 'reads',
                        'FastqRd2': 'reads',
                        'forebrain_enhancers': 'enhancers_forebrain',
                        'heart_enhancers': 'enhancers_heart',
                        'GreenIdat': 'idat green file',
                        'hotspot_broad_peaks': 'hotspots',
                        'hotspot_narrow_peaks': 'hotspots',
                        'hotspot_signal': 'hotspots',
                        'Hotspots': 'hotspots',
                        'Interactions': 'interactions',
                        'MinusRawSignal': 'raw minus signal',
                        'PlusRawSignal': 'raw plus signal',
                        'macs2_dnase_peaks': 'peaks',
                        'macs2_dnase_signal': 'signal',
                        'MinusSignal': 'minus signal',
                        'minusSignal': 'minus signal',
                        'MultiMinus': 'multi-read minus signal',
                        'MultiPlus': 'multi-read plus signal',
                        'MultiSignal': 'multi-read signal',
                        'MultiUnstranded': 'multi-read signal',
                        'RawData2': 'reads',
                        'RedIdat': 'idat red file',
                        'peak': 'peaks',
                        'PeakCalls': 'peaks',
                        'Peaks': 'peaks',
                        'PlusSignal': 'plus signal',
                        'plusSignal': 'plus signal',
                        'predicted_enhancers_heart': 'enhancers_heart',
                        'RawSignal': 'raw signal',
                        'RawData': 'raw data',
                        'rcc': 'raw data',
                        'Read': 'reads',
                        'read': 'reads',
                        'read1': 'reads',
                        'rejected_reads': 'rejected reads',
                        'RepPeaks': 'peaks',
                        'RepSignal': 'signal',
                        'Signal': 'signal',
                        'SimpleSignal': 'signal',
                        'Sites': 'sites',
                        'Spikeins': 'spike-ins',
                        'Spikes': 'spike-ins',
                        'Splices': 'splice junctions',
                        'uniqueReads': 'unique signal',
                        'UniqueSignal': 'unique signal',
                        'uniqueSignal': 'unique signal',
                        'UniqueMinus': 'unique minus signal',
                        'uniqueMinusSignal': 'unique minus signal',
                        'UniquePlus': 'unique plus signal',
                        'uniquePlusSignal': 'unique plus signal',
                        'UniqueUnstranded': 'unique signal',
                        'UnstrandedSignal': 'signal',
                        'dataset_used': 'enhancers',
                        'TRAINING_DATA_MOUSE_VISTA': 'enhancers',
                        'method_description': 'enhancers',
                        'unknown': 'enhancers',
                        'Protocol': 'raw data',
                        }

    current_output_type = value['output_type']
    if current_output_type in output_type_dict:
        value['output_type'] = output_type_dict[current_output_type]

    # Help the raw data problem
    if value['output_type'] == 'raw data' and value['file_format'] == 'fastq':
        value['output_type'] = 'reads'


@upgrade_step('file', '3', '4')
def file_3_4(value, system):
    #  http://redmine.encodedcc.org/issues/1714

    context = system['context']
    root = find_root(context)
    dataset = root.get_by_uuid(value['dataset']).upgrade_properties()

    value.pop('download_path')

    value['lab'] = dataset['lab']
    value['award'] = dataset['award']

    # EDW User
    if value.get('submitted_by') == '0e04cd39-006b-4b4a-afb3-b6d76c4182ff':
        value['lab'] = 'fb0af3d0-3a4c-4e96-b67a-f273fe527b04'
        value['award'] = '8bafd685-aa17-43fe-95aa-37bc1c90074a'


@upgrade_step('file', '4', '5')
def file_4_5(value, system):
    #  http://redmine.encodedcc.org/issues/2566
    #  http://redmine.encodedcc.org/issues/2565
    # we need to remeber  bedRnaElements,

    bed_files = {
        'bed_bedLogR': 'bedLogR',
        'bed_bedMethyl': 'bedMethyl',
        'bed_broadPeak': 'broadPeak',
        'bed_gappedPeak': 'gappedPeak',
        'bed_narrowPeak': 'narrowPeak',
        'bed_bedRnaElements': 'bedRnaElements'
    }

    bigBed_files = [
        'bedLogR',
        'bedMethyl',
        'broadPeak',
        'narrowPeak',
        'gappedPeak',
        'bedRnaElements'
    ]

    current = value['file_format']

    if current in ['bed', 'bigBed']:
        value['file_format_type'] = 'unknown'
        # we do not know what those formats were,  wranglers  will need to investigate
    elif current in bigBed_files:
        value['file_format_type'] = current
        value['file_format'] = 'bigBed'
    elif current in bed_files:
        value['file_format_type'] = bed_files[current]
        value['file_format'] = 'bed'
    elif current in ['gff']:
        value['file_format_type'] = 'unknown'
        # all gffs todate were in gff3, but we wouldn't know without wranglers checking

    # classify the peptide stuff
    if value['output_type'] in ['mPepMapGcFt', 'mPepMapGcUnFt']:
        value['file_format_type'] = 'modPepMap'
    elif value['output_type'] in ['pepMapGcFt', 'pepMapGcUnFt']:
        value['file_format_type'] = 'pepMap'

    #  http://redmine.encodedcc.org/issues/2565
    output_mapping = {
        # Category: Raw data
        'idat green file': 'idat green channel',
        'idat red file': 'idat red channel',
        'reads': 'reads',
        'rejected reads': 'rejected reads',
        'rcc': 'reporter code counts',
        'CEL': 'intensity values',
        'raw data': 'raw data',

        'alignments': 'alignments',
        'transcriptome alignments': 'transcriptome alignments',
        'spike-ins': 'spike-in alignments',

        'multi-read minus signal': 'minus strand signal of multi-mapped reads',
        'multi-read plus signal': 'plus strand signal of multi-mapped reads',
        'multi-read signal': 'signal of multi-mapped reads',
        'multi-read normalized signal': 'normalized signal of multi-mapped reads',
        'raw minus signal': 'raw minus strand signal',
        'raw plus signal': 'raw plus strand signal',
        'raw signal': 'raw signal',
        'raw normalized signal': 'raw normalized signal',
        'unique minus signal': 'minus strand signal of unique reads',
        'unique plus signal': 'plus strand signal of unique reads',
        'unique signal': 'signal of unique reads',
        'signal': 'signal',
        'minus signal': 'minus strand signal',
        'plus signal': 'plus strand signal',
        'Base_Overlap_Signal': 'base overlap signal',
        'PctSignal': 'percentage normalized signal',
        'SumSignal': 'summed densities signal',
        'WaveSignal': 'wavelet-smoothed signal',
        'signal p-value': 'signal p-value',
        'fold change over control': 'fold change over control',

        'enrichment': 'enrichment',
        'exon quantifications': 'exon quantifications',
        'ExonsDeNovo': 'exon quantifications',
        'ExonsEnsV65IAcuff': 'exon quantifications',
        'ExonsGencV10': 'exon quantifications',
        'ExonsGencV3c': 'exon quantifications',
        'ExonsGencV7': 'exon quantifications',
        'GeneDeNovo': 'gene quantifications',
        'GeneEnsV65IAcuff': 'gene quantifications',
        'GeneGencV10': 'gene quantifications',
        'GeneGencV3c': 'gene quantifications',
        'GeneGencV7': 'gene quantifications',
        'genome quantifications': 'gene quantifications',
        'library_fraction': 'library fraction',
        'transcript quantifications': 'transcript quantifications',
        'TranscriptDeNovo': 'transcript quantifications',
        'TranscriptEnsV65IAcuff': 'transcript quantifications',
        'TranscriptGencV10': 'transcript quantifications',
        'TranscriptGencV3c': 'transcript quantifications',
        'TranscriptGencV7': 'transcript quantifications',
        'mPepMapGcFt': 'filtered modified peptide quantification',
        'mPepMapGcUnFt': 'unfiltered modified peptide quantification',
        'pepMapGcFt': 'filtered peptide quantification',
        'pepMapGcUnFt': 'unfiltered peptide quantification',

        'clusters': 'clusters',
        'CNV': 'copy number variation',
        'contigs': 'contigs',
        'enhancer validation': 'enhancer validation',
        'FiltTransfrags': 'filtered transcribed fragments',
        'hotspots': 'hotspots',
        'Junctions': 'splice junctions',
        'interactions': 'long range chromatin interactions',
        'Matrix': 'long range chromatin interactions',
        'PrimerPeaks': 'long range chromatin interactions',
        'sites': 'methylation state at CpG',
        'methyl CG': 'methylation state at CpG',
        'methyl CHG': 'methylation state at CHG',
        'methyl CHH': 'methylation state at CHH',
        'peaks': 'peaks',
        'replicated peaks': 'replicated peaks',
        'RbpAssocRna': 'RNA-binding protein associated mRNAs',
        'splice junctions': 'splice junctions',
        'Transfrags': 'transcribed fragments',
        'TssGencV3c': 'transcription start sites',
        'TssGencV7': 'transcription start sites',
        'Valleys': 'valleys',
        'Alignability': 'sequence alignability',
        'Excludable': 'blacklisted regions',
        'Uniqueness': 'sequence uniqueness',

        'genome index': 'genome index',
        'genome reference': 'genome reference',
        'Primer': 'primer sequence',
        'spike-in sequence': 'spike-in sequence',
        'reference': 'reference',

        'enhancers': 'predicted enhancers',
        'enhancers_forebrain': 'predicted forebrain enhancers',
        'enhancers_heart': 'predicted heart enhancers',
        'enhancers_wholebrain': 'predicted whole brain enhancers',
        'TssHmm': 'predicted transcription start sites',
        'UniformlyProcessedPeakCalls': 'optimal idr thresholded peaks',
        'Validation': 'validation',
        'HMM': 'HMM predicted chromatin state'
    }

    old_output_type = value['output_type']

    # The peptide mapping files from UCSC all assumed V10 hg19
    if old_output_type in ['mPepMapGcFt', 'mPepMapGcUnFt', 'pepMapGcFt', 'pepMapGcUnFt']:
        value['genome_annotation'] = 'V10'
        value['assembly'] = 'hg19'

    elif old_output_type in ['ExonsEnsV65IAcuff', 'GeneEnsV65IAcuff', 'TranscriptEnsV65IAcuff']:
        value['genome_annotation'] = 'ENSEMBL V65'

    elif old_output_type in ['ExonsGencV3c', 'GeneGencV3c', 'TranscriptGencV3c', 'TssGencV3c']:
        value['genome_annotation'] = 'V3c'

    elif old_output_type in ['ExonsGencV7', 'GeneGenc7', 'TranscriptGencV7', 'TssGencV7']:
        value['genome_annotation'] = 'V7'

    elif old_output_type in ['ExonsGencV10', 'GeneGenc10', 'TranscriptGencV10', 'TssGencV10']:
        value['genome_annotation'] = 'V10'

    elif old_output_type in ['spike-ins'] and value['file_format'] == 'fasta':
        old_output_type = 'spike-in sequence'

    elif old_output_type in ['raw data'] and value['file_format'] in ['fastq', 'csfasta', 'csqual', 'fasta']:
        old_output_type = 'reads'

    elif old_output_type in ['raw data'] and value['file_format'] in ['CEL', 'tar']:
        old_output_type = 'CEL'

    elif old_output_type in ['raw data'] and value['file_format'] in ['rcc']:
        old_output_type = 'rcc'

    elif old_output_type in ['raw data'] and value['lab'] == '/labs/timothy-hubbard/':
        old_output_type = 'reference'

    elif old_output_type in ['raw data']:
        if 'These are protocol documents' in value.get('notes', ''):
            old_output_type = 'reference'

    elif old_output_type == 'sites' and value['file_format'] == 'tsv':
        old_output_type = 'interactions'

    elif old_output_type in ['Validation'] and value['file_format'] == '2bit':
        old_output_type = 'genome reference'

    value['output_type'] = output_mapping[old_output_type]

    #  label the lost bedRnaElements files #2940
    bedRnaElements_files = [
        'transcript quantifications',
        'gene quantifications',
        'exon quantifications'
        ]
    if (
        value['output_type'] in bedRnaElements_files
        and value['status'] in ['deleted', 'replaced']
        and value['file_format'] == 'bigBed'
        and value['file_format_type'] == 'unknown'
    ):
        value['file_format_type'] = 'bedRnaElements'

    #  Get the replicate information
    if value.get('file_format') in ['fastq', 'fasta', 'csfasta']:
        context = system['context']
        root = find_root(context)
        if 'replicate' in value:
            replicate = root.get_by_uuid(value['replicate']).upgrade_properties()

            if 'read_length' not in value:
                value['read_length'] = replicate.get('read_length')
                if value['read_length'] is None:
                    del value['read_length']

            run_type_dict = {
                True: 'paired-ended',
                False: 'single-ended',
                None: 'unknown'
            }
            if 'run_type' not in value:
                value['run_type'] = run_type_dict[replicate.get('paired_ended')]

        if value.get('paired_end') in ['2']:
            value['run_type'] = 'paired-ended'

    # Backfill content_md5sum #2683
    if 'content_md5sum' not in value:
        md5sum_content_md5sum = system['registry'].get('backfill_2683', {})
        if value['md5sum'] in md5sum_content_md5sum:
            value['content_md5sum'] = md5sum_content_md5sum[value['md5sum']]
