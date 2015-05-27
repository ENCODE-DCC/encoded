=========================
Change log for file.json
=========================


Schema version 5
----------------

* *run_type* was migrated from replicate.paired_ended. It will be required for fastq files.  If run_type is paired-ended then "paired_with" will be required as well.:

        "run_type": {
            "title": "Run type for sequencing files",
            "description": "Indicates if file is part of a single or paired run",
            "type": "string",
            "enum": [
                "single-ended",
                "paired-ended",
                "unknown"
            ]
        },

* *read_length* was migrated this field from replicate.read_length.  It will be required for fastq files.:

            "read_length": {
                "title": "Read length",
                "description": "For high-throughput sequencing, the number of contiguous nucleotides determined by sequencing.",
                "type": "integer"
            },

* *read_length_units* was added as a calculated field.  It will not need to be submitted.

* *platform* was migrated this field from replicate.read_length.  It will be required for fastq files.:

            "platform": {
                "title": "Platform",
                "description": "The measurement device used to collect data.",
                "comment": "See platform.json for available identifiers.",
                "type": "string",
                "linkTo": "platform"
            },

* *file_format* enum was restricted to general formats for example bed not bed_narrowpeak:
    
            "mapping" = {
                'bed_bedLogR': 'bed',
                'bed_bedMethyl': 'bed',
                'bed_broadPeak': 'bed',
                'bed_gappedPeak': 'bed',
                'bed_narrowPeak': 'bed',
                'bed_bedRnaElements': 'bed',
                'bedLogR': 'bigBed',
                'bedMethyl': 'bigBed',
                'broadPeak': 'bigBed',
                'narrowPeak': 'bigBed',
                'gappedPeak': 'bigBed',
                'bedRnaElements': 'bigBed'
            }

            "current_enum": [
                    "bam",
                    "bed",
                    "bigBed",
                    "bigWig",
                    "fasta",
                    "fastq",
                    "gff",
                    "gtf",
                    "hdf5",
                    "idat",
                    "rcc",
                    "CEL",
                    "tsv",
                    "csv",
                    "sam",
                    "tar",
                    "wig"
            ]


* *file_format_type* was added and will be required when *file_format* is ["bed", "bigBed", "gff"]:

            "enum": [
                "bed6",
                "bed9",
                "bedGraph",
                "bedLogR",
                "bedMethyl",
                "broadPeak",
                "gappedPeak",
                "gff2",
                "gff3",
                "narrowPeak"
            ]

            "comment": "Historical file formats, not valid for new submissions.",
            "enum": [
                "unknown",
                "bedRnaElements"
            ]

* *file_format_specifications* was added as a way to add description or autosql to the file object:

            "file_format_specifications": {
                "title": "File format specifications documents",
                "description": "Text or .as files the further explain the file format",
                "type": "array",
                "items": {
                        "comment": "See document.json for a list of available identifiers.",
                        "type": "string",
                        "linkTo": "document"
                        }
            },
             
* *output_category* added as a calculated field.  The files are now given one of these categories.:

           [
           "raw data",
           "alignment",
           "signal",
           "annotation",
           "quantification",
           "reference",
           "validation"
           ]


* *output_type* enum was changed dramatically to more specifically describe what the file contents are.  The maping here is simplistic.  (For further details in how we re-classified please look at src/encoded/upgrade/file.py.):

            output_mapping = {
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


* *md5sum_content* was added.  The DCC will calculate this field. The goal is to make this unique.:

            "content_md5sum": {
                    "title": "Content MD5sum",
                    "description": "The MD5sum of the uncompressed file.",
                    "comment": "This is only relavant for gzipped files.",
                    "type": "string",
                    "format": "hex"
            }


Schema version 4
----------------

* *lab* was added
* *award* was added
* *download_path* was removed as we now have *href*
* *flowcell_details* array was migrated from *replicate.flowcell_details*
