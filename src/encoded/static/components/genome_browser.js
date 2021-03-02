import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { FetchedData, Param } from './fetched';
import { BrowserFeat } from './browserfeat';
import { filterForVisualizableFiles } from './objectutils';
import AutocompleteBox from './region_search';


/**
 * Maps long annotation_type values to shorter versions for Valis track labels. Any not included
 * remain unchanged.
 */
export const annotationTypeMap = {
    'candidate Cis-Regulatory Elements': 'cCRE',
    'representative DNase hypersensitivity sites (rDHSs)': 'rDHS',
};

const GV_COORDINATES_KEY = 'ENCODE-GV-coordinates';

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
const getDefaultCoordinates = (assemblyAnnotation, ignoreCache = false) => {
    const assembly = assemblyAnnotation.split(' ')[0];
    // Files to be displayed on all genome browser results
    let pinnedFiles = [];
    let contig = null;
    let x0 = null;
    let x1 = null;
    const gVState = ignoreCache ? null : window.sessionStorage.getItem(GV_COORDINATES_KEY);

    if (gVState) {
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
        ];
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
        ];
        contig = 'chrII';
        x0 = 232475;
        x1 = 237997;
    }

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
                        </>
                    : null}
                </ul>
            :
                <ul className="gb-info">
                    <li>
                        <a href={file['@id']} className="gb-accession">{file.title}<span className="sr-only">{`Details for file ${file.title}`}</span></a>
                        {(biologicalReplicates !== '') ? <span>{` (rep ${biologicalReplicates})`}</span> : null}
                    </li>
                    {long ?
                        <>
                            {file.biosample_ontology && file.biosample_ontology.term_name ? <li>{file.biosample_ontology.term_name}</li> : null}
                            {file.target ? <li>{file.target.label}</li> : null}
                            {file.assay_term_name ? <li>{file.assay_term_name}</li> : null}
                            <li>{file.output_type}</li>
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

const GenomeBrowser = (props, context) => {
    const [trackList, setTrackList] = React.useState([]);
    const [visualizer, setVisualizer] = React.useState(null);
    const [showAutoSuggest, setShowAutoSuggest] = React.useState(true);
    const [searchTerm, setSearchTerm] = React.useState('');
    const [genome, setGenome] = React.useState('');
    const [contig, setContig] = React.useState('chr1');
    const [x0, setX0] = React.useState(0);
    const [x1, setX1] = React.useState(59e6);
    const [pinnedFiles, setPinnedFiles] = React.useState([]);
    const [disableBrowserForIE, setDisableBrowserForIE] = React.useState(false);
    // Indicates ascending or descending order for each sort parameter; true is descending and false is ascending
    const [sortToggle, setSortToggle] = React.useState(props.sortParam.map(() => true));
    // Indicates the final (primary) sort applied to the list of files
    const [primarySort, setPrimarySort] = React.useState(props.sortParam[0] || 'Replicates');
    const [GV, setGV] = React.useState(null);
    const chartdisplay = React.useRef(null);
    const [gene, setGene] = React.useState(null);

    /* eslint-disable react/no-did-update-set-state */
    // componentDidUpdate(prevProps, prevState) {
    //     console.log('click');
    //     if (!(this.state.disableBrowserForIE) && this.GV) {
    //         console.log('component did update');
    //         // console.log(this.props);
    //         // console.log(prevProps);
    //
    //         if (this.state.contig !== prevState.contig) {
    //             console.log('updated location');
    //             if (this.state.visualizer) {
    //                 this.state.visualizer.setLocation({ contig: this.state.contig, x0: this.state.x0, x1: this.state.x1 });
    //             }
    //         }
    //
    //         if (this.props.assembly !== prevProps.assembly) {
    //             console.log('assembly changed');
    //             // Determine pinned files based on genome, filter and sort files, compute and draw tracks
    //             this.setGenomeAndTracks();
    //             // Clear the gene search
    //             this.setState({ searchTerm: '' });
    //         }
    //
    //         // If the parent container changed size, we need to update the browser width
    //         if (this.props.expanded !== prevProps.expanded) {
    //             console.log('resize');
    //             setTimeout(this.drawTracksResized, 1000);
    //         }
    //
    //         if (!(_.isEqual(this.props.files, prevProps.files))) {
    //             console.log('files updated');
    //             const primarySortIndex = this.props.sortParam.indexOf(this.state.primarySort);
    //             const primarySortToggle = this.state.sortToggle[primarySortIndex];
    //             this.sortAndRefresh(this.state.primarySort, primarySortToggle, primarySortIndex, false);
    //         }
    //     }
    // }
    /* eslint-enable react/no-did-update-set-state */

    // componentWillUnmount() {
    //     // Recommendation from George of Valis to clear web-browser memory used by Valis.
    //     this.clearBrowserMemory();
    //     if (this.state.visualizer) {
    //         this.state.visualizer.appCanvasRef.componentWillUnmount();
    //     }
    //
    //     // save co-ordinates to be used to restore location if user comes back to genome_browser tab/area
    //     const { x0, x1, contig } = readGenomeBrowserLabelCoordinates();
    //
    //     window.sessionStorage.setItem(GV_COORDINATES_KEY, JSON.stringify({
    //         contig,
    //         x0,
    //         x1,
    //         pinnedFiles: this.state.pinnedFiles,
    //     }));
    // }

    const handleChange = (e) => {
        setShowAutoSuggest(true);
        setSearchTerm(e.target.value);
    };

    const handleAutocompleteClick = (term, id, name) => {
        const newTerms = {};
        const inputNode = gene;
        inputNode.value = term;
        newTerms[name] = id;
        setShowAutoSuggest(true);
        setSearchTerm(term);
        inputNode.focus();
        // Now let the timer update the terms state when it gets around to it.
    };

    const handleOnFocus = () => {
        setShowAutoSuggest(false);
        const coordinateHref = `/suggest/?genome=${genome}&q=${searchTerm}`;
        getCoordinateData(coordinateHref, context.fetch).then((response) => {
            // Find the response line that matches the search
            const responseIndex = response['@graph'].findIndex((responseLine) => responseLine.text === searchTerm);

            // Find the annotation line that matches the genome selected in the fake facets
            const { annotations } = response['@graph'][responseIndex]._source;
            const annotationIndex = annotations.findIndex((annotation) => annotation.assembly_name === genome);
            const annotation = annotations[annotationIndex];

            // Compute gene location information from the annotation
            const annotationLength = +annotation.end - +annotation.start;
            const newContig = `chr${annotation.chromosome}`;
            const xStart = +annotation.start - (annotationLength / 2);
            const xEnd = +annotation.end + (annotationLength / 2);

            if (contig !== '') {
                visualizer.setLocation({
                    newContig,
                    x0: xStart,
                    x1: xEnd,
                });
            }
        });
    };

    function setBrowserDefaults(assemblyAnnotation, resolve) {
        const { newContig, newX0, newX1, newPinnedFiles } = getDefaultCoordinates(assemblyAnnotation);
        setContig(newContig);
        setX0(newX0);
        setX1(newX1);
        setPinnedFiles(newPinnedFiles);
        resolve('success!');
    }

    const filesToTracks = (files, label, domain) => {
        const tracks = files.map((file) => {
            let labelLength = 0;
            const defaultHeight = 34;
            const extraLineHeight = 12;
            const maxCharPerLine = 26;
            // Some labels on the cart which have a target, assay name, and biosample are too long for one line (some actually extend to three lines)
            // Here we do some approximate math to try to figure out how many lines the labels extend to assuming that ~30 characters fit on one line
            // Labels on the experiment pages are short enough to fit on one line (they contain less information) so we can bypass these calculations for those pages
            if (label === 'cart') {
                labelLength += file.target ? file.target.label.length + 2 : 0;
                labelLength += file.assay_term_name ? file.assay_term_name.length + 2 : 0;
                labelLength += file.biosample_ontology && file.biosample_ontology.term_name ? file.biosample_ontology.term_name.length + 2 : 0;
                labelLength += file.annotation_type ? file.annotation_type.length : 0;
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
                trackObj.expandedHeightPx = 140;
                return trackObj;
            }
            if (file.file_format === 'vdna-dir') {
                const trackObj = {};
                trackObj.name = <ul className="gb-info"><li>{props.assembly.split(' ')[0]}</li></ul>;
                trackObj.type = 'sequence';
                trackObj.path = file.href;
                trackObj.heightPx = 40;
                trackObj.expandable = false;
                return trackObj;
            }
            if (file.file_format === 'vgenes-dir') {
                const trackObj = {};
                trackObj.name = <ul className="gb-info"><li>{file.title}</li></ul>;
                trackObj.type = 'annotation';
                trackObj.path = file.href;
                trackObj.heightPx = 120;
                trackObj.expandable = false;
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
            trackObj.expandedHeightPx = 140;
            trackObj.fileFormatType = file.file_format_type;
            // bigBed bedRNAElements, bigBed peptideMapping, bigBed bedExonScore, bed12, and bed9 have two tracks and need extra height
            // Convert to lower case in case of inconsistency in the capitalization of the file format in the data
            if (file.file_format_type &&
                (['bedrnaelements', 'peptidemapping', 'bedexonscore', 'bed12', 'bed9'].indexOf(file.file_format_type.toLowerCase()) > -1)) {
                trackObj.name = <TrackLabel file={file} label={label} long />;
                trackObj.heightPx = 95;
                trackObj.expandable = false;
            }
            return trackObj;
        });
        return tracks;
    };

    /**
     * Clear any remains of memory Valis has used within the web browser.
     */
    const clearBrowserMemory = () => {
        if (visualizer) {
            visualizer.stopFrameLoop();
            visualizer.clearCaches();
        }
    };

    // Sort file object by an arbitrary number of sort parameters
    // "primarySort" is the primary sort parameter
    // "sortDirection" refers to ascending or descending order
    // "sortIdx" keeps track of the index of the primarySort in this.state.sortToggle
    // "toggleFlag" indicates whether the primarySort has changed and if its sortDirection should be reversed
    //      (i.e., whether this function is being called upon initialization or upon the user clicking on a sort button)
    const sortFiles = (sortDirection, sortIdx, toggleFlag) => {
        let propsFiles = [];
        const domain = `${window.location.protocol}//${window.location.hostname}`;

        // Make sure that the sorting parameter "primarySort" is the last element in the sort array
        const orderedSortParam = [...props.sortParam];
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
            propsFiles = filterForVisualizableFiles(props.files);
        }
        let files = propsFiles;

        // Apply sort parameters
        if (props.displaySort) {
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
            const newSortToggle = [...sortToggle];
            newSortToggle[sortIdx] = !newSortToggle[sortIdx];
            setPrimarySort(primarySort);
            setSortToggle(newSortToggle);
        }
        return files;
    };

    function drawTracks(container) {
        const newVisualizer = new GV.GenomeVisualizer({
            clampToTracks: true,
            reorderTracks: true,
            removableTracks: false,
            panels: [{
                location: { contig, x0, x1 },
            }],
            tracks: trackList,
        });
        setVisualizer(newVisualizer);
        clearBrowserMemory();
        visualizer.render({
            width: chartdisplay.clientWidth,
            height: visualizer.getContentHeight(),
        }, container);
        // visualizer.addEventListener('track-resize', drawTracksResized);
        // window.addEventListener('resize', drawTracksResized);
    }

    // Call sortFiles() to sort file object by an arbitrary number of sort parameters
    // Re-draw the tracks on the genome browser
    function sortAndRefresh(sort, sortDirection, sortIdx, toggleFlag) {
        setPrimarySort(sort);
        let files = [];
        let newFiles = [];
        const domain = `${window.location.protocol}//${window.location.hostname}`;
        files = sortFiles(primarySort, sortDirection, sortIdx, toggleFlag);
        console.log(files);
        console.log(pinnedFiles);
        // newFiles = [...pinnedFiles, ...files];
        // let tracks = [];
        // if (files.length > 0) {
        //     tracks = filesToTracks(newFiles, props.label, domain);
        // }
        // if (chartdisplay) {
        //     const coordinates = readGenomeBrowserLabelCoordinates();
        //     const { newX0, newX1, newContig } = coordinates;
        //     setContig(newContig);
        //     setX0(newX0);
        //     setX1(newX1);
        // }
        // setTrackList(tracks);
        // if (chartdisplay && tracks.length > 0) {
        //     drawTracks(chartdisplay);
        // }
    }

    // const drawTracksResized = () => {
    //     if (this.chartdisplay) {
    //         visualizer.render({
    //             width: this.chartdisplay.clientWidth,
    //             height: visualizer.getContentHeight(),
    //         }, this.chartdisplay);
    //     }
    // };

    const setGenomeAndTracks = () => {
        setGenome(mapGenome(props.assembly));
        // Determine genome and Gencode pinned files for selected assembly
        const genomePromise = new Promise((resolve) => {
            setBrowserDefaults(genome, resolve);
        });
        // Make sure that we have these pinned files before we convert the files to tracks and chart them
        genomePromise.then(() => {
            console.log('do we even get here?');
            const primarySortIndex = props.sortParam.indexOf(primarySort);
            const primarySortToggle = sortToggle[primarySortIndex];
            sortAndRefresh(primarySort, primarySortToggle, primarySortIndex, false);
        });
    };

    React.useEffect(() => {
        // Check if browser is IE 11 and disable browser if so
        if (BrowserFeat.getBrowserCaps('uaTrident')) {
            setDisableBrowserForIE(true);
        } else {
            // Load GenomeVisualizer library
            // We have to wait for the component to mount because the library relies on window variable
            require.ensure(['genome-visualizer'], (require) => {
                setGV(require('genome-visualizer'));
                // Determine pinned files based on genome, filter and sort files, compute and draw tracks
                setGenomeAndTracks();
            });
        }
    });

    const resetLocation = () => {
        const { newContig, newX0, newX1 } = getDefaultCoordinates(genome, true);
        visualizer.setLocation({ newContig, newX0, newX1 });
    };

    return (
        <>
            {(trackList.length > 0 && genome !== null && !(disableBrowserForIE)) ?
                <>
                    { (genome.indexOf('GRC') !== -1) ?
                        <div className="gene-search">
                            <i className="icon icon-search" />
                            <div className="search-instructions">Search for a gene</div>
                            <div className="searchform">
                                <input id="gene" ref={(input) => { setGene(input); }} aria-label="search for gene name" placeholder="Enter gene name here" value={searchTerm} onChange={handleChange} />
                                {(showAutoSuggest && searchTerm) ?
                                    <FetchedData loadingComplete>
                                        <Param
                                            name="auto"
                                            url={`/suggest/?genome=${genome}&q=${searchTerm}`}
                                            type="json"
                                        />
                                        <AutocompleteBox
                                            name="annotation"
                                            userTerm={searchTerm}
                                            handleClick={handleAutocompleteClick}
                                        />
                                    </FetchedData>
                                : null}
                            </div>
                            <button type="button" className="submit-gene-search btn btn-info" onClick={handleOnFocus}>Submit</button>
                        </div>
                    : null}
                    {props.displaySort ?
                        <div className="sort-control-container">
                            <div className="sort-label">Sort by: </div>
                            {props.sortParam.map((param, paramIdx) => <button type="button" className={`sort-button ${param === primarySort ? 'active' : ''}`} key={param.replace(/\s/g, '_')} onClick={() => sortAndRefresh(param, sortToggle[paramIdx], paramIdx, true)}><i className={sortToggle[paramIdx] ? 'tcell-desc' : 'tcell-asc'} /><div className="sort-label">{param}</div></button>)}
                        </div>
                    : null}
                    <div className="browser-container">
                        <button type="button" className="reset-browser-button" onClick={resetLocation}>
                            <i className="icon icon-undo" />
                            <span className="reset-title">Reset coordinates</span>
                        </button>
                        <div ref={chartdisplay} className="valis-browser" />
                    </div>
                </>
            :
                <>
                    {(disableBrowserForIE) ?
                        <div className="browser-error valis-browser">The genome browser does not support Internet Explorer. Please upgrade your browser to Edge to visualize files on ENCODE.</div>
                    :
                        <div className="browser-error valis-browser">There are no visualizable results.</div>
                    }
                </>
            }
        </>
    );
};

GenomeBrowser.propTypes = {
    files: PropTypes.array.isRequired,
    expanded: PropTypes.bool.isRequired,
    assembly: PropTypes.string,
    label: PropTypes.string.isRequired,
    sortParam: PropTypes.array,
    displaySort: PropTypes.bool,
};

GenomeBrowser.defaultProps = {
    assembly: '',
    sortParam: ['Replicates', 'Output type'], // Array of parameters for sorting file object
    displaySort: false, // Determines if sort buttons should be displayed
};

GenomeBrowser.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};

export default GenomeBrowser;
