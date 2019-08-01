import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { FetchedData, Param } from './fetched';
import { BrowserFeat } from './browserfeat';
import AutocompleteBox from './region_search';

const domainName = 'https://www.encodeproject.org';

// Files to be displayed for local version of browser
const dummyFiles = [
    {
        file_format: 'bigWig',
        output_type: 'minus strand signal of all reads',
        accession: 'ENCFF425LKJ',
        href: '/files/ENCFF425LKJ/@@download/ENCFF425LKJ.bigWig',
    },
    {
        file_format: 'bigWig',
        output_type: 'plus strand signal of all reads',
        accession: 'ENCFF638QHN',
        href: '/files/ENCFF638QHN/@@download/ENCFF638QHN.bigWig',
    },
    {
        file_format: 'bigWig',
        output_type: 'plus strand signal of unique reads',
        accession: 'ENCFF541XFO',
        href: '/files/ENCFF541XFO/@@download/ENCFF541XFO.bigWig',
    },
    {
        file_format: 'bigBed bedRNAElements',
        output_type: 'transcription start sites',
        accession: 'ENCFF517WSY',
        href: '/files/ENCFF517WSY/@@download/ENCFF517WSY.bigBed',
    },
    {
        file_format: 'bigBed',
        output_type: 'peaks',
        accession: 'ENCFF026DAN',
        href: '/files/ENCFF026DAN/@@download/ENCFF026DAN.bigBed',
    },
    {
        file_format: 'bigBed',
        output_type: 'peaks',
        accession: 'ENCFF847CBY',
        href: '/files/ENCFF847CBY/@@download/ENCFF847CBY.bigBed',
    },
];

// Not all files can be visualized on the Valis genome browser
// Some of these files should be visualizable later, after updates to browser
export function filterForVisualizableFiles(fileList) {
    const newFileList = fileList.filter(file => (
        (file.file_format === 'bigWig' || file.file_format === 'bigBed')
        && (file.file_format_type !== 'bedMethyl')
        && (file.file_format_type !== 'bedLogR')
        && (file.file_format_type !== 'idr_peak')
        && (file.file_format_type !== 'tss_peak')
        && (file.file_format_type !== 'pepMap')
        && (file.file_format_type !== 'modPepMap')
        && ['released', 'in progress', 'archived'].indexOf(file.status) > -1
    ));
    return newFileList;
}

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
        };
        this.setBrowserDefaults = this.setBrowserDefaults.bind(this);
        this.filesToTracks = this.filesToTracks.bind(this);
        this.drawTracks = this.drawTracks.bind(this);
        this.drawTracksResized = this.drawTracksResized.bind(this);
        this.handleChange = this.handleChange.bind(this);
        this.handleAutocompleteClick = this.handleAutocompleteClick.bind(this);
        this.handleOnFocus = this.handleOnFocus.bind(this);
        this.compileFiles = this.compileFiles.bind(this);
        this.setGenomeAndTracks = this.setGenomeAndTracks.bind(this);
    }

    componentDidMount() {
        // Check if browser is IE 11 and disable browser if so
        if (BrowserFeat.getBrowserCaps('uaTrident')) {
            this.setState({ disableBrowserForIE: true });
        } else {
            // Determine pinned files based on genome, filter and sort files, compute and draw tracks
            this.setGenomeAndTracks();
        }
    }

    componentDidUpdate(prevProps, prevState) {
        if (!(this.state.disableBrowserForIE)) {
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
                let newFiles = [];
                let files = [];
                let domain = `${window.location.protocol}//${window.location.hostname}`;
                if (domain.includes('localhost')) {
                    domain = domainName;
                    newFiles = [...this.state.pinnedFiles, ...dummyFiles];
                } else {
                    const propsFiles = filterForVisualizableFiles(this.props.files);
                    files = _.chain(propsFiles)
                        .sortBy(obj => obj.output_type)
                        .sortBy((obj) => {
                            if (obj.biological_replicates.length > 1) {
                                return +obj.biological_replicates.join('');
                            }
                            return +obj.biological_replicates * 1000;
                        })
                        .value();
                    newFiles = [...this.state.pinnedFiles, ...files];
                }
                let tracks = [];
                if (files.length > 0) {
                    tracks = this.filesToTracks(newFiles, domain);
                }
                this.setState({ trackList: tracks }, () => {
                    if (this.chartdisplay && tracks !== []) {
                        this.drawTracks(this.chartdisplay);
                    }
                });
            }
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
                    file_format: 'vgenes-dir',
                    href: 'https://encoded-build.s3.amazonaws.com/browser/GRCh38/GRCh38.vgenes-dir',
                },
            ];
            contig = 'chr1';
            x0 = 11102837;
            x1 = 11267747;
        } else if (assembly === 'hg19' || assembly === 'GRCh37') {
            pinnedFiles = [
                {
                    file_format: 'vgenes-dir',
                    href: 'https://encoded-build.s3.amazonaws.com/browser/hg19/hg19.vgenes-dir',
                },
            ];
            contig = 'chr21';
            x0 = 33031597;
            x1 = 33041570;
        } else if (assembly === 'mm10' || assembly === 'mm10-minimal' || assembly === 'GRCm38') {
            pinnedFiles = [
                {
                    file_format: 'vgenes-dir',
                    href: 'https://encoded-build.s3.amazonaws.com/browser/mm10/mm10.vgenes-dir',
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
            const domain = `${window.location.protocol}//${window.location.hostname}`;
            const files = this.compileFiles(domain);
            if (files.length > 1) {
                const tracks = this.filesToTracks(files, domain);
                this.setState({ trackList: tracks }, () => {
                    this.drawTracks(this.chartdisplay);
                });
            } else {
                this.setState({ trackList: [] });
            }
        });
    }

    compileFiles(domain) {
        let newFiles = [];
        if (domain.includes('localhost')) {
            // Locally we will display some default tracks
            newFiles = [...this.state.pinnedFiles, ...dummyFiles];
        } else {
            // Filter files to include only bigWig and bigBed formats, and not 'bigBed bedMethyl' formats and only released or in progress files
            const propsFiles = filterForVisualizableFiles(this.props.files);
            // Set default ordering of tracks to be first by replicate then by output_type
            // Ordering by replicate is like this: 'Rep 1,2' -> 'Rep 1,3,...' -> 'Rep 2,3,...' -> 'Rep 1' -> 'Rep 2' -> 'Rep N'
            // Multiplication by 1000 orders the replicates with a single replicate at the end
            const files = _.chain(propsFiles)
                .sortBy(obj => obj.output_type)
                .sortBy((obj) => {
                    if (obj.biological_replicates.length > 1) {
                        return +obj.biological_replicates.join('');
                    }
                    return +obj.biological_replicates * 1000;
                })
                .value();
            newFiles = [...this.state.pinnedFiles, ...files];
        }
        return newFiles;
    }

    filesToTracks(files, domain) {
        const tracks = files.map((file) => {
            if (file.name) {
                const trackObj = {};
                trackObj.name = file.name;
                trackObj.type = 'signal';
                trackObj.path = file.href;
                trackObj.heightPx = 80;
                return trackObj;
            } else if (file.file_format === 'bigWig') {
                const trackObj = {};
                trackObj.name = `${file.accession} ${file.output_type} ${file.biological_replicates ? `rep ${file.biological_replicates.join(',')}` : ''}`;
                trackObj.type = 'signal';
                trackObj.path = domain + file.href;
                trackObj.heightPx = 80;
                return trackObj;
            } else if (file.file_format === 'vdna-dir') {
                const trackObj = {};
                trackObj.name = 'Genome';
                trackObj.type = 'sequence';
                trackObj.path = file.href;
                trackObj.heightPx = 40;
                return trackObj;
            } else if (file.file_format === 'vgenes-dir') {
                const trackObj = {};
                trackObj.name = this.props.assembly;
                trackObj.type = 'annotation';
                trackObj.path = file.href;
                trackObj.heightPx = 120;
                return trackObj;
            }
            const trackObj = {};
            trackObj.name = `${file.accession} ${file.output_type} ${file.biological_replicates ? `rep ${file.biological_replicates.join(',')}` : ''}`;
            trackObj.type = 'annotation';
            trackObj.path = domain + file.href;
            // bigBed bedRNAElements, bigBed peptideMapping, bigBed bedExonScore, bed12, and bed9 have two tracks and need extra height
            // Convert to lower case in case of inconsistency in the capitalization of the file format in the data
            if (file.file_format_type &&
                (['bedrnaelements', 'peptidemapping', 'bedexonscore', 'bed12', 'bed9'].indexOf(file.file_format_type.toLowerCase() > -1))) {
                trackObj.heightPx = 120;
            } else {
                trackObj.heightPx = 80;
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
        // eslint-disable-next-line no-undef
        const visualizer = new GenomeVisualizer({
            clampToTracks: true,
            removableTracks: false,
            panels: [{
                location: { contig: this.state.contig, x0: this.state.x0, x1: this.state.x1 },
            }],
            tracks: this.state.trackList,
        });
        this.setState({ visualizer });
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
        console.log(this.props.assembly);
        console.log(`${this.context.location_href.split('/experiments/')[0]}/suggest/?genome=${this.state.genome}&q=${this.state.searchTerm}`);

        getCoordinateData(`${this.context.location_href.split('/experiments/')[0]}/suggest/?genome=${this.state.genome}&q=${this.state.searchTerm}`, this.context.fetch).then((response) => {
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
            console.log(annotation);
            const printStatement = `Success: found gene location for ${this.state.searchTerm}`;
            console.log(printStatement);

            if (contig !== '') {
                this.state.visualizer.setLocation({
                    contig,
                    x0: xStart,
                    x1: xEnd,
                });
            }
        });
    }

    render() {
        return (
            <React.Fragment>
                {(this.state.trackList.length > 1 && this.state.genome !== null && !(this.state.disableBrowserForIE)) ?
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
                        <div ref={(div) => { this.chartdisplay = div; }} className="valis-browser" />
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
};

GenomeBrowser.defaultProps = {
    assembly: '',
};

GenomeBrowser.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};

export default GenomeBrowser;
