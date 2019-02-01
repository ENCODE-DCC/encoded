import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import { BrowserSelector } from './objectutils';
import { Panel, PanelBody } from '../libs/bootstrap/panel';
import { FacetList, FilterList, Listing, ResultBrowser } from './search';
import { FetchedData, Param } from './fetched';
import * as globals from './globals';
import _ from 'underscore';
import { SortTablePanel, SortTable } from './sorttable';


const regulomeGenomes = [
    { value: 'GRCh37', display: 'hg19' },
    { value: 'GRCh38', display: 'GRCh38' },
];

class DataTypes extends React.Component {

    constructor() {
        super();

        // Bind this to non-React methods.
        this.handleInfo = this.handleInfo.bind(this);
    }

    handleInfo(e) {
        let infoId = e.target.id.split("data-type-")[1];
        if (infoId){
            let infoElement = document.getElementById("data-explanation-"+infoId);
            infoElement.classList.toggle("show");
            let iconElement = e.target.getElementsByTagName("i")[0];
            if (e.target.getElementsByTagName("i")[0].className.indexOf("icon-caret-right") > -1){
                iconElement.classList.add("icon-caret-down");
                iconElement.classList.remove("icon-caret-right");
            } else {
                iconElement.classList.remove("icon-caret-down");
                iconElement.classList.add("icon-caret-right");
            }
        }
    }

    render () {
        return(
            <div className="data-types">
                <div className="data-types-instructions"><h4>Use RegulomeDB to identify DNA features and regulatory elements in non-coding regions of the human genome by entering ...</h4></div>
                <div className="data-types-block" onClick={this.handleInfo}>
                    <h4 id="data-type-0" className="data-type"><i className="icon icon-caret-right" /> dbSNP IDs</h4>
                    <p className="data-type-explanation" id="data-explanation-0">Enter dbSNP ID(s) (example) or upload a list of dbSNP IDs to identify DNA features and regulatory elements that contain the coordinate of the SNP(s).</p>
                    <h4 id="data-type-1" className="data-type"><i className="icon icon-caret-right" /> Single nucleotides</h4>
                    <p className="data-type-explanation" id="data-explanation-1">Enter hg19 coordinates for a single nucleotide as 0-based (example) coordinates or in a BED file (example), VCF file (example), or GFF3 file (example). These coordinates will be mapped to a dbSNP IDs (if available) in addition to identifying DNA features and regulatory elements that contain the input coordinate(s).</p>
                    <h4 id="data-type-2" className="data-type"><i className="icon icon-caret-right" /> A chromosomal region</h4>
                    <p className="data-type-explanation" id="data-explanation-2">Enter hg19 chromosomal regions, such as a promoter region upstream of a gene, as 0-based (example) coordinates or in a BED file (example) or GFF3 file (example). All dbSNP IDs with an allele frequency >1% that are found in this region will be used to identify DNA features and regulatory elements that contain the coordinate of the SNP(s).</p>
                </div>
            </div>
        )
    }
}

DataTypes.propTypes = {
    handleInfo: PropTypes.func,
};


class AdvSearch extends React.Component {
    constructor() {
        super();

        // Set intial React state.
        /* eslint-disable react/no-unused-state */
        // Need to disable this rule because of a bug in eslint-plugin-react.
        // https://github.com/yannickcr/eslint-plugin-react/issues/1484#issuecomment-366590614
        this.state = {
            coordinates: '',
            genome: 'GRCh37',
        };
        /* eslint-enable react/no-unused-state */

        // Bind this to non-React methods.
        this.handleChange = this.handleChange.bind(this);
        this.handleOnFocus = this.handleOnFocus.bind(this);
        this.handleExamples = this.handleExamples.bind(this);
    }

    handleChange(e) {
        this.newSearchTerm = e.target.value;
    }

    handleOnFocus() {
        this.context.navigate(this.context.location_href);
    }

    handleExamples(e){

        let replaceNewline = (input) => {

            let replaceAll = (str, find, replace) => {
                return str.replace(new RegExp(find, 'g'), replace);
            }

            var newline = String.fromCharCode(13, 10);
            return replaceAll(input, "\\n", newline);
        }

        let exampleString = "";
        if (e.target.id === "example-snps") {
            exampleString = "rs3768324\nrs75982468\nrs10905307\nrs10823321\nrs7745856";
        } else if (e.target.id === "example-coordinates") {
            exampleString = "chr11:62607065-62607067\nchr10:5894500-5894501\nchr10:11741181-11741181\nchr1:39492463-39492463\nchr6:10695158-10695160";
        } else {
            exampleString = "rs3768324\nrs75982468\nrs10905307\nrs10823321\nrs7745856";
        }
        document.getElementById("multiple-entry-input").value = replaceNewline(exampleString);
    }

    render() {
        const context = this.props.context;
        const id = url.parse(this.context.location_href, true);
        const region = id.query.region || '';
        const searchBase = url.parse(this.context.location_href).search || '';

        return (
            <Panel>
                <PanelBody>
                    <form id="panel1" className="adv-search-form" autoComplete="off" aria-labelledby="tab1" onSubmit={this.handleOnFocus} >
                        <div className="form-group">
                            <label htmlFor="annotation"><i className="icon icon-search"></i>Search by dbSNP ID or coordinate range (hg19)</label>
                            <div className="input-group input-group-region-input">
                                <textarea className="multiple-entry-input" id="multiple-entry-input" placeholder="Enter search parameters here." onChange={this.handleChange} name="region">
                                </textarea>

                                <p className="example-inputs" onClick={this.handleExamples}>Click for example entry: <span className="example-input" id="example-snps">multiple dbSNPs</span> or <span className="example-input" id="example-coordinates">coordinates ranges</span></p>

                                <input type="submit" value="Search" className="btn btn-sm btn-info" />
                                <input type="hidden" name="genome" value={this.state.genome} />
                            </div>
                        </div>

                    </form>

                    {(context.notification) ?
                        <div className="notification">{context.notification}</div>
                    : null}
                    {(context.coordinates) ?
                        <p>Searched coordinates: {context.coordinates}</p>
                    : null}
                    {(context.regulome_score) ?
                        <p className="regulomescore">RegulomeDB score: {context.regulome_score}</p>
                    : null}
                    {(context.regulome_score  && !context.peak_details) ?
                        <a
                            rel="nofollow"
                            className="btn btn-info btn-sm"
                            href={searchBase ? `${searchBase}&peak_metadata` : '?peak_metadata'}
                        >
                            See peaks
                        </a>
                    : null}
                    {(context.peak_details !== undefined && context.peak_details !== null) ?
                        <div className="btn-container">
                            <a className="btn btn-info btn-sm" href={context.download_elements[0]} data-bypass>Download peak details (TSV)</a>
                            <a className="btn btn-info btn-sm" href={context.download_elements[1]} data-bypass>Download peak details (JSON)</a>
                        </div>
                    : null}
                </PanelBody>
            </Panel>
        );
    }
}

AdvSearch.propTypes = {
    context: PropTypes.object.isRequired,
};

AdvSearch.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
};

const PeakDetails = (props) => {

    const context = props.context;
    const peaks = context.peak_details;

    const peaksTableColumns = {
        method: {
            title: 'Method',
        },

        chrom: {
            title: 'Chromosome location',
            getValue: item => item.chrom+":"+item.start+".."+item.end,
        },

        biosample_term_name: {
            title: 'Biosample',
        },

        targets: {
            title: 'Targets',
            getValue: item => item.targets.join(', '),
        },
    };

    return (
        <div>
            <SortTablePanel title="Peak details">
                <SortTable list={peaks} columns={peaksTableColumns} />
            </SortTablePanel>
        </div>
    );

}

const ResultsTable = (props) => {

    const context = props.context;
    const data = context["@graph"];
    
    console.log("building table of length:");
    console.log(data.length);

    const dataColumns = {

        assay_title: {
            title: 'Method',
            getValue: item => item.assay_title ? item.assay_title : item.annotation_type,
        },

        biosample_term_name: {
            title: 'Biosample',
        },

        target: {
            title: 'Targets',
            getValue: (item) => (item.target) ? item.target.label : (item.targets) ? item.targets.map(t => t.label).join(', ') : '',
        },

        organ_slims: {
            title: 'Organ',
            getValue: (item) => item.organ_slims ? item.organ_slims.join(', ') : '',
        },

        accession: {
            title: "Link",
            display: (item) => {
                return <a href={item['@id']}>{item.accession}</a>;
            }
        },

        description: {
            title: 'Description',
        },
    };

    return (
        <div>
            <SortTablePanel title="Results">
                <SortTable list={data} columns={dataColumns} />
            </SortTablePanel>
        </div>
    );

}

class RegulomeSearch extends React.Component {
    constructor() {
        super();

        let assemblies = 'hg19';
        this.assembly == 'hg19';

        // Bind this to non-React methods.
        this.onFilter = this.onFilter.bind(this);
    }

    onFilter(e) {
        if (this.props.onChange) {
            const search = e.currentTarget.getAttribute('href');
            this.props.onChange(search);
            e.stopPropagation();
            e.preventDefault();
        }
    }
    
    // shouldComponentUpdate(nextProps) {
    //     console.log("should the component update?");
    //     let currentResultsLength = this.props.context['@graph'].length;
    //     let nextResultsLength = nextProps.context['@graph'].length;
    //     if (currentResultsLength > 0){
    //         console.log(currentResultsLength===nextResultsLength);
    //         return currentResultsLength===nextResultsLength;
    //     } else {
    //         console.log(true);
    //         return true;
    //     }
    // }
    
    shouldComponentUpdate(nextProps) {
        console.log("should the component update?");
        console.log(!_.isEqual(this.props, nextProps));
        return !_.isEqual(this.props, nextProps);
    }

    render() {
        const visualizeLimit = 100;
        const context = this.props.context;
        const results = context['@graph'];
        const columns = context.columns;
        const notification = context.notification;
        const searchBase = url.parse(this.context.location_href).search || '';
        const trimmedSearchBase = searchBase.replace(/[?|&]limit=all/, '');
        const filters = context.filters;
        const facets = context.facets;
        const total = context.total;
        const visualizeDisabled = total > visualizeLimit;
        
        console.log("rendering with length:");
        console.log(results.length);

        let browseAllFiles = true; // True to pass all files to browser
        let browserAssembly = ''; // Assembly to pass to ResultsBrowser component
        let browserDatasets = []; // Datasets will be used to get vis_json blobs
        let browserFiles = []; // Files to pass to ResultsBrowser component
        let assemblyChooser;
        let visualizeCfg = context.visualize_batch;

        // Get a sorted list of batch hubs keys with case-insensitive sort
        let visualizeKeys = [];
        if (context.visualize_batch && Object.keys(context.visualize_batch).length) {
            console.log("getting sorted list of batch hubs keys");
            visualizeKeys = Object.keys(context.visualize_batch).sort((a, b) => {
                const aLower = a.toLowerCase();
                const bLower = b.toLowerCase();
                return (aLower > bLower) ? 1 : ((aLower < bLower) ? -1 : 0);
            });
        }
        
        // // Check whether the search query qualifies for a genome browser display. Start by counting
        // // the number of "type" filters exist.
        // let typeFilter;
        // const counter = filters.reduce((prev, curr) => {
        //     if (curr.field === 'type') {
        //         typeFilter = curr;
        //         return prev + 1;
        //     }
        //     return prev;
        // }, 0);
        // 
        // // If we have only one "type" term in the query string and it's for File, then we can
        // // display the List/Browser tabs. Otherwise we just get the list.
        // let browserAvail = counter === 1 && typeFilter && typeFilter.term === 'File' && assemblies.length === 1;
        // console.log("is browser available?");
        // console.log(browserAvail);
        // if (browserAvail) {
        //     // If dataset is in the query string, we can show all files.
        //     const datasetFilter = filters.find(filter => filter.field === 'dataset');
        //     if (datasetFilter) {
        //         browseAllFiles = true;
        // 
        //         // Probably not worth a define in globals.js for visualizable types and statuses.
        //         browserFiles = results.filter(file => ['bigBed', 'bigWig'].indexOf(file.file_format) > -1);
        //         if (browserFiles.length > 0) {
        //             browserFiles = browserFiles.filter(file =>
        //                 ['released', 'in progress', 'archived'].indexOf(file.status) > -1
        //             );
        //         }
        //         browserAvail = (browserFiles.length > 0);
        // 
        //         if (browserAvail) {
        //             // Distill down to a list of datasets so they can be passed to genome_browser code.
        //             browserDatasets = browserFiles.reduce((datasets, file) => (
        //                 (!file.dataset || datasets.indexOf(file.dataset) > -1) ? datasets : datasets.concat(file.dataset)
        //             ), []);
        //         }
        //     } else {
        //         browseAllFiles = false;
        //         browserAvail = false; // NEW: Limit browser option to type=File&dataset=... only!
        //     }
        // }

        // if (browserAvail) {
        //     // Now determine if we have a mix of assemblies in the files, or just one. If we have
        //     // a mix, we need to render a drop-down.
        //     if (assemblies.length === 1) {
        //         // Only one assembly in all the files. No menu needed.
        //         browserAssembly = assemblies[0];
        //         // empty div to avoid warning only.
        //         assemblyChooser = (
        //             <div className="browser-assembly-chooser" />
        //         );
        //     } else {
        //         browserAssembly = this.state.browserAssembly;
        //         assemblyChooser = (
        //             <div className="browser-assembly-chooser">
        //                 <div className="browser-assembly-chooser__title">Assembly:</div>
        //                 <div className="browser-assembly-chooser__menu">
        //                     <AssemblyChooser assemblies={assemblies} assemblyChange={this.assemblyChange} />
        //                 </div>
        //             </div>
        //         );
        //     }
        // }

        return (
            <div>

                {(context.total > 0) ?
                    <div>
                        <div className="lead-logo"><a href="/"><img src="/static/img/RegulomeLogoFinal.gif"></img></a></div>
                        <div>
                            <div className="result-summary">
                                {(context.regulome_score) ?
                                    <p className="regulomescore">Score: <span className="bold-class">{context.regulome_score}</span></p>
                                : null}
                            </div>
                            <div className="search-information">
                                {(context.coordinates) ?
                                    <p>Searched coordinates: {context.coordinates}</p>
                                : null}
                                {(context.notification) ?
                                    <p>{context.notification}</p>
                                : null}
                            </div>
                            <div className="button-collection">
                                {visualizeKeys && context.visualize_batch && !visualizeDisabled ?
                                    <div className="visualize-block">
                                        {visualizeCfg['hg19']['UCSC'] ?
                                            <div>
                                                <div className="visualize-element"><a href={visualizeCfg['hg19']['Quick View']} rel="noopener noreferrer" target="_blank">
                                                    <i className="icon icon-external-link"></i>
                                                    Visualize: Quick View
                                                </a></div>
                                                <div className="visualize-element"><a href={visualizeCfg['hg19']['UCSC']} rel="noopener noreferrer" target="_blank">
                                                    <i className="icon icon-external-link"></i>
                                                    UCSC browser
                                                </a></div>
                                            </div>
                                        :
                                            <div className="visualize-element visualize-error">To visualize, choose other datasets.</div>
                                        }
                                    </div>
                                :
                                    <div className="visualize-block">
                                        <div className="visualize-element visualize-error">Filter to fewer than 100 results to visualize</div>
                                    </div>
                                }
                                {(context.regulome_score  && !context.peak_details) ?
                                    <a
                                        rel="nofollow"
                                        className="peaks-link"
                                        href={searchBase ? `${searchBase}&peak_metadata` : '?peak_metadata'}
                                    >
                                        <i className="icon icon-external-link"></i>
                                        View peak details
                                    </a>
                                : null}
                            </div>
                            <div>
                                <div className="panel flex-panel">

                                    {facets.length ?
                                        <div className="facet-column">
                                            <div className="facet-controls">
                                                <div className="results-count">Showing {results.length} of {total}</div>
                                            </div>
                                            <FilterList {...this.props} />
                                            <FacetList
                                                {...this.props}
                                                facets={facets}
                                                filters={filters}
                                                searchBase={searchBase ? `${searchBase}&` : `${searchBase}?`}
                                                onFilter={this.onFilter}
                                                modifyFacetsFlag={1}
                                            />
                                        </div>
                                    : ''}

                                    <div className="wide-column">

                                        <ResultsTable {...this.props} />

                                    </div>

                                </div>

                            </div>
                        </div>
                    </div>
                : null}

                {(context.peak_details) ?
                    <div>
                        <div className="lead-logo"><a href="/"><img src="/static/img/RegulomeLogoFinal.gif"></img></a></div>
                        <PeakDetails {...this.props} />
                    </div>
                : null}

                {(context.peak_details === undefined && !notification.startsWith('Success')) ? 
                    <div>
                        <div className="lead-logo"><a href="/"><img src="/static/img/RegulomeLogoFinal.gif"></img></a></div>
                        <AdvSearch {...this.props} />
                        <DataTypes />
                    </div>
                :  null}

            </div>
        );
    }
}

RegulomeSearch.propTypes = {
    context: PropTypes.object.isRequired,
    onChange: PropTypes.func,
    region: PropTypes.string,
};

RegulomeSearch.defaultProps = {
    onChange: null,
    region: null,
};

RegulomeSearch.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
};

globals.contentViews.register(RegulomeSearch, 'region-search');
