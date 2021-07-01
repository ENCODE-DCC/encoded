/**
 * Functions and components for both dataset visualizations and batch visualizations.
 */
import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import * as encoding from '../libs/query_encoding';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/ui/modal';
import * as globals from './globals';


/**
 * Dataset visualization section.
 **************************************************************************************************
 */

/**
 * Maximum number of hic files allowed to be selected at once.
 */
const MAX_HIC_FILES_SELECTED = 8;


/**
 * If you modify ASSEMBLY_DETAILS in vis_defines.py, this object might need corresponding
 * modifications.
 */
export const ASSEMBLY_DETAILS = {
    GRCh38: {
        species: 'Homo sapiens',
        ucsc_assembly: 'hg38',
        ensembl_host: 'www.ensembl.org',
    },
    'GRCh38-minimal': {
        species: 'Homo sapiens',
        ucsc_assembly: 'hg38',
        ensembl_host: 'www.ensembl.org',
    },
    hg19: {
        species: 'Homo sapiens',
        ucsc_assembly: 'hg19',
        ensembl_host: 'grch37.ensembl.org',
    },
    GRCm39: {
        species: 'Mus musculus',
        ucsc_assembly: 'mm39',
        ensembl_host: 'www.ensembl.org',
    },
    mm10: {
        species: 'Mus musculus',
        ucsc_assembly: 'mm10',
        ensembl_host: 'www.ensembl.org',
    },
    'mm10-minimal': {
        species: 'Mus musculus',
        ucsc_assembly: 'mm10',
        ensembl_host: 'www.ensembl.org',
    },
    mm9: {
        species: 'Mus musculus',
        ucsc_assembly: 'mm9',
    },
    dm6: {
        species: 'Drosophila melanogaster',
        ucsc_assembly: 'dm6',
    },
    dm3: {
        species: 'Drosophila melanogaster',
        ucsc_assembly: 'dm3',
    },
    ce11: {
        species: 'Caenorhabditis elegans',
        ucsc_assembly: 'ce11',
    },
    ce10: {
        species: 'Caenorhabditis elegans',
        ucsc_assembly: 'ce10',
    },
    ce6: {
        species: 'Caenorhabditis elegans',
        ucsc_assembly: 'ce6',
    },
};

/**
 * File types allowed for each browser.
 */
const browserFileTypes = {
    UCSC: [],
    Ensembl: ['bigWig', 'bigBed'],
    hic: ['hic'],
};


/**
 * Open a browser visualization in a new tab. If called from a React component, that component must
 * be mounted.
 * @param {object} dataset Dataset object whose files we're visualizing
 * @param {string} browser Specifies browser to use: UCSC, Ensembl, hic currently
 *                         acceptable
 * @param {string} assembly Assembly to use with visualizer
 * @param {array} files Array of files to visualize if applicable
 * @param {string} datasetUrl URL of `dataset` parameter
 */
export const visOpenBrowser = (dataset, browser, assembly, files, datasetUrl) => {
    let href;
    switch (browser) {
    case 'UCSC': {
        // UCSC does not use `files` under any circumstances.
        const ucscAssembly = ASSEMBLY_DETAILS[assembly].ucsc_assembly;
        href = `http://genome.ucsc.edu/cgi-bin/hgTracks?hubClear=${datasetUrl}@@hub/hub.txt&db=${ucscAssembly}`;
        break;
    }
    case 'hic': {
        const parsedUrl = url.parse(datasetUrl);
        delete parsedUrl.path;
        delete parsedUrl.search;
        delete parsedUrl.query;
        const fileQueries = files.map((file) => {
            parsedUrl.pathname = file.href;
            const name = file.biological_replicates && file.biological_replicates.length > 0 ? `&name=${dataset.accession} / ${file.title}, Replicate ${file.biological_replicates.join(',')}` : '';
            return encoding.encodedURIComponentOLD(`{hicUrl=${url.format(parsedUrl)}${name}}`, { encodeEquals: true });
        });
        href = `http://aidenlab.org/juicebox/?juicebox=${fileQueries.join(',')}`;
        break;
    }
    case 'Ensembl': {
        if (ASSEMBLY_DETAILS[assembly].ensembl_host) {
            href = `http://${ASSEMBLY_DETAILS[assembly].ensembl_host}/Trackhub?url=${datasetUrl}@@hub/hub.txt;species=${ASSEMBLY_DETAILS[assembly].species.replace(/ /g, '_')}`;
        }
        break;
    }
    default:
        break;
    }
    if (href) {
        window.open(href, '_blank');
    }
};


/**
 * Filter files down to the ones that should be selected by default for the given browser.
 * @param {array} files Files to filter according to what a browser uses
 * @param {string} browser Browser to filter files against; see `browserFileTypes`
 * @param {boolean} limits True to place browser-specific limits on resulting files, if any
 * @return {array} `files` that can be browsed with `browser`.
 */
export const visFilterBrowserFiles = (files, browser, limits = false) => {
    // Filter the given files to ones qualified for the given browser, and only those files with
    // "released" status.
    const qualifiedFileTypes = browserFileTypes[browser];
    let qualifiedFiles = files.filter((file) => qualifiedFileTypes.indexOf(file.file_format) !== -1 && file.status === 'released');

    // For the hic browser, sort to prioritize "mapping quality thresholded chromatin interactions"
    // output_types.
    if (browser === 'hic') {
        qualifiedFiles = qualifiedFiles.sort((file) => (file.output_type === 'mapping quality thresholded chromatin interactions' ? -1 : 0));
        if (limits) {
            qualifiedFiles = qualifiedFiles.slice(0, MAX_HIC_FILES_SELECTED);
        }
    }
    return qualifiedFiles;
};


/**
 * Determine whether a file is selectable for the currently selected genome browser.
 * @param {object} file File to check against its browser selectable state
 * @param {array} selectedFiles Files that are currently selected
 * @param {string} browser Currently selected browser
 */
export const visFileSelectable = (file, selectedFiles, browser) => {
    let selectable = false;
    switch (browser) {
    case 'UCSC':
        // Always not selectable.
        break;
    case 'hic':
        selectable = (browserFileTypes[browser].indexOf(file.file_format) !== -1) && (selectedFiles.length < MAX_HIC_FILES_SELECTED);
        break;
    case 'Ensembl':
        // Always not selectable.
        break;
    default:
        // Should never happen, but not selectable if it does.
        break;
    }
    return selectable;
};


/**
 * The order that browsers should appear when sorted.
 */
const browserOrder = [
    'UCSC',
    'hic',
    'Ensembl',
];


/**
 * Given an array of browsers, sort them according to the order in the `browserOrder` global above.
 * @param {array} browsers Array of browsers to sort
 * @return {array} Same contents as `browsers` but sorted according to `browserOrder`
 */
export const visSortBrowsers = (browsers) => (
    _.sortBy(browsers, (browser) => browserOrder.indexOf(browser))
);


/**
 * Map of browser to display name.
 */
const browserNameMap = {
    UCSC: 'UCSC',
    hic: 'Juicebox',
    Ensembl: 'Ensembl',
};


/**
 * Map a browser to its display name.
 * @param {string} browser Browser whose display name is desired
 */
export const visMapBrowserName = (browser) => browserNameMap[browser];


/**
 * Batch visualization section.
 **************************************************************************************************
 */

/**
 * Generate a batch hub URL from the search results. This URL gets inserted into visualization
 * URLs.
 * @param {object} results Search results
 * @param {string} hostName Domain name of host
 *
 * @return {string} hub URL used in visualization URLs
 */
const generateBatchHubUrl = (resultsId, hostName) => {
    const parsedUrl = url.parse(resultsId).search;
    if (parsedUrl) {
        return `${hostName}/batch_hub/${encodeURIComponent(parsedUrl.substr(1).replace('&', ',,'))}/hub.txt`;
    }
    return null;
};


/**
 * Generate a list of relevant assemblies from the given search results. This includes any
 * assemblies included in the search results, filtered by any specified in the query string that
 * generated these search results, or all included assemblies if no assemblies were given in the
 * query string.
 * @param {object} results Search results
 *
 * @return {array} Assemblies in search results, filtered by query string assemblies if any
 */
const getRelevantAssemblies = (results) => {
    let relevantAssemblies = [];
    const assemblyFacet = results.facets.find((facet) => facet.field === 'assembly');
    if (assemblyFacet) {
        // Get array of assemblies specified in the search query; empty array if none.
        const specifiedAssemblies = results.filters.filter((filter) => filter.field === 'assembly').map((filter) => filter.term);
        relevantAssemblies = assemblyFacet.terms.filter((term) => term.doc_count > 0 && (specifiedAssemblies.length === 0 || specifiedAssemblies.includes(term.key)));
    }
    return relevantAssemblies.map((assembly) => assembly.key).sort((a, b) => globals.assemblyPriority.indexOf(a) - globals.assemblyPriority.indexOf(b));
};


/**
 * Currently this maps an assembly as stored in encode to an assembly that UCSC uses in the URL.
 * Each mapping results in an object to allow for future expansion.
 */
const ucscAssemblyDetails = {
    GRCh38: { mappedAssembly: 'hg38' },
    'GRCh38-minimal': { mappedAssembly: 'hg38' },
    hg19: { mappedAssembly: 'hg19' },
    GRCm39: { mappedAssembly: 'mm39' },
    mm10: { mappedAssembly: 'mm10' },
    'mm10-minimal': { mappedAssembly: 'mm10' },
    mm9: { mappedAssembly: 'mm9' },
    dm6: { mappedAssembly: 'dm6' },
    dm3: { mappedAssembly: 'dm3' },
    ce11: { mappedAssembly: 'ce11' },
    ce10: { mappedAssembly: 'ce10' },
    ce6: { mappedAssembly: 'ce6' },
};


/**
 * Generate a batch hub URL for UCSC based on the given assembly.
 * @param {string} assembly Assembly to use for the generated URL
 * @param {string} batchHubUrl Batch hub URL
 * @param {string} position Optional region search position string
 */
const ucscUrlGenerator = (assembly, batchHubUrl, position) => {
    const details = ucscAssemblyDetails[assembly];
    if (details) {
        return {
            visualizer: 'UCSC',
            url: `http://genome.ucsc.edu/cgi-bin/hgTracks?hubClear=${batchHubUrl}&db=${details.mappedAssembly}${position ? `&position=${position}` : ''}`,
        };
    }
    return null;
};


/**
 * Currently this maps an assembly as stored in encode to a species that ENSEMBL uses in the URL.
 * Each mapping results in an object to allow for future expansion.
 */
const ensembleAssemblyDetails = {
    GRCh38: { species: 'Homo_sapiens' },
    'GRCh38-minimal': { species: 'Homo_sapiens' },
    GRCm39: { species: 'Mus_musculus' },
    mm10: { species: 'Mus_musculus' },
    'mm10-minimal': { species: 'Mus_musculus' },
};


/**
 * Generate a batch hub URL for ENSEMBL based on the given assembly.
 * @param {string} assembly Assembly to use for the generated URL
 * @param {string} batchHubUrl Batch hub URL
 */
const ensemblUrlGenerator = (assembly, batchHubUrl) => {
    const details = ensembleAssemblyDetails[assembly];
    if (details) {
        return {
            visualizer: 'Ensembl',
            url: `http://www.ensembl.org/Trackhub?url=${batchHubUrl};species=${details.species}`,
        };
    }
    return null;
};


/**
 * Used for the loop through each external visualization we support. Add new generator functions to
 * this array to support new visualizers.
 */
const urlGenerators = [ucscUrlGenerator, ensemblUrlGenerator];


/**
 * Display a Visualize button that brings up a modal that lets you choose an assembly and a browser
 * in which to display the visualization.
 */
export class BrowserSelector extends React.Component {
    constructor() {
        super();

        // Set initial React state.
        this.state = { selectorOpen: false };
        this.openModal = this.openModal.bind(this);
        this.closeModal = this.closeModal.bind(this);
        this.handleClick = this.handleClick.bind(this);
    }

    // When the link to open a browser gets clicked, this gets called to close the modal in
    // addition to going to the link.
    handleClick() {
        this.closeModal();
    }

    // Called to open the browser-selection modal.
    openModal() {
        this.setState({ selectorOpen: true });
    }

    // Called to close the browser-selection modal.
    closeModal() {
        this.setState({ selectorOpen: false });
    }

    render() {
        const { results, disabledTitle, additionalFilters } = this.props;

        // Only consider Visualize button if exactly one type= of Experiment or Annotation exists
        // in query string.
        const docTypes = results.filters.filter((filter) => filter.field === 'type').map((filter) => filter.term);
        if (docTypes.length > 1 || (docTypes.length === 1 && docTypes[0] !== 'Experiment' && docTypes[0] !== 'Annotation')) {
            return null;
        }

        // Generate the batch hub URL used in batch visualization query strings.
        const parsedLocationHref = url.parse(this.context.location_href);
        const hostName = `${parsedLocationHref.protocol}//${parsedLocationHref.host}`;

        // Generate the query string, including elements from any given filters outside of search result filters.
        const resultsId = results['@id'].concat(additionalFilters.reduce((accQuery, filter) => `${accQuery}&${filter.field}=${encoding.encodedURIComponent(filter.term)}`, ''));
        const batchHubUrl = generateBatchHubUrl(resultsId, hostName);
        if (!batchHubUrl) {
            return null;
        }

        // If coordinates are given, construct a "position" query string parameter expanded by 200
        // bp in either direction.
        let position = '';
        if (results.coordinates) {
            const matches = results.coordinates.match(/(.+):(\d+)-(\d+)/);
            if (matches) {
                const lowCoordinate = Number(matches[2]);
                const highCoordinate = Number(matches[3]);
                position = `${matches[1]}:${lowCoordinate - 200}-${highCoordinate + 200}`;
            }
        }

        const relevantAssemblies = getRelevantAssemblies(results);
        const visualizeCfg = {};
        relevantAssemblies.forEach((assembly) => {
            visualizeCfg[assembly] = {};
            urlGenerators.forEach((urlGenerator) => {
                const visualizationMechanism = urlGenerator(assembly, batchHubUrl, position);
                if (visualizationMechanism) {
                    visualizeCfg[assembly][visualizationMechanism.visualizer] = visualizationMechanism.url;
                }
            });
        });

        if (relevantAssemblies.length > 0) {
            return (
                <>
                    <button type="button" onClick={this.openModal} className="btn btn-info btn-sm" data-test="visualize" id="visualize-control">
                        Visualize
                    </button>
                    {this.state.selectorOpen ?
                        <Modal closeModal={this.closeModal} addClasses="browser-selector__modal" focusId="visualize-limit-close">
                            <ModalHeader title="Open visualization browser" closeModal={this.closeModal} />
                            <ModalBody>
                                {disabledTitle ?
                                    <div>{disabledTitle}</div>
                                :
                                    <div className="browser-selector">
                                        <div className="browser-selector__inner">
                                            <div className="browser-selector__title">
                                                <div className="browser-selector__assembly-title">
                                                    Assembly
                                                </div>
                                                <div className="browser-selector__browsers-title">
                                                    Visualize with browser…
                                                </div>
                                            </div>
                                            <hr />
                                            {relevantAssemblies.map((assembly) => {
                                                const assemblyBrowsers = visualizeCfg[assembly];
                                                const browserList = _(Object.keys(assemblyBrowsers)).sortBy((browser) => _(globals.browserPriority).indexOf(browser));

                                                return (
                                                    <div key={assembly} className="browser-selector__assembly-option">
                                                        <div className="browser-selector__assembly">
                                                            {assembly}:
                                                        </div>
                                                        <div className="browser-selector__browsers">
                                                            {browserList.map((browser) => (
                                                                <div key={browser} className="browser-selector__browser">
                                                                    <a href={assemblyBrowsers[browser]} onClick={this.handleClick} rel="noopener noreferrer" target="_blank">
                                                                        {browser}
                                                                    </a>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                }
                            </ModalBody>
                            <ModalFooter closeModal={<button type="button" id="visualize-limit-close" className="btn btn-info" onClick={this.closeModal}>Close</button>} />
                        </Modal>
                    : null}
                </>
            );
        }
        return null;
    }
}

BrowserSelector.propTypes = {
    /** Search results that might include visualizations */
    results: PropTypes.object.isRequired,
    /** Title of accessible text for disabled title; also flag for disabling */
    disabledTitle: PropTypes.string,
    /** Filters not included in results.filters */
    additionalFilters: PropTypes.array,
};

BrowserSelector.defaultProps = {
    disabledTitle: '',
    additionalFilters: [],
};

BrowserSelector.contextTypes = {
    location_href: PropTypes.string,
};
