import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { FetchedData, Param } from './fetched';
import { BrowserFeat } from './browserfeat';
import { filterForVisualizableFiles } from './objectutils';
import AutocompleteBox from './region_search';

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
    return (
        <React.Fragment>
            {(label === 'cart') ?
                <ul className="gb-info">
                    {file.target ? <span>{file.target.label}, </span> : null}
                    {file.assay_term_name ? <span>{file.assay_term_name}, </span> : null}
                    {file.biosample_ontology && file.biosample_ontology.term_name ? <span>{file.biosample_ontology.term_name}</span> : null}
                    {long ?
                        <React.Fragment>
                            <li><a href={file.dataset} className="gb-accession">{datasetName}<span className="sr-only">{`Details for dataset ${datasetName}`}</span></a></li>
                            <li><a href={file['@id']} className="gb-accession">{file.title}<span className="sr-only">{`Details for file ${file.title}`}</span></a></li>
                            <li>{file.output_type}</li>
                            <li>{`rep ${biologicalReplicates}`}</li>
                        </React.Fragment>
                    : null}
                </ul>
            :
                <ul className="gb-info">
                    <li>
                        <a href={file['@id']} className="gb-accession">{file.title}<span className="sr-only">{`Details for file ${file.title}`}</span></a>
                        {(biologicalReplicates !== '') ? <span>{` (rep ${biologicalReplicates})`}</span> : null}
                    </li>
                    {long ?
                        <React.Fragment>
                            {file.biosample_ontology && file.biosample_ontology.term_name ? <li>{file.biosample_ontology.term_name}</li> : null}
                            {file.target ? <li>{file.target.label}</li> : null}
                            {file.assay_term_name ? <li>{file.assay_term_name}</li> : null}
                            <li>{file.output_type}</li>
                        </React.Fragment>
                    : null}
                </ul>
            }
        </React.Fragment>
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
            showAutoSuggest: true,
            searchTerm: '',
            genome: '',
            contig: 'chr1',
            x0: 0,
            x1: 59e6,
            pinnedFiles: [],
            disableBrowserForIE: false,
            sortToggle: this.props.sortParam.map(() => true), // Indicates ascending or descending order for each sort parameter; true is descending and false is ascending
            primarySort: this.props.sortParam[0] || 'Replicates', // Indicates the final (primary) sort applied to the list of files
        };
        this.setBrowserDefaults = this.setBrowserDefaults.bind(this);
        this.clearBrowserMemory = this.clearBrowserMemory.bind(this);
        this.filesToTracks = this.filesToTracks.bind(this);
        this.drawTracks = this.drawTracks.bind(this);
        this.drawTracksResized = this.drawTracksResized.bind(this);
        this.handleChange = this.handleChange.bind(this);
        this.handleAutocompleteClick = this.handleAutocompleteClick.bind(this);
        this.handleOnFocus = this.handleOnFocus.bind(this);
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

    componentDidUpdate(prevProps, prevState) {
        if (!(this.state.disableBrowserForIE) && this.GV) {
            if (this.state.contig !== prevState.contig) {
                if (this.state.visualizer) {
                    this.state.visualizer.setLocation({ contig: this.state.contig, x0: this.state.x0, x1: this.state.x1 });
                }
            }

            if (this.props.assembly !== prevProps.assembly) {
                // Determine pinned files based on genome, filter and sort files, compute and draw tracks
                this.setGenomeAndTracks();
                // Clear the gene search
                this.setState({ searchTerm: '' });
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

    componentWillUnmount() {
        // Recommendation from George of Valis to clear web-browser memory used by Valis.
        this.clearBrowserMemory();
        if (this.state.visualizer) {
            this.state.visualizer.appCanvasRef.componentWillUnmount();
        }
    }

    setBrowserDefaults(assemblyAnnotation, resolve) {
        const assembly = assemblyAnnotation.split(' ')[0];
        // Files to be displayed on all genome browser results
        let pinnedFiles = [];
        let contig = null;
        let x0 = null;
        let x1 = null;
        if (assembly === 'GRCh38') {
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
        this.setState({
            contig,
            x0,
            x1,
            pinnedFiles,
        }, () => {
            resolve('success!');
        });
    }

    setGenomeAndTracks() {
        const genome = mapGenome(this.props.assembly);
        this.setState({ genome });
        // Determine genome and Gencode pinned files for selected assembly
        const genomePromise = new Promise((resolve) => {
            this.setBrowserDefaults(genome, resolve);
        });
        // Make sure that we have these pinned files before we convert the files to tracks and chart them
        genomePromise.then(() => {
            const primarySortIndex = this.props.sortParam.indexOf(this.state.primarySort);
            const primarySortToggle = this.state.sortToggle[primarySortIndex];
            this.sortAndRefresh(this.state.primarySort, primarySortToggle, primarySortIndex, false);
        });
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
        orderedSortParam.forEach((param) => {
            files = _.chain(files)
                .sortBy(obj => sortLookUp(obj, param));
        });
        files = files.value();

        // sortBy sorts in ascending order and sortDirection is true if descending
        // We want to reverse the sort order when the sort is toggled and ascending (to make it descending)
        if (sortDirection && toggleFlag) {
            files = files.reverse();
        }

        // Update state if function has been triggered by button click and sort and sort direction are new
        if (toggleFlag) {
            const newSortToggle = [...this.state.sortToggle];
            newSortToggle[sortIdx] = !newSortToggle[sortIdx];
            this.setState({
                primarySort,
                sortToggle: newSortToggle,
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
        files = this.sortFiles(primarySort, sortDirection, sortIdx, toggleFlag);
        newFiles = [...this.state.pinnedFiles, ...files];
        let tracks = [];
        if (files.length > 0) {
            tracks = this.filesToTracks(newFiles, this.props.label, domain);
        }
        let contig = this.state.contig;
        let x0 = this.state.x0;
        let x1 = this.state.x1;
        if (this.chartdisplay) {
            const scrollLocation = this.chartdisplay.getElementsByClassName('hpgv_panel-header')[0].getElementsByTagName('span')[0].innerText;
            const splitScrollLocation = scrollLocation.split(' ');
            contig = splitScrollLocation[0];
            x0 = (splitScrollLocation[1].indexOf('Mbp') > -1) ? +splitScrollLocation[1].replace('Mbp', '') * 1e6 : +splitScrollLocation[1].replace('bp', '');
            x1 = (splitScrollLocation[3].indexOf('Mbp') > -1) ? +splitScrollLocation[3].replace('Mbp', '') * 1e6 : +splitScrollLocation[3].replace('bp', '');
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
            let labelLength = 0;
            const defaultHeight = 34;
            const extraLineHeight = 12;
            const maxCharPerLine = 30;
            // Some labels on the cart which have a target, assay name, and biosample are too long for one line (some actually extend to three lines)
            // Here we do some approximate math to try to figure out how many lines the labels extend to assuming that ~30 characters fit on one line
            // Labels on the experiment pages are short enough to fit on one line (they contain less information) so we can bypass these calculations for those pages
            if (label === 'cart') {
                labelLength += file.target ? file.target.label.length + 2 : 0;
                labelLength += file.assay_term_name ? file.assay_term_name.length + 2 : 0;
                labelLength += file.biosample_ontology && file.biosample_ontology.term_name ? file.biosample_ontology.term_name.length : 0;
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
            } else if (file.file_format === 'bigWig') {
                const trackObj = {};
                trackObj.name = <TrackLabel label={label} file={file} />;
                trackObj.longname = <TrackLabel label={label} file={file} long />;
                trackObj.type = 'signal';
                trackObj.path = domain + file.href;
                trackObj.heightPx = labelLength > 0 ? (defaultHeight + (extraLineHeight * labelLength)) : defaultHeight;
                trackObj.expandedHeightPx = 140;
                return trackObj;
            } else if (file.file_format === 'vdna-dir') {
                const trackObj = {};
                trackObj.name = <ul className="gb-info"><li>{this.props.assembly.split(' ')[0]}</li></ul>;
                trackObj.type = 'sequence';
                trackObj.path = file.href;
                trackObj.heightPx = 40;
                trackObj.expandable = false;
                return trackObj;
            } else if (file.file_format === 'vgenes-dir') {
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
            // bigBed bedRNAElements, bigBed peptideMapping, bigBed bedExonScore, bed12, and bed9 have two tracks and need extra height
            // Convert to lower case in case of inconsistency in the capitalization of the file format in the data
            if (file.file_format_type &&
                (['bedrnaelements', 'peptidemapping', 'bedexonscore', 'bed12', 'bed9'].indexOf(file.file_format_type.toLowerCase()) > -1)) {
                trackObj.name = <TrackLabel file={file} label={label} long />;
                trackObj.heightPx = 90;
                trackObj.expandable = false;
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
        const visualizer = new this.GV.GenomeVisualizer({
            clampToTracks: true,
            reorderTracks: true,
            removableTracks: false,
            panels: [{
                location: { contig: this.state.contig, x0: this.state.x0, x1: this.state.x1 },
            }],
            tracks: this.state.trackList,
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

    handleChange(e) {
        this.setState({
            showAutoSuggest: true,
            searchTerm: e.target.value,
        });
    }

    handleAutocompleteClick(term, id, name) {
        const newTerms = {};
        const inputNode = this.gene;
        inputNode.value = term;
        newTerms[name] = id;
        this.setState({
            // terms: newTerms,
            showAutoSuggest: false,
            searchTerm: term,
        });
        inputNode.focus();
        // Now let the timer update the terms state when it gets around to it.
    }

    handleOnFocus() {
        this.setState({ showAutoSuggest: false });
        const coordinateHref = `/suggest/?genome=${this.state.genome}&q=${this.state.searchTerm}`;
        getCoordinateData(coordinateHref, this.context.fetch).then((response) => {
            // Find the response line that matches the search
            const responseIndex = response['@graph'].findIndex(responseLine => responseLine.text === this.state.searchTerm);

            // Find the annotation line that matches the genome selected in the fake facets
            const annotations = response['@graph'][responseIndex]._source.annotations;
            const annotationIndex = annotations.findIndex(annotation => annotation.assembly_name === this.state.genome);
            const annotation = annotations[annotationIndex];

            // Compute gene location information from the annotation
            const annotationLength = +annotation.end - +annotation.start;
            const contig = `chr${annotation.chromosome}`;
            const xStart = +annotation.start - (annotationLength / 2);
            const xEnd = +annotation.end + (annotationLength / 2);

            if (contig !== '') {
                this.state.visualizer.setLocation({
                    contig,
                    x0: xStart,
                    x1: xEnd,
                });
            }
        });
    }

    resetLocation() {
        this.state.visualizer.setLocation({ contig: this.state.contig, x0: this.state.x0, x1: this.state.x1 });
    }

    render() {
        return (
            <React.Fragment>
                {(this.state.trackList.length > 0 && this.state.genome !== null && !(this.state.disableBrowserForIE)) ?
                    <React.Fragment>
                        { (this.state.genome.indexOf('GRC') !== -1) ?
                            <div className="gene-search">
                                <i className="icon icon-search" />
                                <div className="search-instructions">Search for a gene</div>
                                <div className="searchform">
                                    <input id="gene" ref={(input) => { this.gene = input; }} aria-label={'search for gene name'} placeholder="Enter gene name here" value={this.state.searchTerm} onChange={this.handleChange} />
                                    {(this.state.showAutoSuggest && this.state.searchTerm) ?
                                        <FetchedData loadingComplete>
                                            <Param
                                                name="auto"
                                                url={`/suggest/?genome=${this.state.genome}&q=${this.state.searchTerm}`}
                                                type="json"
                                            />
                                            <AutocompleteBox
                                                name="annotation"
                                                userTerm={this.state.searchTerm}
                                                handleClick={this.handleAutocompleteClick}
                                            />
                                        </FetchedData>
                                    : null}
                                </div>
                                <button className="submit-gene-search btn btn-info" onClick={this.handleOnFocus}>Submit</button>
                            </div>
                        : null}
                        {this.props.displaySort ?
                            <div className="sort-control-container">
                                <div className="sort-label">Sort by: </div>
                                {this.props.sortParam.map((param, paramIdx) => <button className={`sort-button ${param === this.state.primarySort ? 'active' : ''}`} key={param.replace(/\s/g, '_')} onClick={() => this.sortAndRefresh(param, this.state.sortToggle[paramIdx], paramIdx, true)}><i className={this.state.sortToggle[paramIdx] ? 'tcell-desc' : 'tcell-asc'} /><div className="sort-label">{param}</div></button>)}
                            </div>
                        : null}
                        <div className="browser-container">
                            <button className="reset-browser-button" onClick={this.resetLocation}>
                                <i className="icon icon-undo" />
                                <span className="reset-title">Reset coordinates</span>
                            </button>
                            <div ref={(div) => { this.chartdisplay = div; }} className="valis-browser" />
                        </div>
                    </React.Fragment>
                :
                    <React.Fragment>
                        {(this.state.disableBrowserForIE) ?
                            <div className="browser-error valis-browser">The genome browser does not support Internet Explorer. Please upgrade your browser to Edge to visualize files on ENCODE.</div>
                        :
                            <div className="browser-error valis-browser">There are no visualizable results.</div>
                        }
                    </React.Fragment>
                }
            </React.Fragment>
        );
    }
}

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
