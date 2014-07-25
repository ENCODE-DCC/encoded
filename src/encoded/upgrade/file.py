from ..migrator import upgrade_step


@upgrade_step('file', '', '2')
def file_0_2(value, system):
    # http://redmine.encodedcc.org/issues/1295
    # http://redmine.encodedcc.org/issues/1307
    if 'status' in value:
        value['status'] = value['status'].lower()


@upgrade_step('file', '2', '3')
def file_2_3(value, system):
    # http://redmine.encodedcc.org/issues/1429
    if value.get('status') == 'current':
        if value['experiment'].get('status') == 'released':
            value['status'] = 'released'

    # http://redmine.encodedcc.org/issues/1618
    value['award'] = value['dataset']['award']
    value['lab'] = value['dataset']['lab']

    output_type_dict = {
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
                        "PlusRawSignal": "plus raw signal",
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
                        "Protocol": "RawData",
                        }

    if value['output_type'] in output_type_dict:
        temp = output_type_dict[value['output_type']]
        value['output_type'] = temp

    # Help the raw data problem
    if value['output_type'] == 'raw data' and value['format'] == "fastq":
        value['output_type'] = 'reads'