import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import getNumberWithOrdinal from '../libs/ordinal_suffix';
import * as encoding from '../libs/query_encoding';
import { svgIcon } from '../libs/svg-icons';
import { CartToggle, cartGetAllowedTypes } from './cart';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import { BrowserFeat } from './browserfeat';
import Tooltip from '../libs/ui/tooltip';

// Display information on page as JSON formatted data
export class DisplayAsJson extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.onClick = this.onClick.bind(this);
    }

    onClick() {
        const urlComponents = url.parse(this.context.location_href);
        if (urlComponents.query !== null) {
            window.location.href += '&format=json';
        } else {
            window.location.href += '?format=json';
        }
    }

    render() {
        return (
            <button type="button" className="btn btn-info btn-sm" title="Convert page to JSON-formatted data" aria-label="Convert page to JSON-formatted data" onClick={this.onClick}>&#123; ; &#125;</button>
        );
    }
}

DisplayAsJson.contextTypes = {
    location_href: PropTypes.string,
};

export function shadeOverflowOnScroll(e) {
    // shading element that indicates there is further to scroll down
    const bottomShading = e.target.parentNode.getElementsByClassName('shading')[0];
    if (bottomShading) {
        if (e.target.scrollHeight - e.target.scrollTop === e.target.clientHeight) {
            bottomShading.classList.add('hide-shading');
        } else {
            bottomShading.classList.remove('hide-shading');
        }
    }

    // shading element that indicates there is further to scroll up
    const topShading = e.target.parentNode.getElementsByClassName('top-shading')[0];
    if (topShading) {
        if (e.target.scrollTop > 0) {
            topShading.classList.remove('hide-shading');
        } else {
            topShading.classList.add('hide-shading');
        }
    }
}


// Display a summary sentence for a single treatment.
export function singleTreatment(treatment) {
    let treatmentText = '';

    if (treatment.amount) {
        treatmentText += `${treatment.amount}${treatment.amount_units ? ` ${treatment.amount_units}` : ''} `;
    }
    treatmentText += `${treatment.treatment_term_name}${treatment.treatment_term_id ? ` (${treatment.treatment_term_id})` : ''} `;
    if (treatment.duration) {
        let units = '';
        if (treatment.duration_units) {
            units = `${treatment.duration_units}${treatment.duration !== 1 ? 's' : ''}`;
        }
        treatmentText += `for ${treatment.duration}${units ? ` ${units}` : ''}`;
    }
    return treatmentText;
}


// Display a treatment definition list.
export function treatmentDisplay(treatment) {
    const treatmentText = singleTreatment(treatment);
    return (
        <dl key={treatment.uuid} className="key-value">
            <div data-test="treatment">
                <dt>Treatment</dt>
                <dd>{treatmentText}</dd>
            </div>

            <div data-test="type">
                <dt>Type</dt>
                <dd>{treatment.treatment_type}</dd>
            </div>
        </dl>
    );
}


/**
 * Perform a request to the given URI and return the results in a promise.
 * @param {string} URI to request from the server
 * @return {promise} Contains request results
 */
export const requestUri = (queryUri) => (
    fetch(queryUri, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
        },
    }).then((response) => {
        // Convert the response to JSON.
        if (response.ok) {
            return response.json();
        }
        return Promise.resolve(null);
    }).then((responseJson) => responseJson || {})
);


/**
 * Do a search of an arbitrary query string passed in the `query` parameter, and return a promise.
 * If, for whatever reason, no results could be had, an empty object gets returned from the
 * promise.
 * @param {string} query Query string, not including ?
 * @return {promise} Contains search results object
 */
export function requestSearch(query) {
    return requestUri(`/search/?${query}`);
}


const SINGLE_QUERY_SIZE_PADDING = 10;
const MAX_DOMAIN_LENGTH = 64 + 19 + 8; // Max AWS domain name + .demo.encodedcc.org + https://
const MAX_URL_LENGTH = 4000 - MAX_DOMAIN_LENGTH;

/**
 * Do a search of the specific objects whose @ids are listed in the `identifiers` parameter. Because
 * we have to specify the @id of each object in the URL of the GET request, the URL can get quite
 * long, so if the number of `identifiers` goes beyond the CHUNK_SIZE constant, we break the
 * searches into chunks, and we estimate the maximum number of @ids in each chunk to reasonably
 * fit within a URL. We then send out all the search GET requests at once, and combine the
 * requested objects into one array returned as a promise.
 *
 * @param {array} identifiers object identifiers, usually @ids
 * @param {string} uri Base URI specifying type and statuses of the objects we want to get
 * @param {string} queryProp Object property to search; '@id' by default
 *
 * @return {promise} Array of objects requested from the server
 */
export const requestObjects = async (identifiers, uri, queryProp = '@id') => {
    if (identifiers.length > 0) {
        // Calculate a roughly reasonable chunk size based on an estimate of how many query-string
        // elements will fit within the maximum URL size. Assume the first identifier has a length
        // typical for all the identifiers.
        const singleQuerySize = queryProp.length + identifiers[0].length + SINGLE_QUERY_SIZE_PADDING;
        const chunkLength = Math.trunc((MAX_URL_LENGTH - uri.length) / singleQuerySize);

        // Break `identifiers` into an array of arrays of <= the calculated chunk size.
        const objectChunks = [];
        for (let start = 0, chunkIndex = 0; start < identifiers.length; start += chunkLength, chunkIndex += 1) {
            objectChunks[chunkIndex] = identifiers.slice(start, start + chunkLength);
        }

        // Going to send out all search chunk GET requests at once, and then wait for all of them to
        // complete.
        const chunks = await Promise.all(objectChunks.map(async (objectChunk) => {
            // Build URL containing search for specific objects for each chunk of objects.
            const objectUrl = uri.concat(objectChunk.reduce((combined, current) => `${combined}&${queryProp}=${encoding.encodedURIComponent(current)}`, ''));
            const response = await fetch(objectUrl, {
                method: 'GET',
                headers: { Accept: 'application/json' },
            });

            // Convert each response response to JSON.
            if (response.ok) {
                return response.json();
            }
            return Promise.resolve(null);
        }));

        // All search chunks have resolved or errored. We get an array of search results in
        // `chunks` -- one per chunk. Now collect their objects from their @graphs into one array of
        // objects and return them as the promise result.
        if (chunks && chunks.length > 0) {
            return chunks.reduce((objects, chunk) => (chunk && chunk['@graph'].length > 0 ? objects.concat(chunk['@graph']) : objects), []);
        }
    }
    return Promise.resolve([]);
};


// Do a search of the specific files whose @ids are listed in the `fileIds` parameter.
//
// You can also supply an array of objects in the filteringFiles parameter. Any file @ids in
// `atIds` that matches an object['@id'] in `filteringFiles` doesn't get included in the GET
// request.
//
// Note: this function calls requestObjects which calls `fetch`, so you can't call this function
// from code that runs on the server or it'll complain that `fetch` isn't defined. If called from a
// React component, make sure you only call it when you know the component is mounted, like from
// the componentDidMount method.
//
// fileIds: array of file @ids.
// filteringFiles: Array of files to filter out of the array of file @ids in the fileIds parameter.
export function requestFiles(fileIds, filteringFiles) {
    return requestObjects(fileIds, '/search/?type=File&limit=all&status!=deleted&status!=revoked&status!=replaced', filteringFiles);
}


// Given a dataset (for now, only ReferenceEpigenome), return the donor diversity of that dataset.
export function donorDiversity(dataset) {
    let diversity = 'none';

    if (dataset.related_datasets && dataset.related_datasets.length > 0) {
        // Get all non-deleted related experiments; empty array if none.
        const experiments = dataset.related_datasets.filter((experiment) => experiment.status !== 'deleted');

        // From list list of non-deleted experiments, get all non-deleted replicates into one
        // array.
        if (experiments.length > 0) {
            // Make an array of replicate arrays, one replicate array per experiment. Only include
            // non-deleted replicates.
            const replicatesByExperiment = experiments.map((experiment) => (
                (experiment.replicates && experiment.replicates.length > 0) ?
                    experiment.replicates.filter((replicate) => replicate.status !== 'deleted')
                : []
            ));

            // Merge all replicate arrays into one non-deleted replicate array.
            const replicates = replicatesByExperiment.reduce((replicateCollection, replicatesForExperiment) => replicateCollection.concat(replicatesForExperiment), []);

            // Look at the donors in each replicate's biosample. If we see at least two different
            // donors, we know we have a composite. If only one unique donor after examining all
            // donors, we have a single. "None" if no donors found in all replicates.
            if (replicates.length > 0) {
                const donorAtIdCollection = [];
                replicates.every((replicate) => {
                    if (replicate.library && replicate.library.status !== 'deleted' &&
                            replicate.library.biosample && replicate.library.biosample.status !== 'deleted' &&
                            replicate.library.biosample.donor && replicate.library.biosample.donor.status !== 'deleted') {
                        const donorAccession = replicate.library.biosample.donor.accession;

                        // If we haven't yet seen this donor @id, add it to our collection
                        if (donorAtIdCollection.indexOf(donorAccession) === -1) {
                            donorAtIdCollection.push(donorAccession);
                        }

                        // If we have two, we know have a composite, and we can exit the loop by
                        // returning false, which makes the replicates.every function end.
                        return donorAtIdCollection.length !== 2;
                    }

                    // No donor to examine in this replicate. Keep the `every` loop going.
                    return true;
                });

                // Now determine the donor diversity.
                if (donorAtIdCollection.length > 1) {
                    diversity = 'composite';
                } else if (donorAtIdCollection.length === 1) {
                    diversity = 'single';
                } // Else keep its original value of 'none'.
            }
        }
    }
    return diversity;
}

/**
 * Return control type if needed or empty string other wise.
 *
 * @param {string} type Type
 * @returns Control Type part of URL
 */
export const controlTypeParameter = (type) => (['Experiment', 'FunctionalCharacterizationExperiment'].includes(type) ? '&control_type!=*' : '');


// Render the Download icon while allowing the hovering tooltip.
class DownloadIcon extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.onMouseEnter = this.onMouseEnter.bind(this);
        this.onMouseLeave = this.onMouseLeave.bind(this);
    }

    onMouseEnter() {
        this.props.hoverDL(true);
    }

    onMouseLeave() {
        this.props.hoverDL(false);
    }

    render() {
        const { file } = this.props;

        return (
            <i className="icon icon-download" style={!file.restricted ? {} : { opacity: '0.3' }} onMouseEnter={file.restricted ? this.onMouseEnter : null} onMouseLeave={file.restricted ? this.onMouseLeave : null}>
                <span className="sr-only">Download</span>
            </i>
        );
    }
}

DownloadIcon.propTypes = {
    hoverDL: PropTypes.func.isRequired, // Function to call when hovering or stop hovering over the icon
    file: PropTypes.object.isRequired, // File associated with this download button
};


// Render an accession as a button if clicking it sets a graph node, or just as text if not.
const FileAccessionButton = (props) => {
    const { file } = props;
    return <a href={file['@id']} title={`Go to page for ${file.title}`}>{file.title}</a>;
};

FileAccessionButton.propTypes = {
    file: PropTypes.object.isRequired, // File whose button is being rendered
};


// Display a button to open the file information modal.
class FileInfoButton extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.onClick = this.onClick.bind(this);
    }

    onClick() {
        this.props.clickHandler(this.props.file);
    }

    render() {
        return (
            <button type="button" className="file-table-btn" onClick={this.onClick}>
                <i className="icon icon-info-circle">
                    <span className="sr-only">Open file information</span>
                </i>
            </button>
        );
    }
}

FileInfoButton.propTypes = {
    file: PropTypes.object.isRequired, // File whose information is to be displayed
    clickHandler: PropTypes.func.isRequired, // Function to call when the info button is clicked
};


// Render a download button for a file that reacts to login state and admin status to render a
// tooltip about the restriction based on those things.
export const RestrictedDownloadButton = (props) => {
    const { file } = props;
    const buttonEnabled = !(file.restricted || file.no_file_available);

    // Default icon
    const icon = (
        <i className="icon icon-download" style={!file.restricted ? {} : { opacity: '0.3' }}>
            <span className="sr-only">Download</span>
        </i>
    );

    // If the user provided us with a component for downloading files, add the download
    // properties to the component before rendering.
    const downloadComponent = props.downloadComponent ? React.cloneElement(props.downloadComponent, {
        file,
        href: file.href,
        download: file.href.substr(file.href.lastIndexOf('/') + 1),
        hoverDL: null,
        buttonEnabled,
    }) : icon;

    return (
        <Tooltip
            trigger={
                <div>
                    {buttonEnabled ?
                        <span>
                            <a href={file.href} download={file.href.substr(file.href.lastIndexOf('/') + 1)} data-bypass="true">
                                {downloadComponent}
                            </a>
                        </span>
                    :
                        <span>
                            {downloadComponent}
                        </span>
                    }
                </div>
            }
            tooltipId={file['@id']}
            css="dl-tooltip-trigger"
        >
            {file.restricted ?
                <div>
                    If you are a collaborator or owner of this file,<br />
                    please contact <a href="mailto:encode-help@lists.stanford.edu">encode-help@lists.stanford.edu</a><br />
                    to receive a copy of this file
                </div>
            : null}
        </Tooltip>
    );
};

RestrictedDownloadButton.propTypes = {
    file: PropTypes.object.isRequired, // File containing `href` to use as download link
    downloadComponent: PropTypes.object, // Optional component to render the download button, instead of default
};

RestrictedDownloadButton.defaultProps = {
    downloadComponent: null,
};


export const DownloadableAccession = (props) => {
    const { file, clickHandler, loggedIn } = props;
    return (
        <span className="file-table-accession">
            <FileAccessionButton file={file} />
            {clickHandler ? <FileInfoButton file={file} clickHandler={clickHandler} /> : null}
            <RestrictedDownloadButton file={file} loggedIn={loggedIn} />
        </span>
    );
};

DownloadableAccession.propTypes = {
    file: PropTypes.object.isRequired, // File whose accession to render
    clickHandler: PropTypes.func, // Function to call when button is clicked
    loggedIn: PropTypes.bool, // True if current user is logged in
};

DownloadableAccession.defaultProps = {
    clickHandler: null,
    loggedIn: false,
};


// Return `true` if the given dataset is viewable by people not logged in, or people logged in
// but not as admin.
export function publicDataset(dataset) {
    return dataset.status === 'released' || dataset.status === 'archived' || dataset.status === 'revoked';
}


// You can use this function to render a panel view for a context object with a couple options:
//   1. Pass an ENCODE context object (e.g. Biosample or Experiment) directly in props. PanelLookup
//      returns a React component that you can render directly.
//
//   2. Pass an object of the form:
//      {
//          context: context object to render
//          ...any other props you want to pass to the panel-rendering component
//      }
//
// Note: this function really doesn't do much of value, but it does do something and it's been
// around since the beginning of encoded, so it stays for now.

export function PanelLookup(properties) {
    let localProps;
    if (properties['@id']) {
        // `properties` is an ENCODE context object, so normalize it by making `props` an object
        // with the given context as an object property.
        localProps = { context: properties };
    } else {
        localProps = properties;
    }

    // `props` is an object with at least { context: ENCODE context object }.
    const PanelView = globals.panelViews.lookup(localProps.context);
    return <PanelView key={localProps.context.uuid} {...localProps} />;
}


// Display the alternate accessions, normally below the header line in objects.
export const AlternateAccession = (props) => {
    const { altAcc } = props;

    if (altAcc && altAcc.length > 0) {
        return (
            <h4 className="replacement-accessions__alternate">
                {altAcc.length === 1 ?
                    <span>Alternate accession: {altAcc[0]}</span>
                :
                    <span>Alternate accessions: {altAcc.join(', ')}</span>
                }
            </h4>
        );
    }

    // No alternate accessions to display.
    return null;
};

AlternateAccession.propTypes = {
    altAcc: PropTypes.array, // Array of alternate accession strings
};

AlternateAccession.defaultProps = {
    altAcc: null,
};


/**
 * Display image with fallback for non-existent image links
 */
export class ImageWithFallback extends React.Component {
    constructor() {
        super();

        // Initialize image src and alt tags to be empty
        // These should not be set to props values prior to the component mounting or the onError function may not execute for broken image urls on certain browsers (Chrome in particular)
        this.state = {
            imageUrl: '',
            imageAlt: '',
        };
        this.onError = this.onError.bind(this);
    }

    // Only once the component has mounted, update image src and alt tag
    // This ensures that the component mounts and that the onError function will execute for broken image urls
    componentDidMount() {
        this.setState({
            imageUrl: this.props.imageUrl,
            imageAlt: this.props.imageAlt,
        });
    }

    onError() {
        // IE11 has an issue where it frequently throws a "Permission denied" exception, when the image
        // exist. This workaround makes IE11 show either the image if it exist or the browser's
        // inbuilt no-image display
        if (BrowserFeat.getBrowserCaps('uaTrident')) {
            return;
        }

        const imageUrl = '/static/img/brokenImage.png';
        const imageAlt = 'Not found';

        this.setState({
            imageUrl,
            imageAlt,
        });
    }

    render() {
        return (
            <img
                onError={this.onError}
                src={this.state.imageUrl}
                alt={this.state.imageAlt}
            />
        );
    }
}

ImageWithFallback.propTypes = {
    imageUrl: PropTypes.string.isRequired,
    imageAlt: PropTypes.string.isRequired,
};


/**
 * Maps an internal tag to the corresponding image file name. Exported for Jest testing.
 */
export const internalTagsMap = {
    ccre_inputv1: {
        badgeFilename: 'tag-ccre_inputv1.svg',
    },
    ccre_inputv2: {
        badgeFilename: 'tag-ccre_inputv2.svg',
    },
    cre_inputv10: {
        badgeFilename: 'tag-cre_inputv10.svg',
    },
    cre_inputv11: {
        badgeFilename: 'tag-cre_inputv11.svg',
    },
    dbGaP: {
        badgeFilename: 'tag-dbGaP.png',
    },
    DREAM: {
        badgeFilename: 'tag-DREAM.png',
    },
    ENCORE: {
        badgeFilename: 'tag-ENCORE.svg',
        collectionPath: '/encore-matrix/?type=Experiment&status=released&internal_tags=ENCORE',
    },
    ENCYCLOPEDIAv3: {
        badgeFilename: 'tag-ENCYCLOPEDIAv3.svg',
    },
    ENCYCLOPEDIAv4: {
        badgeFilename: 'tag-ENCYCLOPEDIAv4.svg',
    },
    ENCYCLOPEDIAv5: {
        badgeFilename: 'tag-ENCYCLOPEDIAv5.svg',
    },
    ENCYCLOPEDIAv6: {
        badgeFilename: 'tag-ENCYCLOPEDIAv6.svg',
    },
    ENTEx: {
        badgeFilename: 'tag-ENTEx.png',
        collectionPath: '/entex-matrix/?type=Experiment&status=released&internal_tags=ENTEx',
    },
    LRGASP: {
        badgeFilename: 'tag-LRGASP.png',
    },
    MouseDevSeries: {
        badgeFilename: 'tag-MouseDevSeries.svg',
        collectionPath: '/mouse-development-matrix/?type=Experiment&status=released&related_series.@type=OrganismDevelopmentSeries&replicates.library.biosample.organism.scientific_name=Mus+musculus',
    },
    PGP: {
        badgeFilename: 'tag-PGP.png',
    },
    RegulomeDB_1_0: {
        badgeFilename: 'tag-RegulomeDB_1_0.svg',
    },
    RegulomeDB_2_0: {
        badgeFilename: 'tag-RegulomeDB_2_0.svg',
    },
    RegulomeDB_2_1: {
        badgeFilename: 'tag-RegulomeDB_2_1.svg',
    },
    RushAD: {
        badgeFilename: 'tag-RushAD.svg',
    },
    SESCC: {
        badgeFilename: 'tag-SESCC.svg',
        collectionPath: '/sescc-stem-cell-matrix/?type=Experiment&internal_tags=SESCC',
    },
    YaleImmuneCells: {
        badgeFilename: 'tag-YaleImmuneCells.svg',
    },
};

/**
 * Maps a badge type to the corresponding image filename.
 */
const badgeMap = {
    Experiment: 'badge-Experiment.svg',
    Annotation: 'badge-Annotation.svg',
    'ReferenceEpigenome-human': 'badge-ReferenceEpigenome-human.svg',
    'ReferenceEpigenome-mouse': 'badge-ReferenceEpigenome-mouse.svg',
    MouseDevelopment: 'badge-MouseDevelopment.svg',
    ChIPseq: 'badge-ChIPseq.svg',
};


/**
 * Display internal tag badges or a given badge ID from search results. Badge IDs are used for
 * matrix displays that don't necessarily have internal_tags defined in the query string.
 */
export const MatrixBadges = ({ context, type }) => {
    // Collect filters that are internal_tags.
    const internalTags = _.uniq(context.filters.filter((filter) => (
        filter.field === 'internal_tags' && filter.term !== '*'
    )).map((filter) => filter.term));
    if (internalTags.length > 0) {
        return internalTags.map((tag) => {
            const filename = internalTagsMap[tag].badgeFilename;
            if (filename) {
                return <img className="badge-image" src={`/static/img/${filename}`} alt={`${tag} logo`} key={tag} />;
            }
            return null;
        });
    }

    // Use a badge for the specific given type, if provided, when no internal_tags used.
    if (type) {
        const filename = badgeMap[type];
        if (filename) {
            return <img className="badge-image" src={`/static/img/${filename}`} alt={`${type} badge`} />;
        }
    }
    return null;
};

MatrixBadges.propTypes = {
    /** encode search-results object being displayed */
    context: PropTypes.object.isRequired,
    /** Specific type of badge to display; used if available if internal_tags does not exist */
    type: PropTypes.string,
};

MatrixBadges.defaultProps = {
    type: '',
};


/**
 * Display a list of internal_tags for an object as badges that link to a corresponding search. The
 * object in `context` must have at least one `internal_tags` value or the results are
 * unpredictable.
 */
export const InternalTags = ({ internalTags, objectType, css }) => {
    const tagBadges = internalTags.map((tag) => {
        const filename = internalTagsMap[tag];
        if (filename) {
            if (filename.collectionPath) {
                const tagSearchUrl = filename.collectionPath;
                return <a href={tagSearchUrl} key={tag}><img src={`/static/img/${filename.badgeFilename}`} alt={`Visit collection page for ${tag}`} /></a>;
            }
            const tagSearchUrl = `/search/?type=${objectType}&internal_tags=${encoding.encodedURIComponentOLD(tag)}&status=released`;
            return <a href={tagSearchUrl} key={tag}><img src={`/static/img/${filename.badgeFilename}`} alt={`Search for all ${objectType} with internal tag ${tag}`} /></a>;
        }
        return null;
    });
    return <span className={css}>{tagBadges}</span>;
};

InternalTags.propTypes = {
    /** Array of internal tags to display */
    internalTags: PropTypes.array.isRequired,
    /** Object @type internal_tags belongs to */
    objectType: PropTypes.string.isRequired,
    /** Optional CSS class to assign to <span> surrounding all the badges */
    css: PropTypes.string,
};

InternalTags.defaultProps = {
    css: '',
};


/**
 * Given a search results object, extract the type of object that was requested in the query
 * string that generated the search results object and map it to a presentable human-generated
 * object type name from that kind of object's schema. Optionally wrap the name in a given wrapper
 * component. Nothing gets rendered if the search result's query string doesn't specify a
 * "type=anything" or has more than one. The wrapper function must take the form of:
 * "title => <Wrapper>{title}</Wrapper>". Idea for the component wrapping technique from:
 * https://gist.github.com/kitze/23d82bb9eb0baabfd03a6a720b1d637f
 */
export const DocTypeTitle = ({ searchResults, wrapper }, reactContext) => {
    // Determine the search page doc_type title to display at the top of the facet list.
    let facetTitle = '';
    const docTypes = searchResults.filters.length > 0 ? searchResults.filters.filter((searchFilter) => searchFilter.field === 'type') : [];
    if (docTypes.length === 1) {
        facetTitle = reactContext.profilesTitles[docTypes[0].term];
    }

    // If one object type was requested, render it *into* the given wrapper component if one was
    // given.
    if (facetTitle) {
        const facetTitleComponent = <span>{facetTitle}</span>;
        return wrapper ? wrapper(facetTitleComponent) : facetTitleComponent;
    }
    return null;
};

DocTypeTitle.propTypes = {
    searchResults: PropTypes.object.isRequired,
    wrapper: PropTypes.func,
};

DocTypeTitle.defaultProps = {
    wrapper: null,
};

DocTypeTitle.contextTypes = {
    profilesTitles: PropTypes.object,
};


/**
 * Display a block of accessory controls on object-display pages, e.g. the audit indicator button.
 */
export const ItemAccessories = ({ item, audit }, reactContext) => (
    <div className="item-accessories">
        <div className="item-accessories--left">
            {audit ?
                audit.auditIndicators(item.audit, audit.auditId, { session: reactContext.session, sessionProperties: reactContext.session_properties, except: audit.except })
            : null}
        </div>
        <div className="item-accessories--right">
            <DisplayAsJson />
        </div>
    </div>
);

ItemAccessories.propTypes = {
    /** Object being displayed that needs these accessories */
    item: PropTypes.object.isRequired,
    /** Audit information */
    audit: PropTypes.shape({
        auditIndicators: PropTypes.func, // Function to display audit indicators
        auditId: PropTypes.string, // Audit HTML ID to use for a11y
        except: PropTypes.string, // Don't link any references to this @id
    }),
};

ItemAccessories.defaultProps = {
    audit: null,
};

ItemAccessories.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
};


/**
 * Display the top section containing the breadcrumb links on summary pages.
 */
export const TopAccessories = ({ context, crumbs }) => {
    const type = context['@type'][0];
    const isItemAllowedInCart = cartGetAllowedTypes().includes(type);

    return (
        <div className="top-accessories">
            <Breadcrumbs root={`/search/?type=${type}${controlTypeParameter(type)}`} crumbs={crumbs} crumbsReleased={context.status === 'released'} />
            {isItemAllowedInCart ?
                <CartToggle element={context} displayName />
            : null}
        </div>
    );
};

TopAccessories.propTypes = {
    /** Summary page currently displayed */
    context: PropTypes.object.isRequired,
    /** Object with breadcrumb contents */
    crumbs: PropTypes.arrayOf(PropTypes.object).isRequired,
};


// Convert assembly and annotation to a single value
// Values computed such that assembly and annotations that are the most recent have the highest value
// The correct sorting is as follows:
// Genome mm9 or mm10
//                 "ENSEMBL V65",
//                 "M2",
//                 "M3",
//                 "M4",
//                 "M7",
//                 "M14",
//                 "M21",
// Genome hg19
//                 "V3c",
//                 "V7",
//                 "V10",
//                 "V19",
//                 "miRBase V21",
//                 "V22",
// Genome GRCh38
//                 "V24",
//                 "V29",
//                 "V30"
// Genome ce10 or ce11
//                 "WS235",
//                 "WS245"
// outlier:
//                 "None"
export function computeAssemblyAnnotationValue(assembly, annotation) {
    // There are three levels of sorting
    // First level of sorting: most recent assemblies are ordered first (represented by numerical component of assembly)
    // Second level of sorting: assemblies without '-minimal' are sorted before assemblies with '-minimal' at the end (represented by tenths place value which is 5 if there is no '-minimal')
    // Third level of sorting: Annotations within an assembly are ordered with most recent first, with more recent annotations having a higher annotation number (with the exception of "ENSEMBL V65") (represented by the annotation number divided by 10,000, or, the three decimal places after the tenths place)
    let assemblyNumber = +assembly.match(/[0-9]+/g)[0];
    if (assembly.indexOf('minimal') === -1) {
        // If there is no '-minimal', add 0.5 which will order this assembly ahead of any assembly with '-minimal' and the same numerical component
        assemblyNumber += 0.5;
    }
    if (annotation) {
        const annotationNumber = +annotation.match(/[0-9]+/g)[0];
        let annotationDecimal = 0;
        // All of the annotations are in order numerically except for "ENSEMBL V65" which should be ordered behind "M2"
        // We divide by 10000 because the highest annotation number (for now) is 245
        if (+annotationNumber === 65) {
            annotationDecimal = (+annotationNumber / 1000000);
        } else {
            annotationDecimal = (+annotationNumber / 10000);
        }
        assemblyNumber += annotationDecimal;
        return assemblyNumber;
    }
    return assemblyNumber;
}


/**
 * Determine whether the given file is visualizable or not. Needs to be kept in sync with
 * is_file_visualizable in batch_download.py.
 * @param {object} file File object to test for visualizability
 *
 * @return {bool} True if file is visualizable
 */
export const isFileVisualizable = (file) => {
    if (!file || !file.file_format) {
        return false;
    }

    return (file.file_format === 'bigWig' || file.file_format === 'bigBed')
        && (file.file_format_type !== 'bedMethyl')
        && (file.file_format_type !== 'bedLogR')
        && (file.file_format_type !== 'pepMap')
        && (file.file_format_type !== 'modPepMap')
        && (['methylation state at CHG',
            'methylation state at CHH',
            'methylation state at CpG',
            'smoothed methylation state at CpG',
        ].indexOf(file.output_type) === -1)
        && ['released', 'in progress', 'archived'].indexOf(file.status) > -1;
};


// Not all files can be visualized on the Valis genome browser
// Some of these files should be visualizable later, after updates to browser
export function filterForVisualizableFiles(fileList) {
    if (!fileList || fileList.length === 0) {
        return [];
    }

    return fileList.filter((file) => isFileVisualizable(file));
}


/**
 * Filter the given files to only include those with the `preferred_default` or `pseudo_default`
 * flag set.
 * @param {array} fileList Files to filter
 *
 * @return {array} Members of `fileList` that have preferred_default flag set.
 */
export const filterForDefaultFiles = (fileList) => (
    fileList.filter((file) => file.preferred_default || file.pseudo_default)
);


/**
 * Filter the given files to only include those that appear in the given datasets.
 * @param {array} fileList Files to filter
 * @param {array} datasets Datasets to check against
 *
 * @return {array} Members of `fileList` that the given datasets include
 */
export const filterForDatasetFiles = (fileList, datasets) => {
    const datasetFilePaths = datasets
        .reduce((files, dataset) => (dataset.files ? files.concat(dataset.files) : files), [])
        .map((file) => file['@id']);
    return fileList.filter((file) => datasetFilePaths.includes(file['@id']));
};


/**
 * Filter an array of files to ones included in the released analyses in `compiledAnalyses`. If
 * none of the given compiled analyses have the "released" status, filter to the unreleased
 * analyses files.
 * @param {array} fileList Files to filter
 * @param {array} compiledAnalyses Compiled analysis objects
 * @returns {array} Filtered `fileList`
 */
export const filterForReleasedAnalyses = (fileList, compiledAnalyses) => {
    if (fileList.length > 0 && compiledAnalyses.length > 0) {
        const releasedAnalyses = compiledAnalyses.filter((analysis) => analysis.status === 'released');
        const consideredAnalyses = releasedAnalyses.length > 0 ? releasedAnalyses : compiledAnalyses;
        const consideredAnalysisFiles = consideredAnalyses.reduce((files, analysis) => files.concat(analysis.files), []);
        return fileList.filter((file) => consideredAnalysisFiles.includes(file['@id']));
    }
    return [];
};


/**
 * Displays an item count intended for the tops of table, normally reflecting a search result count.
 */
export const TableItemCount = ({ count }) => (
    <div className="table-item-count">{count}</div>
);

TableItemCount.propTypes = {
    count: PropTypes.string.isRequired,
};

/**
 * Call react useEffect just once
 *
 * @param {function} fn
 */
export const useMount = (fn) => React.useEffect(fn, []);


/**
 * Display a button that copies the given text when the user clicks the button.
 */
export const CopyButton = ({ label, copyText, css }) => {
    /** True if browser has clipboard API */
    const [hasClipboard, setHasClipboard] = React.useState(false);
    /** True if user has clicked Copy */
    const [hasCopied, setHasCopied] = React.useState(false);

    /**
     * Called when the user clicks the Copy button.
     */
    const handleClick = async () => {
        // Copy given text to clipboard.
        await navigator.clipboard.writeText(copyText);
        setHasCopied(true);
    };

    const handleTransitionEnd = () => {
        setHasCopied(false);
    };

    useMount(() => {
        // Display Copy button if browser has clipboard API.
        if (navigator.clipboard) {
            setHasClipboard(true);
        }
    });

    if (hasClipboard) {
        return (
            <button
                type="button"
                disabled={!copyText}
                className={`btn btn-copy-action${css ? ` ${css}` : ''}${hasCopied ? ' flash' : ''}`}
                onClick={handleClick}
                onTransitionEnd={handleTransitionEnd}
                aria-label={label}
            >
                {svgIcon('clipboard')}
            </button>
        );
    }

    // No clipboard API.
    return null;
};

CopyButton.propTypes = {
    /** A11Y label for the button */
    label: PropTypes.string.isRequired,
    /** Text to copy */
    copyText: PropTypes.string,
    /** CSS classes to add to the copy button */
    css: PropTypes.string,
};

CopyButton.defaultProps = {
    copyText: '',
    css: 'btn',
};


/**
 * Display a custom-styled, accessible checkbox. Loosely based on:
 * https://webdesign.tutsplus.com/tutorials/how-to-make-custom-accessible-checkboxes-and-radio-buttons--cms-32074
 */
export const Checkbox = ({ label, id, checked, css, clickHandler }) => (
    <div className={`checkbox${css ? ` ${css}` : ''}`}>
        <input id={id} name={id} type="checkbox" checked={checked} onChange={clickHandler} />
        <label htmlFor={id}>
            {label}
            {svgIcon('checkbox')}
        </label>
    </div>
);

Checkbox.propTypes = {
    /** Label for the checkbox */
    label: PropTypes.string.isRequired,
    /** HTML ID for the checkbox <input> */
    id: PropTypes.string.isRequired,
    /** True if checkbox is checked */
    checked: PropTypes.bool.isRequired,
    /** CSS to apply to checkbox wrapper */
    css: PropTypes.string,
    /** Called when the user clicks the checkbox */
    clickHandler: PropTypes.func.isRequired,
};

Checkbox.defaultProps = {
    css: '',
};


/**
 * Examines the `examined_loci` property, if any, of the given dataset and formats it into
 * displayable text.
 * @param {object} experiment Dataset containing examined_loci to display
 * @param {boolean} includeMethod True to include expression method following the expression data
 * @returns {string} Formatted examined_loci display
 */
export function computeExaminedLoci(experiment, includeMethod) {
    const examinedLoci = [];
    if (experiment.examined_loci && experiment.examined_loci.length > 0) {
        experiment.examined_loci.forEach((locus) => {
            let locusData;
            if (locus.expression_percentile || locus.expression_percentile === 0) {
                locusData = `${locus.gene.symbol} (${getNumberWithOrdinal(locus.expression_percentile)} percentile)`;
            } else if ((locus.expression_range_minimum && locus.expression_range_maximum) || (locus.expression_range_maximum === 0 || locus.expression_range_minimum === 0)) {
                locusData = `${locus.gene.symbol} (${locus.expression_range_minimum}-${locus.expression_range_maximum}%)`;
            } else {
                locusData = `${locus.gene.symbol}`;
            }
            examinedLoci.push(`${locusData}${includeMethod && locus.expression_measurement_method ? ` ${locus.expression_measurement_method}` : ''}`);
        });
    }
    return examinedLoci.join(', ');
}
