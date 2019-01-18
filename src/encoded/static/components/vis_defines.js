import _ from 'underscore';
import url from 'url';
import * as globals from './globals';


/**
 * Maximum number of hic files allowed to be selected at once.
 */
const MAX_HIC_FILES_SELECTED = 8;


/**
 * If you modify ASSEMBLY_DETAILS in vis_defines.py, this object might need corresponding
 * modifications.
 */
const ASSEMBLY_DETAILS = {
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
    'Quick View': ['bigWig', 'bigBed'],
    Ensembl: ['bigWig', 'bigBed'],
    hic: ['hic'],
};


/**
 * Open a browser visualization in a new tab. If called from a React component, that component must
 * be mounted.
 * @param {object} dataset Dataset object whose files we're visualizing
 * @param {string} browser Specifies browser to use: UCSC, Quick View, Ensembl, hic currently
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
    case 'Quick View': {
        const fileQueries = files.map(file => `accession=${globals.atIdToAccession(file['@id'])}`);
        href = `/search/?type=File&assembly=${assembly}&dataset=${dataset['@id']}&${fileQueries.join('&')}#browser`;
        break;
    }
    case 'hic': {
        const parsedUrl = url.parse(datasetUrl);
        delete parsedUrl.path;
        delete parsedUrl.search;
        delete parsedUrl.query;
        const fileQueries = files.map((file) => {
            parsedUrl.pathname = file.href;
            const name = file.biological_replicates && file.biological_replicates.length > 0 ? `Replicate ${file.biological_replicates.join(',')}` : '';
            return globals.encodedURIComponent(`{hicUrl=${url.format(parsedUrl)}${name}}`, { encodeEquals: true });
        });
        href = `http://aidenlab.org/juicebox/?juicebox=${fileQueries.join(',')}`;
        break;
    }
    case 'Ensembl': {
        if (ASSEMBLY_DETAILS[assembly].ensembl_host) {
            href = `http://${ASSEMBLY_DETAILS[assembly].ensembl_host}/Trackhub?url=${datasetUrl};species=${ASSEMBLY_DETAILS[assembly].species.replace(/ /g, '_')}`;
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
    let qualifiedFiles = files.filter(file => qualifiedFileTypes.indexOf(file.file_type) !== -1 && file.status === 'released');

    // For the hic browser, sort to prioritize "mapping quality thresholded chromatin interactions"
    // output_types.
    if (browser === 'hic') {
        qualifiedFiles = qualifiedFiles.sort(file => (file.output_type === 'mapping quality thresholded chromatin interactions' ? -1 : 0));
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
    case 'Quick View':
        selectable = browserFileTypes[browser].indexOf(file.file_type) !== -1;
        break;
    case 'hic':
        selectable = (browserFileTypes[browser].indexOf(file.file_type) !== -1) && (selectedFiles.length < MAX_HIC_FILES_SELECTED);
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
    'Quick View',
    'hic',
    'Ensembl',
];


/**
 * Given an array of browsers, sort them according to the order in the `browserOrder` global above.
 * @param {array} browsers Array of browsers to sort
 * @return {array} Same contents as `browsers` but sorted according to `browserOrder`
 */
export const visSortBrowsers = browsers => (
    _.sortBy(browsers, browser => browserOrder.indexOf(browser))
);
