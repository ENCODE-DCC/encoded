import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { BrowserFeat } from './browserfeat';
import { filterForVisualizableFiles } from './objectutils';
import Tooltip from '../libs/ui/tooltip';
import GeneSearch from './gene_search';

/**
 * Maps long annotation_type values to shorter versions for Valis track labels. Any not included
 * remain unchanged.
 */
export const annotationTypeMap = {
    'candidate Cis-Regulatory Elements': 'cCRE',
    'representative DNase hypersensitivity sites (rDHSs)': 'rDHS',
};

const GV_COORDINATES_KEY = 'ENCODE-GV-coordinates';

// used to determine if GV_COORDINATES_KEY should be used
const GV_COORDINATES_ASSEMBLY = 'ENCODE-GV-assembly';
const GV_COORDINATES_ANNOTATION = 'ENCODE-GV-annotation';

const colorChromatinState = {
    'Active TSS': '#ff0000',
    'Flanking TSS': '#ff4400',
    'Flanking TSS upstream': '#ff4500',
    'Flanking TSS downstream': '#ff4500',
    'Strong transcription': '#008000',
    'Weak transcription': '#006400',
    'Genic enhancer 1': '#c4e105',
    'Genic enhancer 2': '#c4e105',
    'Active enhancer 1': '#ffc44d',
    'Active enhancer 2': '#ffc44d',
    'Weak enhancer': '#ffff00',
    'ZNF genes & repeats': '#66cdaa',
    Heterochromatin: '#8a91d0',
    'Bivalent/Poised TSS': '#cd5c5c',
    'Bivalent enhancer': '#bdb86b',
    'Repressed PolyComb': '#808080, #8937df',
    'Weak Repressed PolyComb': '#c0c0c0, #9750e3',
    'Quiescent/Low': '#ffffff',
};

const colorCCREs = {
    'Promoter-like': '#ff0000',
    'Proximal enhancer-like': '#ffa700',
    'Distal enhancer-like': '#ffcd00',
    'DNase-H3K4me3': '#ffaaaa',
    'CTCF-only': '#00b0f0',
    'DNase-only': '#06da93',
    'Low-DNase': '#ffffff',
};

const colorGenome = {
    'Nucleobase A': '#0c7489',
    'Nucleobase T': '#f9ce70',
    'Nucleobase G': '#0fa3b1',
    'Nucleobase C': '#c14953',
    'GC-low': '#0c7489',
    'GC-rich': '#f9ce70',
};

const colorGenes = {
    Transcript: '#cfd7c7',
    'Protein coding': '#575f5a',
    'Non-protein coding': '#f9ce70',
    UTR: '#c14953',
};

/**
 * Returns Valis coordinates off the bar user inputs data in
 *
 * @param {string} scrollLocation, in format: "chr{contig} {x0}bp to {x1}bp, where contig, x0 and x2 and numbers. Note, the unit can also be Mbp"
 * @returns {x0, x1, contig}
 */
const readGenomeBrowserLabelCoordinates = () => {
    const scrollLocation = document.querySelector('.valis-browser .hpgv_panel-header span');

    if (!scrollLocation || !scrollLocation.innerText) {
        return {};
    }

    const splitScrollLocation = scrollLocation.innerText.split(' ');
    const contig = splitScrollLocation[0];
    const x0 = (splitScrollLocation[1].indexOf('Mbp') > -1) ? +splitScrollLocation[1].replace('Mbp', '') * 1e6 : +splitScrollLocation[1].replace('bp', '');
    const x1 = (splitScrollLocation[3].indexOf('Mbp') > -1) ? +splitScrollLocation[3].replace('Mbp', '') * 1e6 : +splitScrollLocation[3].replace('bp', '');

    return { x0, x1, contig };
};

/**
 * Get default coordinates to the genome browser
 *
 * @param {string} assemblyAnnotation Assembly information
 * @param {boolean} [ignoreCache=false] True to not look into cache, false to use cache
 * @returns Default coordinates
 */
const getDefaultCoordinates = (assembly, annotation, ignoreCache = false) => {
    // Files to be displayed on all genome browser results
    let pinnedFiles = [];
    let contig = null;
    let x0 = null;
    let x1 = null;
    const gVState = ignoreCache ? null : window.sessionStorage.getItem(GV_COORDINATES_KEY);
    const gVAssembly = window.sessionStorage.getItem(GV_COORDINATES_ASSEMBLY);
    const gVAnnotation = window.sessionStorage.getItem(GV_COORDINATES_ANNOTATION);

    if (gVState && gVAssembly === assembly && gVAnnotation === annotation) {
        const savedState = gVState ? JSON.parse(gVState) : {};
        ({ contig } = savedState);
        ({ x0, x1, pinnedFiles } = savedState);
    } else if (assembly === 'GRCh38') {
        pinnedFiles = [
            {
                file_format: 'vdna-dir',
                href: 'https://encoded-build.s3.amazonaws.com/browser/GRCh38/GRCh38.vdna-dir',
            },
            {
                file_format: 'vgenes-dir',
                href: 'https://encoded-build.s3.amazonaws.com/browser/GRCh38/GRCh38.vgenes-dir',
                title: 'GENCODE V29',
            },
            {
                title: 'dbSNP (153)',
                file_format: 'variant',
                path: 'https://encoded-build.s3.amazonaws.com/browser/GRCh38/GRCh38-dbSNP153.vvariants-dir',
            },
            {
                file_format: 'bigBed',
                href: '/files/ENCFF088UEJ/@@download/ENCFF088UEJ.bigBed',
                dataset: '/annotations/ENCSR169HLH/',
                title: 'representative DNase hypersensitivity sites',
            },
            {
                file_format: 'bigBed',
                href: '/files/ENCFF389ZVZ/@@download/ENCFF389ZVZ.bigBed',
                dataset: '/annotations/ENCSR439EAZ/',
                title: 'cCRE, all',
            },
        ];
        if (annotation === 'V33') {
            pinnedFiles = [
                {
                    file_format: 'vdna-dir',
                    href: 'https://encoded-build.s3.amazonaws.com/browser/GRCh38/GRCh38.vdna-dir',
                },
                {
                    file_format: 'vgenes-dir',
                    href: 'https://encoded-build.s3.amazonaws.com/browser/GRCh38/gencode.v33.GRCh38.p13.annotation.vgenes-dir',
                    title: 'GENCODE V33',
                },
                {
                    file_format: 'bigBed',
                    href: '/files/ENCFF088UEJ/@@download/ENCFF088UEJ.bigBed',
                    dataset: '/annotations/ENCSR169HLH/',
                    title: 'representative DNase hypersensitivity sites',
                },
                {
                    file_format: 'bigBed',
                    href: '/files/ENCFF389ZVZ/@@download/ENCFF389ZVZ.bigBed',
                    dataset: '/annotations/ENCSR439EAZ/',
                    title: 'cCRE, all',
                },
            ];
        }
        contig = 'chr1';
        x0 = 11102837;
        x1 = 11267747;
    } else if (assembly === 'hg19' || assembly === 'GRCh37') {
        pinnedFiles = [
            {
                file_format: 'vdna-dir',
                href: 'https://encoded-build.s3.amazonaws.com/browser/hg19/hg19.vdna-dir',
            },
            {
                file_format: 'vgenes-dir',
                href: 'https://encoded-build.s3.amazonaws.com/browser/hg19/hg19.vgenes-dir',
                title: 'GENCODE V29',
            },
        ];
        contig = 'chr21';
        x0 = 33031597;
        x1 = 33041570;
    } else if (assembly === 'GRCm39') {
        pinnedFiles = [
            {
                file_format: 'vdna-dir',
                href: 'https://encoded-build.s3.amazonaws.com/browser/mm39/mm39.vdna-dir',
            },
            {
                file_format: 'vgenes-dir',
                href: 'https://encoded-build.s3.amazonaws.com/browser/mm39/gencode.vM26.GRCm39.annotation.vgenes-dir',
                title: 'GENCODE M26',
            },
        ];
        contig = 'chr7';
        x0 = 72938479;
        x1 = 73220239;
    } else if (assembly === 'mm10' || assembly === 'mm10-minimal' || assembly === 'GRCm38') {
        pinnedFiles = [
            {
                file_format: 'vdna-dir',
                href: 'https://encoded-build.s3.amazonaws.com/browser/mm10/mm10.vdna-dir',
            },
            {
                file_format: 'vgenes-dir',
                href: 'https://encoded-build.s3.amazonaws.com/browser/mm10/mm10.vgenes-dir',
                title: 'GENCODE M21',
            },
            {
                file_format: 'bigBed',
                href: '/files/ENCFF278QAH/@@download/ENCFF278QAH.bigBed',
                dataset: '/annotations/ENCSR672RVL/',
                title: 'representative DNase hypersensitivity sites',
            },
            {
                file_format: 'bigBed',
                href: '/files/ENCFF228JRO/@@download/ENCFF228JRO.bigBed',
                dataset: '/annotations/ENCSR394RWS/',
                title: 'cCRE, all',
            },
        ];
        contig = 'chr12';
        x0 = 56694976;
        x1 = 56714605;
    } else if (assembly === 'mm9' || assembly === 'GRCm37') {
        pinnedFiles = [];
        contig = 'chr12';
        x0 = 57795963;
        x1 = 57815592;
    } else if (assembly === 'dm6') {
        pinnedFiles = [
            {
                file_format: 'vdna-dir',
                href: 'https://encoded-build.s3.amazonaws.com/browser/dm6/dm6.vdna-dir',
            },
            {
                file_format: 'vgenes-dir',
                href: 'https://encoded-build.s3.amazonaws.com/browser/dm6/Drosophila_melanogaster.BDGP6.22.96.vgenes-dir',
                title: 'FlyBase Annotation 6.04',
            },
        ];
        contig = 'chr2L';
        x0 = 2420509;
        x1 = 2467686;
    } else if (assembly === 'dm3') {
        pinnedFiles = [
            {
                file_format: 'vdna-dir',
                href: 'https://encoded-build.s3.amazonaws.com/browser/dm3/dm3.vdna-dir',
            },
            {
                file_format: 'vgenes-dir',
                href: 'https://encoded-build.s3.amazonaws.com/browser/dm3/dmel-all-r5.12.sorted.trimmed.chrM_fixed.vgenes-dir',
                title: 'FlyBase Annotation 5.12',
            },
        ];
        contig = 'chr2L';
        x0 = 2428372;
        x1 = 2459823;
    } else if (assembly === 'ce11') {
        pinnedFiles = [
            {
                file_format: 'vdna-dir',
                href: 'https://encoded-build.s3.amazonaws.com/browser/ce11/ce11.vdna-dir',
            },
            {
                file_format: 'vgenes-dir',
                href: 'https://encoded-build.s3.amazonaws.com/browser/ce11/Caenorhabditis_elegans.WBcel235.96.vgenes-dir',
                title: 'WormBase Annotation WS235',
            },
        ];
        contig = 'chrII';
        x0 = 232292;
        x1 = 238909;
    } else if (assembly === 'ce10') {
        pinnedFiles = [
            {
                file_format: 'vdna-dir',
                href: 'https://encoded-build.s3.amazonaws.com/browser/ce10/ce10.vdna-dir',
            },
            {
                file_format: 'vgenes-dir',
                href: 'https://encoded-build.s3.amazonaws.com/browser/ce10/c_elegans.WS220.annotations.sorted_chr_fixed.vgenes-dir',
                title: 'WormBase Annotation WS220',
            },
        ];
        contig = 'chrII';
        x0 = 232475;
        x1 = 237997;
    }
    window.sessionStorage.setItem(GV_COORDINATES_ASSEMBLY, assembly);
    window.sessionStorage.setItem(GV_COORDINATES_ANNOTATION, annotation);

    return { x0, x1, contig, pinnedFiles };
};

// Files to be displayed for local version of browser
const dummyFiles = [
    {
        file_format: 'bigWig',
        output_type: 'minus strand signal of all reads',
        accession: 'ENCFF425LKJ',
        '@id': '/files/ENCFF425LKJ',
        href: '/files/ENCFF425LKJ/@@download/ENCFF425LKJ.bigWig',
        assembly: 'GRCh38',
        file_type: 'bigWig',
        assay_term_name: 'shRNA knockdown followed by RNA-seq',
        dataset: '/experiments/ENCSR585KOJ/',
        biosample_ontology: {
            term_name: 'HepG2',
        },
        lab: {
            title: 'ENCODE Processing Pipeline',
        },
        status: 'released',
        title: 'ENCFF425LKJ',
        biological_replicates: [1],
    },
    {
        file_format: 'bigWig',
        output_type: 'plus strand signal of all reads',
        accession: 'ENCFF638QHN',
        '@id': '/files/ENCFF638QHN',
        href: '/files/ENCFF638QHN/@@download/ENCFF638QHN.bigWig',
        assembly: 'GRCh38',
        file_type: 'bigWig',
        assay_term_name: 'shRNA knockdown followed by RNA-seq',
        dataset: '/experiments/ENCSR585KOJ/',
        biosample_ontology: {
            term_name: 'HepG2',
        },
        lab: {
            title: 'ENCODE Processing Pipeline',
        },
        status: 'released',
        title: 'ENCFF638QHN',
        biological_replicates: [2],
    },
    {
        file_format: 'bigWig',
        output_type: 'plus strand signal of unique reads',
        accession: 'ENCFF541XFO',
        '@id': '/files/ENCFF541XFO',
        href: '/files/ENCFF541XFO/@@download/ENCFF541XFO.bigWig',
        assembly: 'GRCh38',
        file_type: 'bigWig',
        dataset: '/experiments/ENCSR585KOJ/',
        assay_term_name: 'shRNA knockdown followed by RNA-seq',
        biosample_ontology: {
            term_name: 'HepG2',
        },
        lab: {
            title: 'ENCODE Processing Pipeline',
        },
        status: 'released',
        title: 'ENCFF541XFO',
        biological_replicates: [1],
    },
    {
        file_format: 'bigBed bedRNAElements',
        output_type: 'transcription start sites',
        accession: 'ENCFF517WSY',
        '@id': '/files/ENCFF517WSY',
        href: '/files/ENCFF517WSY/@@download/ENCFF517WSY.bigBed',
        assembly: 'GRCh38',
        file_type: 'bigBed tss_peak',
        dataset: '/experiments/ENCSR000CIS/',
        assay_term_name: 'shRNA knockdown followed by RNA-seq',
        biosample_ontology: {
            term_name: 'HepG2',
        },
        lab: {
            title: 'ENCODE Processing Pipeline',
        },
        status: 'released',
        title: 'ENCFF517WSY',
        biological_replicates: [1],
    },
    {
        file_format: 'bigBed',
        output_type: 'peaks',
        accession: 'ENCFF026DAN',
        '@id': '/files/ENCFF026DAN',
        href: '/files/ENCFF026DAN/@@download/ENCFF026DAN.bigBed',
        assembly: 'hg19',
        file_type: 'bigBed narrowPeak',
        dataset: '/experiments/ENCSR683CSF/',
        assay_term_name: 'ChIP-seq',
        biosample_ontology: {
            term_name: 'HepG2',
        },
        lab: {
            title: 'ENCODE Processing Pipeline',
        },
        status: 'released',
        title: 'ENCFF026DAN',
        biological_replicates: [2],
    },
    {
        file_format: 'bigBed',
        output_type: 'peaks',
        accession: 'ENCFF847CBY',
        '@id': '/files/ENCFF847CBY',
        href: '/files/ENCFF847CBY/@@download/ENCFF847CBY.bigBed',
        assembly: 'hg19',
        file_type: 'bigBed narrowPeak',
        dataset: '/experiments/ENCSR683CSF/',
        assay_term_name: 'ChIP-seq',
        biosample_ontology: {
            term_name: 'HepG2',
        },
        lab: {
            title: 'ENCODE Processing Pipeline',
        },
        status: 'released',
        title: 'ENCFF847CBY',
        biological_replicates: [1, 2],
    },
];

// Fetch gene coordinate file
export function getCoordinateData(geneLink, fetch) {
    return fetch(geneLink, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
        },
    }).then((response) => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('not ok');
    }).catch((e) => {
        console.log('OBJECT LOAD ERROR: %s', e);
    });
}

const getAssemblyWithoutGenomeAnnotationOrMinimal = (assembly) => assembly.split(' ')[0].replace('-minimal', '');

function mapGenome(inputAssembly) {
    let genome = inputAssembly.split(' ')[0];
    if (genome === 'hg19') {
        genome = 'GRCh37';
    } else if (genome === 'mm9') {
        genome = 'GRCm37';
    } else if (genome === 'mm10') {
        genome = 'GRCm38';
    }
    return genome;
}

// Map the name of a sort parameter to a file object property and convert to form that can be compared
// Ordering by replicate is like this: 'Rep 1,2' -> 'Rep 1,3,...' -> 'Rep 2,3,...' -> 'Rep 1' -> 'Rep 2' -> 'Rep N'
// Multiplication by 1000 orders the replicates with a single replicate at the end
const sortLookUp = (obj, param) => {
    switch (param) {
    case 'Replicates':
        return obj.biological_replicates.length > 1 ? +obj.biological_replicates.join('') : +obj.biological_replicates * 1000;
    case 'Output type':
        return obj.output_type.toLowerCase();
    case 'File type':
        return obj.file_type.toLowerCase();
    case 'Assay term name':
        return obj.assay_term_name.toLowerCase();
    case 'Biosample term name':
        return obj.biosample_ontology.term_name.toLowerCase();
    default:
        return null;
    }
};

const LegendLabel = () => (
    <div className="legend-label">
        <div className="legend-color-container">
            <div className="legend-swatch" style={{ background: `${colorGenome['Nucleobase A']}` }} />
            <div className="legend-swatch" style={{ background: `${colorGenome['Nucleobase T']}` }} />
            <div className="legend-swatch" style={{ background: `${colorGenome['Nucleobase C']}` }} />
            <div className="legend-swatch" style={{ background: `${colorGenome['Nucleobase G']}` }} />
        </div>
        <div className="legend-name">Legend</div>
    </div>
);

/**
 * Display a legend
 */
const GenomeLegend = (props) => (
    <Tooltip
        trigger={<LegendLabel />}
        tooltipId="genome-legend"
        css="legend-button"
        size="large"
        columnCount={props.colorBlock.length + 2}
    >
        <div className="legend-container">
            <div className="legend-block">
                <h5>Genome</h5>
                {Object.keys(colorGenome).map((nucleobase) => (
                    <div className="legend-element" key={nucleobase}>
                        <div className={`legend-swatch ${colorGenome[nucleobase] === '#ffffff' ? 'with-border' : ''}`} style={{ background: `${colorGenome[nucleobase]}` }} />
                        <div className="legend-label">{nucleobase}</div>
                    </div>
                ))}
            </div>
            <div className="legend-block">
                <h5>Genes</h5>
                {Object.keys(colorGenes).map((gene) => (
                    <div className="legend-element" key={gene}>
                        <div className={`legend-swatch ${colorGenes[gene] === '#ffffff' ? 'with-border' : ''}`} style={{ background: `${colorGenes[gene]}` }} />
                        <div className="legend-label">{gene}</div>
                    </div>
                ))}
            </div>
            {(props.colorBlock.indexOf('ccres') > -1) ?
                <div className="legend-block">
                    <h5>CCREs</h5>
                    {Object.keys(colorCCREs).map((ccre) => (
                        <div className="legend-element" key={ccre}>
                            <div className={`legend-swatch ${colorCCREs[ccre] === '#ffffff' ? 'with-border' : ''}`} style={{ background: `${colorCCREs[ccre]}` }} />
                            <div className="legend-label">{ccre}</div>
                        </div>
                    ))}
                </div>
            : null}
            {(props.colorBlock.indexOf('chromatin') > -1) ?
                <div className="legend-block">
                    <h5>Chromatin</h5>
                    {Object.keys(colorChromatinState).map((state) => (
                        <div className="legend-element" key={state}>
                            {(colorChromatinState[state].indexOf(', ') === -1) ?
                                <div className={`legend-swatch ${colorChromatinState[state] === '#ffffff' ? 'with-border' : ''}`} style={{ background: `${colorChromatinState[state]}` }} />
                            :
                                <div className={`legend-swatch ${colorChromatinState[state] === '#ffffff' ? 'with-border' : ''}`} style={{ 'background-image': `-webkit-linear-gradient(45deg, ${colorChromatinState[state].split(', ')[0]} 50%, ${colorChromatinState[state].split(', ')[1]} 50%)` }} />
                            }
                            <div className="legend-label">{state}</div>
                        </div>
                    ))}
                </div>
            : null}
        </div>
    </Tooltip>
);

GenomeLegend.propTypes = {
    colorBlock: PropTypes.array.isRequired,
};


/**
 * Display a label for a file’s track.
 */
const TrackLabel = ({ file, label, long }) => {
    const biologicalReplicates = file.biological_replicates && file.biological_replicates.join(', ');
    const splitDataset = file.dataset.split('/');
    const datasetName = splitDataset[splitDataset.length - 2];

    // For Valis in carts, build the short string.
    let cartShortLabel;
    if (label === 'cart') {
        cartShortLabel = _.compact([
            file.target && file.target.label,
            file.assay_term_name,
            file.biosample_ontology && file.biosample_ontology.term_name,
            file.annotation_type,
            file.annotation_subtype,
        ]).join(', ');
    }

    return (
        <>
            {(label === 'cart') ?
                <ul className="gb-info">
                    {cartShortLabel}
                    {long ?
                        <>
                            <li><a href={file.dataset} className="gb-accession">{datasetName}<span className="sr-only">{`Details for dataset ${datasetName}`}</span></a></li>
                            <li><a href={file['@id']} className="gb-accession">{file.title}<span className="sr-only">{`Details for file ${file.title}`}</span></a></li>
                            <li>{file.output_type}</li>
                            {biologicalReplicates ? <li>{`rep ${biologicalReplicates}`}</li> : null}
                            {file.biochemical_inputs ? <li>{(file.biochemical_inputs).join(', ')}</li> : null}
                        </>
                    : null}
                </ul>
            :
                <ul className="gb-info">
                    <li>
                        <a href={file['@id']} className="gb-accession">{file.title}<span className="sr-only">{`Details for file ${file.title}`}</span></a>
                        {(biologicalReplicates && biologicalReplicates !== '') ? <span>{` (rep ${biologicalReplicates})`}</span> : null}
                    </li>
                    {long ?
                        <>
                            {file.biosample_ontology && file.biosample_ontology.term_name ? <li>{file.biosample_ontology.term_name}</li> : null}
                            {file.target ? <li>{file.target.label}</li> : null}
                            {file.assay_term_name ? <li>{file.assay_term_name}</li> : null}
                            <li>{file.output_type}</li>
                            {file.annotation_subtype ? <li>{(file.annotation_subtype)}</li> : null}
                            {file.biochemical_inputs ? <li>{(file.biochemical_inputs).join(', ')}</li> : null}
                        </>
                    : null}
                </ul>
            }
        </>
    );
};

TrackLabel.propTypes = {
    /** File object being displayed in the track */
    file: PropTypes.object.isRequired,
    /** Determines what label to display */
    label: PropTypes.string.isRequired,
    /** True to generate a long version of the label */
    long: PropTypes.bool,
};

TrackLabel.defaultProps = {
    long: false,
};

class GenomeBrowser extends React.Component {
    constructor(props, context) {
        super(props, context);

        this.state = {
            trackList: [],
            visualizer: null,
            genome: '',
            annotation: '',
            contig: 'chr1',
            x0: 0,
            x1: 59e6,
            pinnedFiles: [],
            disableBrowserForIE: false,
            sortToggle: this.props.sortParam.map(() => true), // Indicates ascending or descending order for each sort parameter; true is descending and false is ascending
            primarySort: this.props.sortParam[0] || 'Replicates', // Indicates the final (primary) sort applied to the list of files
            colorBlock: [], // Legend entries
        };
        this.setBrowserDefaults = this.setBrowserDefaults.bind(this);
        this.clearBrowserMemory = this.clearBrowserMemory.bind(this);
        this.filesToTracks = this.filesToTracks.bind(this);
        this.drawTracks = this.drawTracks.bind(this);
        this.drawTracksResized = this.drawTracksResized.bind(this);
        this.handleGeneSearchResultClick = this.handleGeneSearchResultClick.bind(this);
        this.scrollToGeneLocation = this.scrollToGeneLocation.bind(this);
        this.setGenomeAndTracks = this.setGenomeAndTracks.bind(this);
        this.resetLocation = this.resetLocation.bind(this);
        this.sortFiles = this.sortFiles.bind(this);
        this.sortAndRefresh = this.sortAndRefresh.bind(this);
    }

    componentDidMount() {
        // Check if browser is IE 11 and disable browser if so
        if (BrowserFeat.getBrowserCaps('uaTrident')) {
            this.setState({ disableBrowserForIE: true });
        } else {
            // Load GenomeVisualizer library
            // We have to wait for the component to mount because the library relies on window variable
            require.ensure(['genome-visualizer'], (require) => {
                this.GV = require('genome-visualizer');
                // Determine pinned files based on genome, filter and sort files, compute and draw tracks
                this.setGenomeAndTracks();
            });
        }
    }

    /* eslint-disable react/no-did-update-set-state */
    componentDidUpdate(prevProps, prevState) {
        if (!(this.state.disableBrowserForIE) && this.GV) {
            if (this.state.contig !== prevState.contig) {
                if (this.state.visualizer) {
                    this.state.visualizer.setLocation({ contig: this.state.contig, x0: this.state.x0, x1: this.state.x1 });
                }
            }

            if (this.props.assembly !== prevProps.assembly || this.props.annotation !== prevProps.annotation) {
                // Determine pinned files based on genome, filter and sort files, compute and draw tracks
                this.setGenomeAndTracks();
            }

            // If the parent container changed size, we need to update the browser width
            if (this.props.expanded !== prevProps.expanded) {
                setTimeout(this.drawTracksResized, 1000);
            }

            if (!(_.isEqual(this.props.files, prevProps.files))) {
                const primarySortIndex = this.props.sortParam.indexOf(this.state.primarySort);
                const primarySortToggle = this.state.sortToggle[primarySortIndex];
                this.sortAndRefresh(this.state.primarySort, primarySortToggle, primarySortIndex, false);
            }
        }
    }
    /* eslint-enable react/no-did-update-set-state */

    componentWillUnmount() {
        // Recommendation from George of Valis to clear web-browser memory used by Valis.
        this.clearBrowserMemory();
        if (this.state.visualizer) {
            this.state.visualizer.appCanvasRef.componentWillUnmount();
        }

        // save co-ordinates to be used to restore location if user comes back to genome_browser tab/area
        const { x0, x1, contig } = readGenomeBrowserLabelCoordinates();

        window.sessionStorage.setItem(GV_COORDINATES_KEY, JSON.stringify({
            contig,
            x0,
            x1,
            pinnedFiles: this.state.pinnedFiles,
        }));
    }

    handleGeneSearchResultClick(gene) {
        this.scrollToGeneLocation(gene);
    }

    setBrowserDefaults(assembly, annotation, resolve) {
        const { contig, x0, x1, pinnedFiles } = getDefaultCoordinates(assembly, annotation);

        this.setState({ contig, x0, x1, pinnedFiles }, () => {
            if (resolve) {
                resolve('success!');
            }
        });
    }

    setGenomeAndTracks() {
        const genome = mapGenome(this.props.assembly);
        const { annotation } = this.props;
        this.setState({ genome, annotation });
        // Determine genome and Gencode pinned files for selected assembly
        const genomePromise = new Promise((resolve) => {
            this.setBrowserDefaults(genome, annotation, resolve);
        });
        // Make sure that we have these pinned files before we convert the files to tracks and chart them
        genomePromise.then(() => {
            const primarySortIndex = this.props.sortParam.indexOf(this.state.primarySort);
            const primarySortToggle = this.state.sortToggle[primarySortIndex];
            this.sortAndRefresh(this.state.primarySort, primarySortToggle, primarySortIndex, false);
        });
    }

    scrollToGeneLocation(gene) {
        this.state.visualizer.setLocation(
            gene.locationForVisualization(
                getAssemblyWithoutGenomeAnnotationOrMinimal(
                    this.props.assembly
                )
            )
        );
    }

    /**
     * Clear any remains of memory Valis has used within the web browser.
     */
    clearBrowserMemory() {
        if (this.state.visualizer) {
            this.state.visualizer.stopFrameLoop();
            this.state.visualizer.clearCaches();
        }
    }

    // Sort file object by an arbitrary number of sort parameters
    // "primarySort" is the primary sort parameter
    // "sortDirection" refers to ascending or descending order
    // "sortIdx" keeps track of the index of the primarySort in this.state.sortToggle
    // "toggleFlag" indicates whether the primarySort has changed and if its sortDirection should be reversed
    //      (i.e., whether this function is being called upon initialization or upon the user clicking on a sort button)
    sortFiles(primarySort, sortDirection, sortIdx, toggleFlag) {
        let propsFiles = [];
        const domain = `${window.location.protocol}//${window.location.hostname}`;

        // Make sure that the sorting parameter "primarySort" is the last element in the sort array
        const orderedSortParam = [...this.props.sortParam];
        const fromIdx = orderedSortParam.indexOf(primarySort);
        orderedSortParam.splice((orderedSortParam.length - 1), 0, orderedSortParam.splice(fromIdx, 1)[0]);

        // The sort button for "Output type" is secretly also a sort button for "File type", so that all the bigWigs and bigBeds are grouped with each other
        // Here we add "File type" to the sort array if it's not already there and make sure that it is the sort parameter after "Output type"
        const fileIdx = orderedSortParam.indexOf('File type');
        const outputIdx = orderedSortParam.indexOf('Output type');
        if (fileIdx > -1) {
            orderedSortParam.splice((outputIdx + 1), 0, orderedSortParam.splice(fileIdx, 1)[0]);
        } else {
            orderedSortParam.splice((outputIdx + 1), 0, 'File type');
        }

        // Initialize files
        if (domain.includes('localhost')) {
            propsFiles = dummyFiles;
        } else {
            // Filter files to include only bigWig and bigBed formats, and not 'bigBed bedMethyl' formats and only released or in progress files
            propsFiles = filterForVisualizableFiles(this.props.files);
        }
        let files = propsFiles;

        // Apply sort parameters
        if (this.props.displaySort) {
            orderedSortParam.forEach((param) => {
                files = _.chain(files)
                    .sortBy((obj) => sortLookUp(obj, param));
            });
            files = files.value();
        }

        // sortBy sorts in ascending order and sortDirection is true if descending
        // We want to reverse the sort order when the sort is toggled and ascending (to make it descending)
        if (sortDirection && toggleFlag) {
            files = files.reverse();
        }

        // Update state if function has been triggered by button click and sort and sort direction are new
        if (toggleFlag) {
            this.setState((state) => {
                const newSortToggle = [...state.sortToggle];
                newSortToggle[sortIdx] = !newSortToggle[sortIdx];
                return {
                    primarySort,
                    sortToggle: newSortToggle,
                };
            });
        }
        return files;
    }

    // Call sortFiles() to sort file object by an arbitrary number of sort parameters
    // Re-draw the tracks on the genome browser
    sortAndRefresh(primarySort, sortDirection, sortIdx, toggleFlag) {
        let files = [];
        let newFiles = [];
        const domain = `${window.location.protocol}//${window.location.hostname}`;
        files = this.sortFiles(primarySort, sortDirection, sortIdx, toggleFlag).filter((file) => file.assembly === this.props.assembly);
        newFiles = [...this.state.pinnedFiles, ...files];
        newFiles = _.uniq(newFiles, (file) => file.href);
        let tracks = [];
        if (files.length > 0) {
            tracks = this.filesToTracks(newFiles, this.props.label, domain);
        }
        let { contig, x0, x1 } = this.state;
        if (this.chartdisplay) {
            const coordinates = readGenomeBrowserLabelCoordinates();

            ({ x0, x1, contig } = coordinates);
        }
        this.setState({
            trackList: tracks,
            contig,
            x0,
            x1,
        }, () => {
            if (this.chartdisplay && tracks.length > 0) {
                this.drawTracks(this.chartdisplay);
            }
        });
    }

    filesToTracks(files, label, domain) {
        const tracks = files.map((file) => {
            if (file.output_type === 'candidate Cis-Regulatory Elements' && this.state.colorBlock.indexOf('ccres') === -1) {
                this.setState((prevState) => ({
                    colorBlock: [...prevState.colorBlock, 'ccres'],
                }));
            }
            if ((file.output_type === 'semi-automated genome annotation' || file.output_type === 'HMM predicted chromatin state') && this.state.colorBlock.indexOf('chromatin') === -1) {
                this.setState((prevState) => ({
                    colorBlock: [...prevState.colorBlock, 'chromatin'],
                }));
            }
            const defaultHeight = 29;
            const extraLineHeight = 14;
            const maxCharPerLine = 26;
            let labelLength = file.title ? Math.floor(file.title.length / maxCharPerLine) : 0;
            // Some labels on the cart which have a target, assay name, and biosample are too long for one line (some actually extend to three lines)
            // Here we do some approximate math to try to figure out how many lines the labels extend to assuming that ~30 characters fit on one line
            // Labels on the experiment pages are short enough to fit on one line (they contain less information) so we can bypass these calculations for those pages
            if (label === 'cart') {
                labelLength += file.target ? file.target.label.length + 2 : 0;
                labelLength += file.assay_term_name ? file.assay_term_name.length + 2 : 0;
                labelLength += file.biosample_ontology && file.biosample_ontology.term_name ? file.biosample_ontology.term_name.length + 2 : 0;
                labelLength += file.annotation_type ? file.annotation_type.length : 0;
                labelLength += file.annotation_subtype ? file.annotation_subtype.length : 0;
                labelLength += file.biochemical_inputs ? file.biochemical_inputs.length : 0;
                labelLength = Math.floor(labelLength / maxCharPerLine);
            }
            if (file.name) {
                const trackObj = {};
                trackObj.name = <div className="gb-info"><i>{file.name}</i></div>;
                trackObj.type = 'signal';
                trackObj.path = file.href;
                trackObj.heightPx = labelLength > 0 ? (defaultHeight + (extraLineHeight * labelLength)) : defaultHeight;
                trackObj.expandedHeightPx = 140;
                return trackObj;
            }
            if (file.file_format === 'bigWig') {
                const trackObj = {};
                trackObj.name = <TrackLabel label={label} file={file} />;
                trackObj.longname = <TrackLabel label={label} file={file} long />;
                trackObj.type = 'signal';
                trackObj.path = domain + file.href;
                trackObj.heightPx = labelLength > 0 ? (defaultHeight + (extraLineHeight * labelLength)) : defaultHeight;
                trackObj.expandedHeightPx = 135;
                return trackObj;
            }
            if (file.file_format === 'vdna-dir') {
                const trackObj = {};
                trackObj.name = <ul className="gb-info"><li>{this.props.assembly.split(' ')[0]}</li></ul>;
                trackObj.type = 'sequence';
                trackObj.path = file.href;
                trackObj.heightPx = 35;
                trackObj.expandable = false;
                return trackObj;
            }
            if (file.file_format === 'vgenes-dir') {
                const trackObj = {};
                trackObj.name = <ul className="gb-info"><li>{file.title}</li></ul>;
                trackObj.type = 'annotation';
                trackObj.path = file.href;
                trackObj.heightPx = 115;
                trackObj.expandable = false;
                trackObj.displayLabels = true;
                return trackObj;
            }
            if (file.file_format === 'variant') {
                const trackObj = {};
                trackObj.name = <ul className="gb-info"><li>{file.title}</li></ul>;
                trackObj.type = 'variant';
                trackObj.path = file.href || file.path; // some titles like dBSNP set path
                trackObj.heightPx = 40;
                trackObj.expandable = true;
                trackObj.displayLabels = true;
                return trackObj;
            }
            const trackObj = {};
            trackObj.name = <TrackLabel file={file} label={label} />;
            trackObj.longname = <TrackLabel file={file} label={label} long />;
            trackObj.type = 'annotation';
            trackObj.path = domain + file.href;
            trackObj.expandable = true;
            trackObj.displayLabels = false;
            trackObj.heightPx = labelLength > 0 ? (defaultHeight + (extraLineHeight * labelLength)) : defaultHeight;
            trackObj.expandedHeightPx = 135;
            trackObj.fileFormatType = file.file_format_type;
            // bigBed bedRNAElements, bigBed peptideMapping, bigBed bedExonScore, bed12, and bed9 have two tracks and need extra height
            // Convert to lower case in case of inconsistency in the capitalization of the file format in the data
            if (file.file_format_type &&
                (['bedrnaelements', 'peptidemapping', 'bedexonscore', 'bed12', 'bed9'].indexOf(file.file_format_type.toLowerCase()) > -1)) {
                const openedOutputTypes = [
                    'predicted transcription start sites',
                    'contigs',
                    'splice junctions',
                    'clusters',
                    'exon quantifications',
                    'unfiltered peptide quantification',
                    'filtered peptide quantification',
                ];
                trackObj.name = <TrackLabel file={file} label={label} long />;

                const opened = openedOutputTypes.includes(file.output_type);
                trackObj.heightPx = opened ? 95 : trackObj.heightPx;
            }
            return trackObj;
        });
        return tracks;
    }

    drawTracksResized() {
        if (this.chartdisplay) {
            this.state.visualizer.render({
                width: this.chartdisplay.clientWidth,
                height: this.state.visualizer.getContentHeight(),
            }, this.chartdisplay);
        }
    }

    drawTracks(container) {
        const { contig, x0, x1, trackList } = this.state;
        const visualizer = new this.GV.GenomeVisualizer({
            clampToTracks: true,
            reorderTracks: true,
            removableTracks: false,
            panels: [{
                location: { contig, x0, x1 },
            }],
            tracks: trackList,
        });
        this.setState({ visualizer });
        this.clearBrowserMemory();
        visualizer.render({
            width: this.chartdisplay.clientWidth,
            height: visualizer.getContentHeight(),
        }, container);
        visualizer.addEventListener('track-resize', this.drawTracksResized);
        window.addEventListener('resize', this.drawTracksResized);
    }

    resetLocation() {
        const { contig, x0, x1 } = getDefaultCoordinates(this.state.genome, this.state.annotation, true);
        this.state.visualizer.setLocation({ contig, x0, x1 });
    }

    render() {
        return (
            <>
                {(this.state.trackList.length > 0 && this.state.genome !== null && !(this.state.disableBrowserForIE)) ?
                 <>
                     <div className="gene-search">
                         <i className="icon icon-search" />
                         <div className="search-instructions">Search for a gene</div>
                         <GeneSearch
                             assembly={
                                 getAssemblyWithoutGenomeAnnotationOrMinimal(
                                     this.props.assembly
                                 )
                             }
                             handleClick={this.handleGeneSearchResultClick}
                         />
                     </div>
                     <div className="horizontal-control-container">
                         {this.props.displaySort ?
                              <>
                                  <div className="sort-label">Sort by: </div>
                                  {this.props.sortParam.map((param, paramIdx) => <button type="button" className={`sort-button ${param === this.state.primarySort ? 'active' : ''}`} key={param.replace(/\s/g, '_')} onClick={() => this.sortAndRefresh(param, this.state.sortToggle[paramIdx], paramIdx, true)}><i className={this.state.sortToggle[paramIdx] ? 'tcell-desc' : 'tcell-asc'} /><div className="sort-label">{param}</div></button>)}
                              </>
                         : null}
                         <GenomeLegend colorBlock={this.state.colorBlock} />
                     </div>
                     <div className="browser-container">
                         <button type="button" className="reset-browser-button" onClick={this.resetLocation}>
                             <i className="icon icon-undo" />
                             <span className="reset-title">Reset coordinates</span>
                         </button>
                         <div ref={(div) => { this.chartdisplay = div; }} className="valis-browser" />
                     </div>
                 </>
                 :
                 <>
                     {(this.state.disableBrowserForIE) ?
                      <div className="browser-error valis-browser">The genome browser does not support Internet Explorer. Please upgrade your browser to Edge to visualize files on ENCODE.</div>
                      :
                      <div className="browser-error valis-browser">There are no visualizable results.</div>
                     }
                 </>
                }
            </>
        );
    }
}

GenomeBrowser.propTypes = {
    files: PropTypes.array.isRequired,
    expanded: PropTypes.bool.isRequired,
    assembly: PropTypes.string.isRequired,
    annotation: PropTypes.string,
    label: PropTypes.string.isRequired,
    sortParam: PropTypes.array,
    displaySort: PropTypes.bool,
};

GenomeBrowser.defaultProps = {
    annotation: '',
    sortParam: ['Replicates', 'Output type'], // Array of parameters for sorting file object
    displaySort: false, // Determines if sort buttons should be displayed
};

GenomeBrowser.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};

export default GenomeBrowser;
